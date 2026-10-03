using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Pipes;
using System.Threading;
using Autodesk.AutoCAD.ApplicationServices;
using ForgeWa.AutoCAD.Semantic;

internal static class BridgeFixtureHarness
{
    private static readonly List<string> Received = new List<string>();

    private static void Server()
    {
        for (int i = 0; i < 3; i++)
        {
            using (NamedPipeServerStream pipe = new NamedPipeServerStream(
                BridgeSender.PipeName, PipeDirection.In, 1, PipeTransmissionMode.Byte))
            {
                pipe.WaitForConnection();
                using (StreamReader reader = new StreamReader(pipe))
                {
                    string line = reader.ReadLine();
                    lock (Received) Received.Add(line);
                }
            }
        }
    }

    public static int Main()
    {
        if (CommandNamePolicy.Normalize("line") != "LINE") return 10;
        if (CommandNamePolicy.Normalize("LINE 0,0") != null) return 11;
        if (CommandNamePolicy.Normalize(new string('X', 65)) != null) return 12;

        DocumentCollection documents = new DocumentCollection();
        Document document = new Document();
        documents.FixtureAdd(document);
        Application.DocumentManager = documents;

        Thread server = new Thread(Server);
        server.IsBackground = true;
        server.Start();
        Thread.Sleep(50);

        SemanticBridge bridge = new SemanticBridge();
        bridge.Initialize();
        document.FixtureStart("LINE");
        Thread.Sleep(75);
        document.FixtureEnd("LINE");
        Thread.Sleep(75);
        document.FixtureCancel("MOVE");
        server.Join(2000);
        bridge.Terminate();

        lock (Received)
        {
            if (Received.Count != 3) return 20;
            if (!Received[0].Contains("\"phase\":\"start\"") || !Received[0].Contains("\"command\":\"LINE\"")) return 21;
            if (!Received[1].Contains("\"phase\":\"end\"") || !Received[1].Contains("\"command\":\"LINE\"")) return 22;
            if (!Received[2].Contains("\"phase\":\"cancel\"") || !Received[2].Contains("\"command\":\"MOVE\"")) return 23;
            foreach (string line in Received)
            {
                if (line.Contains("argument") || line.Contains("drawing") || line.Contains("path")) return 24;
            }
        }
        Console.WriteLine("BRIDGE_FIXTURE_PASS");
        return 0;
    }
}
