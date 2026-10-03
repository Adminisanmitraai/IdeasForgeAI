using System;
using System.Collections;
using System.Collections.Generic;

namespace Autodesk.AutoCAD.Runtime
{
    [AttributeUsage(AttributeTargets.Assembly)]
    public sealed class ExtensionApplicationAttribute : Attribute
    {
        public ExtensionApplicationAttribute(Type type) { }
    }
    public interface IExtensionApplication { void Initialize(); void Terminate(); }
}

namespace Autodesk.AutoCAD.ApplicationServices
{
    public delegate void CommandEventHandler(object sender, CommandEventArgs args);
    public delegate void DocumentCollectionEventHandler(object sender, DocumentCollectionEventArgs args);

    public sealed class CommandEventArgs : EventArgs
    {
        public string GlobalCommandName { get; set; }
    }

    public sealed class DocumentCollectionEventArgs : EventArgs
    {
        public Document Document { get; set; }
    }

    public class Document
    {
        public event CommandEventHandler CommandWillStart;
        public event CommandEventHandler CommandEnded;
        public event CommandEventHandler CommandCancelled;

        public void FixtureStart(string name) { if (CommandWillStart != null) CommandWillStart(this, new CommandEventArgs { GlobalCommandName = name }); }
        public void FixtureEnd(string name) { if (CommandEnded != null) CommandEnded(this, new CommandEventArgs { GlobalCommandName = name }); }
        public void FixtureCancel(string name) { if (CommandCancelled != null) CommandCancelled(this, new CommandEventArgs { GlobalCommandName = name }); }
    }

    public class DocumentCollection : IEnumerable<Document>
    {
        private readonly List<Document> items = new List<Document>();
        public event DocumentCollectionEventHandler DocumentCreated;
        public IEnumerator<Document> GetEnumerator() { return items.GetEnumerator(); }
        IEnumerator IEnumerable.GetEnumerator() { return GetEnumerator(); }
        public void FixtureAdd(Document document)
        {
            items.Add(document);
            if (DocumentCreated != null) DocumentCreated(this, new DocumentCollectionEventArgs { Document = document });
        }
    }

    public static class Application
    {
        public static DocumentCollection DocumentManager { get; set; }
    }
}
