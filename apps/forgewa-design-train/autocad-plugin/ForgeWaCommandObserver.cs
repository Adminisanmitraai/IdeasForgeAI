using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.Runtime;

[assembly: ExtensionApplication(typeof(ForgeWa.CommandObserver))]

namespace ForgeWa {
  public sealed class CommandObserver : IExtensionApplication {
    static readonly Regex Safe = new Regex("^[A-Z][A-Z0-9_.-]{0,63}$", RegexOptions.CultureInvariant);
    static readonly Dictionary<Document, Handlers> Docs = new Dictionary<Document, Handlers>();
    static readonly object Gate = new object();
    static string Root;
    static bool Armed;

    sealed class Handlers {
      internal CommandEventHandler Start, End, Cancel, Fail;
    }

    public void Initialize() {
      Root = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                          "ForgeWa", "Teacher", "AutoCADCommandEvents");
      Application.DocumentManager.DocumentCreated += OnDocumentCreated;
      Application.DocumentManager.DocumentToBeDestroyed += OnDocumentDestroyed;
      foreach (Document doc in Application.DocumentManager) Attach(doc);
      // Loading the assembly never arms capture.
    }

    public void Terminate() {
      Armed = false;
      Application.DocumentManager.DocumentCreated -= OnDocumentCreated;
      Application.DocumentManager.DocumentToBeDestroyed -= OnDocumentDestroyed;
      foreach (var doc in new List<Document>(Docs.Keys)) Detach(doc);
    }

    // These commands control only this observer's subscription state; they do not edit a drawing.
    [CommandMethod("FORGEWA_OBSERVE_START", CommandFlags.Session)]
    public static void StartObserver() { Armed = true; AppendControl("observer_start"); }

    [CommandMethod("FORGEWA_OBSERVE_STOP", CommandFlags.Session)]
    public static void StopObserver() { AppendControl("observer_stop"); Armed = false; }

    static void OnDocumentCreated(object sender, DocumentCollectionEventArgs e) { Attach(e.Document); }
    static void OnDocumentDestroyed(object sender, DocumentCollectionEventArgs e) { Detach(e.Document); }

    static void Attach(Document doc) {
      if (doc == null || Docs.ContainsKey(doc)) return;
      var h = new Handlers();
      h.Start = (s,e) => Record(doc,"start",e.GlobalCommandName);
      h.End = (s,e) => Record(doc,"end",e.GlobalCommandName);
      h.Cancel = (s,e) => Record(doc,"cancel",e.GlobalCommandName);
      h.Fail = (s,e) => Record(doc,"fail",e.GlobalCommandName);
      doc.CommandWillStart += h.Start; doc.CommandEnded += h.End;
      doc.CommandCancelled += h.Cancel; doc.CommandFailed += h.Fail;
      Docs.Add(doc,h);
    }

    static void Detach(Document doc) {
      Handlers h; if (doc == null || !Docs.TryGetValue(doc,out h)) return;
      doc.CommandWillStart -= h.Start; doc.CommandEnded -= h.End;
      doc.CommandCancelled -= h.Cancel; doc.CommandFailed -= h.Fail; Docs.Remove(doc);
    }

    static string Sanitize(string raw) {
      var name=(raw ?? "").Trim().ToUpperInvariant();
      while (name.StartsWith("_") || name.StartsWith(".") || name.StartsWith("'")) name=name.Substring(1);
      return Safe.IsMatch(name) ? name : null;
    }

    static void Record(Document doc,string phase,string raw) {
      if (!Armed) return;
      var name=Sanitize(raw); if (name == null) return;
      var drawing=Path.GetFileName(doc.Name ?? "");
      var line="{\"phase\":\""+phase+"\",\"command_name\":\""+name+
               "\",\"occurred_at\":\""+DateTime.UtcNow.ToString("o")+
               "\",\"drawing_hint\":\""+Json(drawing)+"\"}";
      Append("commands.jsonl",line);
    }

    static string Json(string s) { return (s ?? "").Replace("\\","\\\\").Replace("\"","\\\""); }
    static void AppendControl(string action) {
      Append("controls.jsonl","{\"action\":\""+action+"\",\"occurred_at\":\""+DateTime.UtcNow.ToString("o")+"\"}");
    }
    static void Append(string file,string line) {
      lock(Gate) {
        Directory.CreateDirectory(Root);
        File.AppendAllText(Path.Combine(Root,file),line+Environment.NewLine,new UTF8Encoding(false));
      }
    }
  }
}
