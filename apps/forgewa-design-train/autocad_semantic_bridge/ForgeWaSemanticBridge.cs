using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Pipes;
using System.Text;
using System.Threading;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.Runtime;

[assembly: ExtensionApplication(typeof(ForgeWa.AutoCAD.Semantic.SemanticBridge))]

namespace ForgeWa.AutoCAD.Semantic
{
    public sealed class SemanticBridge : IExtensionApplication
    {
        private readonly object gate = new object();
        private readonly List<WeakReference> documents = new List<WeakReference>();
        private readonly BridgeSender sender = new BridgeSender();
        private DocumentCollection manager;
        private long sequence;

        public void Initialize()
        {
            manager = Application.DocumentManager;
            manager.DocumentCreated += OnDocumentCreated;
            foreach (Document document in manager) Attach(document);
            sender.Start();
        }

        public void Terminate()
        {
            if (manager != null) manager.DocumentCreated -= OnDocumentCreated;
            lock (gate)
            {
                foreach (WeakReference reference in documents)
                {
                    Document document = reference.Target as Document;
                    if (document != null) Detach(document);
                }
                documents.Clear();
            }
            sender.Dispose();
            manager = null;
        }

        private void OnDocumentCreated(object senderObject, DocumentCollectionEventArgs args)
        {
            if (args != null && args.Document != null) Attach(args.Document);
        }

        private void Attach(Document document)
        {
            lock (gate)
            {
                foreach (WeakReference reference in documents)
                    if (Object.ReferenceEquals(reference.Target, document)) return;
                document.CommandWillStart += OnCommandWillStart;
                document.CommandEnded += OnCommandEnded;
                document.CommandCancelled += OnCommandCancelled;
                documents.Add(new WeakReference(document));
            }
        }

        private void Detach(Document document)
        {
            document.CommandWillStart -= OnCommandWillStart;
            document.CommandEnded -= OnCommandEnded;
            document.CommandCancelled -= OnCommandCancelled;
        }

        private void OnCommandWillStart(object senderObject, CommandEventArgs args) { Emit("start", args); }
        private void OnCommandEnded(object senderObject, CommandEventArgs args) { Emit("end", args); }
        private void OnCommandCancelled(object senderObject, CommandEventArgs args) { Emit("cancel", args); }

        private void Emit(string phase, CommandEventArgs args)
        {
            string name = CommandNamePolicy.Normalize(args == null ? null : args.GlobalCommandName);
            if (name == null) return;
            long id = Interlocked.Increment(ref sequence);
            sender.TryEnqueue(new BridgeRecord(id, phase, name));
        }
    }

    internal static class CommandNamePolicy
    {
        internal static string Normalize(string value)
        {
            if (String.IsNullOrEmpty(value) || value.Length > 64) return null;
            string name = value.ToUpperInvariant();
            for (int i = 0; i < name.Length; i++)
            {
                char c = name[i];
                if (!((c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_' || c == '-'))
                    return null;
            }
            return name;
        }
    }

    internal sealed class BridgeRecord
    {
        internal readonly long Sequence;
        internal readonly string Phase;
        internal readonly string Command;
        internal BridgeRecord(long sequence, string phase, string command)
        { Sequence = sequence; Phase = phase; Command = command; }

        internal string ToJson()
        {
            return "{\"v\":1,\"seq\":" + Sequence.ToString(System.Globalization.CultureInfo.InvariantCulture) +
                ",\"phase\":\"" + Phase + "\",\"command\":\"" + Command + "\"}";
        }
    }

    internal sealed class BridgeSender : IDisposable
    {
        internal const string PipeName = "ForgeWa.AutoCAD.Semantic.v1";
        private const int Capacity = 256;
        private readonly object gate = new object();
        private readonly Queue<BridgeRecord> queue = new Queue<BridgeRecord>();
        private readonly AutoResetEvent signal = new AutoResetEvent(false);
        private Thread thread;
        private volatile bool stopping;

        internal void Start()
        {
            if (thread != null) return;
            thread = new Thread(Run);
            thread.IsBackground = true;
            thread.Name = "ForgeWaAutoCADSemanticOutbound";
            thread.Start();
        }

        internal bool TryEnqueue(BridgeRecord record)
        {
            lock (gate)
            {
                if (stopping || queue.Count >= Capacity) return false;
                queue.Enqueue(record);
            }
            signal.Set();
            return true;
        }

        private void Run()
        {
            while (!stopping)
            {
                BridgeRecord record = null;
                lock (gate) { if (queue.Count > 0) record = queue.Dequeue(); }
                if (record == null) { signal.WaitOne(250); continue; }
                TrySend(record);
            }
        }

        private static void TrySend(BridgeRecord record)
        {
            try
            {
                using (NamedPipeClientStream pipe = new NamedPipeClientStream(
                    ".", PipeName, PipeDirection.Out, PipeOptions.Asynchronous))
                {
                    pipe.Connect(25);
                    byte[] bytes = Encoding.UTF8.GetBytes(record.ToJson() + "\n");
                    pipe.Write(bytes, 0, bytes.Length);
                    pipe.Flush();
                }
            }
            catch (IOException) { }
            catch (TimeoutException) { }
            catch (UnauthorizedAccessException) { }
        }

        public void Dispose()
        {
            stopping = true;
            signal.Set();
            if (thread != null) thread.Join(300);
            signal.Dispose();
            thread = null;
        }
    }
}
