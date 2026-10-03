// TEST ONLY executable; compiles the exact candidate with stub Autodesk types.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Threading;
using ForgeWa.Bounded;
using Autodesk.AutoCAD.ApplicationServices;

internal static class BoundedObserverTests {
  static readonly List<string> Results = new List<string>();
  static string Root;
  static int Failed;
  static CommandObserver Plugin;
  static Document Doc;
  static void Check(bool ok, string message) { if (!ok) throw new System.Exception(message); }
  static void Test(string name, Action body) {
    try { body(); Results.Add("{\"name\":" + CaptureRun.J(name) + ",\"status\":\"PASS\"}"); }
    catch (System.Exception e) { Failed++; Results.Add("{\"name\":" + CaptureRun.J(name) + ",\"status\":\"FAIL\",\"error\":" + CaptureRun.J(e.Message) + "}"); }
    finally { if (Plugin != null) Plugin.Terminate(); }
  }
  static void Reset() {
    if (Plugin != null) Plugin.Terminate();
    Application.DocumentManager = new DocumentCollection(); Doc = new Document();
    Application.DocumentManager.MdiActiveDocument = Doc;
    CommandObserver.Current = null;
    Plugin = new CommandObserver(); Plugin.Initialize();
    CommandObserver.Root = Path.Combine(Root, Guid.NewGuid().ToString("N"));
  }
  static void Saved(CaptureRun r) {
    Check(SpinWait.SpinUntil(() => r.SavingComplete, 3000), "save_not_completed");
    Check(r.Saved && r.SaveError == null, "unexpected_save_error");
  }
  public static int Main(string[] args) {
    Root = Path.GetFullPath(args[0]); Directory.CreateDirectory(Root);
    Test("load_is_idle_no_files_or_document_hooks", () => { Reset(); Check(Doc.Subscribers == 0 && CommandObserver.Current == null && !Directory.Exists(CommandObserver.Root), "not_idle"); });
    Test("normalize_only_command_names", () => { Check(CaptureRun.Normalize("._line") == "LINE" && CaptureRun.Normalize("'zoom") == "ZOOM", "normalization"); });
    Test("reject_free_text_arguments_and_newlines", () => { foreach (var raw in new[] { "", "LINE 0,0", "MOVE\n", "MOVE\t", "(command)", new string('A',65), "123", "__", " LINE" }) Check(CaptureRun.Normalize(raw) == null, "accepted_bad_name"); });
    Test("json_escapes_all_control_characters", () => { Check(CaptureRun.J("a\n\t\"\\") == "\"a\\u000a\\u0009\\\"\\\\\"", "json_escape"); });
    Test("same_command_id_start_end", () => { var r=new CaptureRun("Fixture.dwg",()=>0,_=>{}); r.Accept("start","MOVE");r.Accept("end","MOVE");r.Stop("user_stop");Check(r.Count==2 && r.Pending==0 && r.Rows[0].Contains("\"command_id\":1") && r.Rows[1].Contains("\"command_id\":1"),"pair"); });
    foreach (var outcome in new[] { "cancel", "fail" }) {
      string phase=outcome;
      Test("terminal_"+phase, () => { var r=new CaptureRun("Fixture.dwg",()=>0,_=>{});r.Accept("start","LINE");r.Accept(phase,"LINE");Check(r.Count==2 && r.Pending==0,"terminal"); });
    }
    Test("nested_transparent_commands_keep_distinct_ids", () => { var r=new CaptureRun("x",()=>0,_=>{});r.Accept("start","LINE");r.Accept("start","'ZOOM");r.Accept("end","ZOOM");r.Accept("end","LINE");Check(r.Count==4 && r.Pending==0 && r.Rows[2].Contains("\"command_id\":2"),"nested"); });
    Test("orphan_terminal_not_fabricated", () => { var r=new CaptureRun("x",()=>0,_=>{});r.Accept("end","LINE");Check(r.Count==0,"orphan"); });
    Test("mismatch_fails_closed", () => { var r=new CaptureRun("x",()=>0,_=>{});r.Accept("start","LINE");r.Accept("end","MOVE");Check(!r.Active && r.Reason=="pairing_mismatch" && r.Count==1 && r.Pending==1,"mismatch"); });
    Test("exact_deadline_rejects_command", () => { double ms=0;var r=new CaptureRun("x",()=>ms,_=>{});ms=10000;r.Accept("start","LINE");Check(!r.Active && r.Count==0 && r.Reason=="time_limit","deadline"); });
    Test("timeout_preserves_incomplete_command", () => { double ms=0;var r=new CaptureRun("x",()=>ms,_=>{});r.Accept("start","LINE");ms=10000;r.Accept("end","LINE");Check(r.Count==1 && r.Pending==1 && r.Summary().Contains("\"lifecycle_complete\":false"),"false_end"); });
    Test("event_cap_is_forty", () => { var r=new CaptureRun("x",()=>0,_=>{});for(int i=0;i<30;i++){r.Accept("start","LINE");r.Accept("end","LINE");}Check(r.Count==40 && r.Reason=="event_limit" && !r.Active,"event_cap"); });
    Test("stop_is_idempotent", () => { int writes=0;var r=new CaptureRun("x",()=>0,_=>writes++);r.Stop("user_stop");r.Stop("time_limit");r.Accept("start","LINE");Check(writes==1 && r.Count==0 && r.Reason=="user_stop","double_stop"); });
    Test("sink_exception_cannot_escape", () => { var r=new CaptureRun("x",()=>0,_=>{throw new IOException("fixture");});r.Stop("user_stop");Check(!r.Active && r.SaveError=="IOException","escaped"); });
    Test("observer_control_names_excluded", () => { var r=new CaptureRun("x",()=>0,_=>{});r.Accept("start","FORGEWA_SEM_START");r.Accept("end","FORGEWA_SEM_STATUS");Check(r.Count==0,"control_recorded"); });
    Test("only_selected_document_is_subscribed", () => { Reset();var other=new Document();CommandObserver.StartObserver();Check(Doc.Subscribers==4 && other.Subscribers==0,"scope");Doc.Emit("start","LINE");Doc.Emit("end","LINE");CommandObserver.StopObserver();Saved(CommandObserver.Current);Check(Doc.Subscribers==0,"not_detached"); });
    Test("duplicate_start_keeps_same_run", () => { Reset();CommandObserver.StartObserver();var r=CommandObserver.Current;CommandObserver.StartObserver();Check(Object.ReferenceEquals(r,CommandObserver.Current),"budget_reset");CommandObserver.StopObserver();Saved(r); });
    Test("manual_stop_blocks_later_events", () => { Reset();CommandObserver.StartObserver();Doc.Emit("start","LINE");Doc.Emit("cancel","LINE");CommandObserver.StopObserver();var r=CommandObserver.Current;Doc.Emit("start","MOVE");Saved(r);Check(r.Count==2 && r.Reason=="user_stop" && !r.Active,"post_stop"); });
    Test("document_change_stops_without_other_doc_data", () => { Reset();CommandObserver.StartObserver();var r=CommandObserver.Current;Application.DocumentManager.MdiActiveDocument=new Document();Doc.Emit("start","LINE");Saved(r);Check(r.Count==0 && r.Reason=="document_changed","scope_leak"); });
    Test("document_close_disarms", () => { Reset();CommandObserver.StartObserver();var r=CommandObserver.Current;Application.DocumentManager.Destroy(Doc);Saved(r);Check(!r.Active && Doc.Subscribers==0 && r.Reason=="document_closed","close"); });
    Test("callback_exception_is_contained", () => { Reset();CommandObserver.StartObserver();Doc.Emit("start","LINE",true);var r=CommandObserver.Current;Saved(r);Check(r.Reason=="observer_error" && !r.Active,"callback"); });
    Test("status_does_not_arm", () => { Reset();CommandObserver.StatusObserver();Check(CommandObserver.Current==null && Doc.Subscribers==0 && File.Exists(Path.Combine(CommandObserver.Root,"observer_status.json")),"status_armed"); });
    Test("no_command_file_write_inside_live_callback", () => { Reset();CommandObserver.StartObserver();Doc.Emit("start","LINE");Check(!Directory.Exists(CommandObserver.Root),"io_during_callback");Doc.Emit("end","LINE");CommandObserver.StopObserver();Saved(CommandObserver.Current); });
    Test("failed_disk_write_remains_disarmed", () => { Reset();File.WriteAllText(CommandObserver.Root,"fixture_blocker");CommandObserver.StartObserver();var r=CommandObserver.Current;CommandObserver.StopObserver();Check(SpinWait.SpinUntil(()=>r.SavingComplete,3000) && !r.Saved && r.SaveError!=null && !r.Active,"io_failure"); });
    Test("ten_second_real_timer_expires_without_any_command", () => {
      Reset();var sw=Stopwatch.StartNew();CommandObserver.StartObserver();var r=CommandObserver.Current;
      Check(SpinWait.SpinUntil(()=>r.Reason!=null,11500),"timer_missing");Saved(r);Application.TickIdle();
      Check(!r.Active && r.Count==0 && r.Reason=="time_limit" && Doc.Subscribers==0,"timer_failed");
      Check(sw.Elapsed.TotalSeconds>=9.8 && sw.Elapsed.TotalSeconds<11.5,"timer_delay");
    });
    string json="{\"status\":"+CaptureRun.J(Failed==0?"PASS":"FAIL")+",\"passed\":"+(Results.Count-Failed)+",\"failed\":"+Failed+",\"total\":"+Results.Count+",\"source\":\"compiled_CSharp_with_AutoCAD_stubs\",\"live_autocad_calls\":false,\"results\":["+String.Join(",",Results)+"]}";
    File.WriteAllText(Path.Combine(Root,"bounded_test_results.json"),json);Console.WriteLine(json);
    return Failed==0?0:1;
  }
}
