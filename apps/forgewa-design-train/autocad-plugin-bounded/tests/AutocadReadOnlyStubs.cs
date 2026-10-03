// TEST ONLY. Never reference this file in the AutoCAD plugin DLL build.
using System;
namespace Autodesk.AutoCAD.Runtime {
  public interface IExtensionApplication { void Initialize(); void Terminate(); }
  [AttributeUsage(AttributeTargets.Assembly)] public sealed class ExtensionApplicationAttribute : Attribute {
    public ExtensionApplicationAttribute(Type type) { }
  }
  public enum CommandFlags { Session }
  [AttributeUsage(AttributeTargets.Method)] public sealed class CommandMethodAttribute : Attribute {
    public CommandMethodAttribute(string name, CommandFlags flags) { }
  }
}
namespace Autodesk.AutoCAD.ApplicationServices {
  public delegate void CommandEventHandler(object sender, CommandEventArgs args);
  public sealed class CommandEventArgs : EventArgs {
    readonly string value; readonly bool fail;
    public CommandEventArgs(string name, bool throwOnRead) { value = name; fail = throwOnRead; }
    public string GlobalCommandName { get { if (fail) throw new InvalidOperationException("fixture"); return value; } }
  }
  public sealed class DocumentCollectionEventArgs : EventArgs {
    public Document Document { get; private set; }
    public DocumentCollectionEventArgs(Document d) { Document = d; }
  }
  public sealed class FakeEditor {
    public int OutputCount;
    public void WriteMessage(string value) { OutputCount++; }
  }
  public sealed class Document {
    public string Name = "Fixture.dwg";
    public readonly FakeEditor Editor = new FakeEditor();
    public event CommandEventHandler CommandWillStart, CommandEnded, CommandCancelled, CommandFailed;
    public int Subscribers {
      get { return Count(CommandWillStart) + Count(CommandEnded) + Count(CommandCancelled) + Count(CommandFailed); }
    }
    static int Count(Delegate d) { return d == null ? 0 : d.GetInvocationList().Length; }
    public void Emit(string phase, string name) { Emit(phase, name, false); }
    public void Emit(string phase, string name, bool fail) {
      var handler = phase == "start" ? CommandWillStart : phase == "end" ? CommandEnded : phase == "cancel" ? CommandCancelled : CommandFailed;
      if (handler != null) handler(this, new CommandEventArgs(name, fail));
    }
  }
  public sealed class DocumentCollection {
    public Document MdiActiveDocument;
    public event EventHandler<DocumentCollectionEventArgs> DocumentToBeDestroyed;
    public void Destroy(Document d) { if (DocumentToBeDestroyed != null) DocumentToBeDestroyed(this, new DocumentCollectionEventArgs(d)); }
  }
  public static class Application {
    public static DocumentCollection DocumentManager = new DocumentCollection();
    public static event EventHandler Idle;
    public static void TickIdle() { if (Idle != null) Idle(null, EventArgs.Empty); }
  }
}
