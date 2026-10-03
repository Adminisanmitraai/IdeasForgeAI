// Isolated candidate. Compile this file alone, not the superseded unbounded observer.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.Runtime;

[assembly: ExtensionApplication(typeof(ForgeWa.Bounded.CommandObserver))]

namespace ForgeWa.Bounded {
  // No AutoCAD calls and no disk access while accepting an event.
  internal sealed class CaptureRun {
    internal const int DurationMs = 10000;
    internal const int MaxEvents = 40;
    static readonly Regex Safe = new Regex(@"\A[A-Z][A-Z0-9_.-]{0,63}\z", RegexOptions.CultureInvariant);
    readonly object gate = new object();
    readonly Func<double> clock;
    readonly double started;
    readonly Action<CaptureRun> completed;
    readonly List<string> rows = new List<string>();
    readonly List<KeyValuePair<string, int>> stack = new List<KeyValuePair<string, int>>();
    int nextCommand, invalid, orphan;
    bool active = true;
    string reason, ended;
    double elapsed;
    internal readonly string RunId = "run_" + Guid.NewGuid().ToString("N");
    internal readonly string DrawingHint;
    internal readonly string StartedAt = DateTime.UtcNow.ToString("o");
    internal volatile bool Saved;
    internal volatile string SaveError;

    internal CaptureRun(string drawingHint, Func<double> monotonicMilliseconds, Action<CaptureRun> sink) {
      DrawingHint = drawingHint; clock = monotonicMilliseconds; started = clock(); completed = sink;
    }
    internal bool Active { get { lock (gate) { return active && clock() - started < DurationMs; } } }
    internal int Count { get { lock (gate) { return rows.Count; } } }
    internal int Pending { get { lock (gate) { return stack.Count; } } }
    internal string Reason { get { lock (gate) { return reason; } } }
    internal string[] Rows { get { lock (gate) { return rows.ToArray(); } } }
    internal bool SavingComplete { get { return Saved || SaveError != null; } }
    internal static string Normalize(string raw) {
      if (raw == null || raw.Length == 0 || raw.Length > 128) return null;
      // Whitespace/free text is rejected, not trimmed into a plausible command.
      var name = raw.ToUpperInvariant().TrimStart('_', '.', '\'');
      return Safe.IsMatch(name) ? name : null;
    }
    internal static string J(string s) {
      if (s == null) return "null";
      var b = new StringBuilder("\"");
      foreach (char c in s) {
        if (c == '\\' || c == '"') { b.Append('\\'); b.Append(c); }
        else if (c < 32) { b.Append("\\u"); b.Append(((int)c).ToString("x4")); }
        else b.Append(c);
      }
      return b.Append('"').ToString();
    }
    internal void Accept(string phase, string raw) {
      string stop = null;
      lock (gate) {
        if (!active) return;
        if (clock() - started >= DurationMs) stop = "time_limit";
        else {
          string name = Normalize(raw);
          if (name == null || (phase != "start" && phase != "end" && phase != "cancel" && phase != "fail")) { invalid++; return; }
          if (name.StartsWith("FORGEWA_", StringComparison.Ordinal)) return;
          int id = 0;
          if (phase == "start") {
            id = ++nextCommand;
            stack.Add(new KeyValuePair<string,int>(name, id));
          } else if (stack.Count == 0) { orphan++; return; }
          else if (stack[stack.Count - 1].Key != name) stop = "pairing_mismatch";
          else { id = stack[stack.Count - 1].Value; stack.RemoveAt(stack.Count - 1); }
          if (stop == null) {
            rows.Add("{\"session_id\":" + J(RunId) + ",\"sequence\":" + (rows.Count + 1) +
              ",\"command_id\":" + id + ",\"phase\":" + J(phase) + ",\"command_name\":" + J(name) +
              ",\"occurred_at\":" + J(DateTime.UtcNow.ToString("o")) + ",\"drawing_hint\":" + J(DrawingHint) + "}");
            if (rows.Count >= MaxEvents) stop = "event_limit";
          }
        }
      }
      if (stop != null) Stop(stop);
    }
    internal void Stop(string stopReason) {
      lock (gate) {
        if (!active) return;
        active = false; reason = stopReason; ended = DateTime.UtcNow.ToString("o");
        elapsed = Math.Max(0.0, clock() - started);
      }
      try { completed(this); }
      catch (System.Exception e) { SaveError = e.GetType().Name; }
    }
    internal string Summary() {
      lock (gate) {
        return "{\"schema\":\"forgewa.autocad-semantic-bounded.v1\",\"run_id\":" + J(RunId) +
          ",\"started_at\":" + J(StartedAt) + ",\"ended_at\":" + J(ended) +
          ",\"active\":" + (active && clock() - started < DurationMs ? "true" : "false") +
          ",\"stop_reason\":" + J(reason) + ",\"elapsed_ms\":" + elapsed.ToString("F3",CultureInfo.InvariantCulture) +
          ",\"event_count\":" + rows.Count + ",\"pending_commands\":" + stack.Count +
          ",\"lifecycle_complete\":" + (!active && stack.Count == 0 && reason != "pairing_mismatch" ? "true" : "false") +
          ",\"invalid_events\":" + invalid + ",\"orphan_events\":" + orphan +
          ",\"max_ms\":10000,\"max_events\":40,\"observe_only\":true,\"autonomous_actions\":false," +
          "\"argument_capture\":false,\"prompt_capture\":false,\"production_activation\":false}";
      }
    }
  }

  public sealed class CommandObserver : IExtensionApplication {
    static readonly object Gate = new object();
    internal static string Root;
    internal static CaptureRun Current;
    static Document bound;
    static CommandEventHandler start, end, cancel, fail;
    static Timer expiry;
    static bool initialized;

    public void Initialize() {
      if (initialized) return;
      Root = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                          "ForgeWa", "Teacher", "AutoCADCommandEventsBounded");
      Application.Idle += OnIdle;
      Application.DocumentManager.DocumentToBeDestroyed += OnDestroyed;
      initialized = true; // No command subscriptions, files, timer, or capture on load.
    }
    public void Terminate() {
      try {
        StopCurrent("plugin_unload"); Detach();
        Application.Idle -= OnIdle;
        Application.DocumentManager.DocumentToBeDestroyed -= OnDestroyed;
      } catch (System.Exception) { }
      initialized = false;
    }
    [CommandMethod("FORGEWA_SEM_START", CommandFlags.Session)]
    public static void StartObserver() {
      try {
        lock (Gate) {
          if (!initialized) return;
          if (Current != null && Current.Active) return; // Duplicate Start never extends budget.
          if (Current != null) {
            Current.Stop("time_limit");
            if (!Current.SavingComplete) return;
          }
          Detach();
          Document doc = Application.DocumentManager.MdiActiveDocument;
          if (doc == null) return;
          string hint = Path.GetFileName(doc.Name ?? "");
          var watch = Stopwatch.StartNew();
          var run = new CaptureRun(hint, () => watch.Elapsed.TotalMilliseconds, QueueSave);
          Current = run; bound = doc;
          start = (s,e) => Record(doc, run, "start", e);
          end = (s,e) => Record(doc, run, "end", e);
          cancel = (s,e) => Record(doc, run, "cancel", e);
          fail = (s,e) => Record(doc, run, "fail", e);
          doc.CommandWillStart += start; doc.CommandEnded += end;
          doc.CommandCancelled += cancel; doc.CommandFailed += fail;
          // Timer callback touches only this run. AutoCAD event unsubscription occurs on Idle.
          expiry = new Timer(_ => run.Stop("time_limit"), null,
                             Math.Max(0, CaptureRun.DurationMs - (int)watch.ElapsedMilliseconds), Timeout.Infinite);
        }
      } catch (System.Exception) { StopCurrent("start_error"); Detach(); }
    }
    [CommandMethod("FORGEWA_SEM_STOP", CommandFlags.Session)]
    public static void StopObserver() { StopCurrent("user_stop"); Detach(); }

    [CommandMethod("FORGEWA_SEM_STATUS", CommandFlags.Session)]
    public static void StatusObserver() {
      try {
        var run = Current;
        string status = run == null ? "{\"state\":\"IDLE\",\"active\":false}" : run.Summary();
        Directory.CreateDirectory(Root);
        File.WriteAllText(Path.Combine(Root, "observer_status.json"), status, new UTF8Encoding(false));
        // UI output only, in a user-issued status command, never in an event callback.
        var doc = Application.DocumentManager.MdiActiveDocument;
        if (doc != null) doc.Editor.WriteMessage("\nForgeWa semantic observer: " + (run == null ? "IDLE" : run.Active ? "ARMED (10s maximum)" : "STOPPED") + ".");
      } catch (System.Exception) { }
    }
    static void Record(Document doc, CaptureRun run, string phase, CommandEventArgs e) {
      try {
        if (!Object.ReferenceEquals(run, Current)) return;
        if (!run.Active) { run.Stop("time_limit"); return; }
        if (!Object.ReferenceEquals(doc, bound) || !Object.ReferenceEquals(doc, Application.DocumentManager.MdiActiveDocument)) {
          run.Stop("document_changed"); return;
        }
        run.Accept(phase, e.GlobalCommandName); // Never read prompt/input/arguments or drawing entities.
      } catch (System.Exception) { run.Stop("observer_error"); }
    }
    static void StopCurrent(string reason) {
      var run = Current;
      if (run != null) run.Stop(reason);
    }
    static void OnIdle(object sender, EventArgs e) {
      try { if (Current != null && !Current.Active) { Current.Stop("time_limit"); Detach(); } }
      catch (System.Exception) { StopCurrent("observer_error"); }
    }
    static void OnDestroyed(object sender, DocumentCollectionEventArgs e) {
      if (Object.ReferenceEquals(e.Document, bound)) { StopCurrent("document_closed"); Detach(); }
    }
    static void Detach() {
      lock (Gate) {
        if (expiry != null) { expiry.Dispose(); expiry = null; }
        if (bound != null) {
          try {
            bound.CommandWillStart -= start; bound.CommandEnded -= end;
            bound.CommandCancelled -= cancel; bound.CommandFailed -= fail;
          } catch (System.Exception) { }
        }
        bound = null; start = end = cancel = fail = null;
      }
    }
    static void QueueSave(CaptureRun run) {
      string outputRoot = Root; // Copy once; never consult AutoCAD from the worker.
      if (!ThreadPool.QueueUserWorkItem(_ => {
        try {
          string path = Path.Combine(outputRoot, run.RunId);
          if (Directory.Exists(path)) throw new IOException("run_directory_exists");
          Directory.CreateDirectory(path);
          File.WriteAllLines(Path.Combine(path, "commands.jsonl"), run.Rows, new UTF8Encoding(false));
          File.WriteAllText(Path.Combine(path, "summary.json"), run.Summary(), new UTF8Encoding(false));
          run.Saved = true;
        } catch (System.Exception e) { run.SaveError = e.GetType().Name; }
      })) run.SaveError = "QueueRejected";
    }
  }
}
