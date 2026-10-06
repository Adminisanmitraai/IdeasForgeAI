using System;
using System.Collections.Generic;
using System.Text;
using System.Threading;
using ForgeWa.AutoCAD.Semantic;

internal sealed class FakeTransport : IBridgeTransport
{
    internal readonly Queue<bool> ConnectResults = new Queue<bool>();
    internal readonly Queue<bool> WriteResults = new Queue<bool>();
    internal readonly List<string> Writes = new List<string>();
    internal int ConnectCalls;
    internal int WriteCalls;
    public bool IsConnected { get; private set; }

    public bool TryConnect(int timeoutMilliseconds)
    {
        ConnectCalls++;
        bool ok = ConnectResults.Count == 0 ? true : ConnectResults.Dequeue();
        IsConnected = ok;
        return ok;
    }

    public bool TryWrite(byte[] bytes)
    {
        WriteCalls++;
        bool ok = WriteResults.Count == 0 ? true : WriteResults.Dequeue();
        if (ok) Writes.Add(Encoding.UTF8.GetString(bytes).Trim());
        else IsConnected = false;
        return ok;
    }

    public void Disconnect() { IsConnected = false; }
    public void Dispose() { Disconnect(); }
}

internal static class DeliveryReliabilityHarness
{
    private static bool Wait(Func<bool> condition)
    {
        for (int i=0;i<200;i++) { if (condition()) return true; Thread.Sleep(5); }
        return false;
    }

    private static int PersistentOrderedDelivery()
    {
        FakeTransport t=new FakeTransport();
        t.ConnectResults.Enqueue(true);
        using (BridgeSender s=new BridgeSender(t))
        {
            s.Start();
            s.TryEnqueue(new BridgeRecord(1,"start","LINE"));
            s.TryEnqueue(new BridgeRecord(2,"end","LINE"));
            s.TryEnqueue(new BridgeRecord(3,"start","MOVE"));
            s.TryEnqueue(new BridgeRecord(4,"cancel","MOVE"));
            if (!Wait(()=>s.Snapshot().Delivered==4)) return 10;
            DeliverySnapshot snap=s.Snapshot();
            if (snap.Dropped!=0 || snap.Retries!=0) return 11;
            if (t.ConnectCalls!=1 || t.WriteCalls!=4 || t.Writes.Count!=4) return 12;
            if (!t.Writes[0].Contains("\"seq\":1") || !t.Writes[1].Contains("\"seq\":2") ||
                !t.Writes[2].Contains("\"seq\":3") || !t.Writes[3].Contains("\"seq\":4")) return 13;
        }
        return 0;
    }

    private static int BoundedConnectRetry()
    {
        FakeTransport t=new FakeTransport();
        t.ConnectResults.Enqueue(false);t.ConnectResults.Enqueue(false);t.ConnectResults.Enqueue(true);
        using (BridgeSender s=new BridgeSender(t))
        {
            s.Start();s.TryEnqueue(new BridgeRecord(10,"start","COPY"));
            if (!Wait(()=>s.Snapshot().Delivered==1)) return 20;
            DeliverySnapshot snap=s.Snapshot();
            if (snap.Retries!=2 || snap.Dropped!=0 || t.ConnectCalls!=3 || t.Writes.Count!=1) return 21;
        }
        return 0;
    }

    private static int ExhaustedConnectDropsOnce()
    {
        FakeTransport t=new FakeTransport();
        for(int i=0;i<BridgeSender.MaxConnectAttempts;i++) t.ConnectResults.Enqueue(false);
        using (BridgeSender s=new BridgeSender(t))
        {
            s.Start();s.TryEnqueue(new BridgeRecord(20,"start","TRIM"));
            if (!Wait(()=>s.Snapshot().Dropped==1)) return 30;
            DeliverySnapshot snap=s.Snapshot();
            if (snap.Delivered!=0 || t.Writes.Count!=0 || t.ConnectCalls!=BridgeSender.MaxConnectAttempts) return 31;
            if (snap.Retries!=BridgeSender.MaxConnectAttempts-1) return 32;
        }
        return 0;
    }

    private static int AmbiguousWriteFailureNeverRetriesRecord()
    {
        FakeTransport t=new FakeTransport();t.ConnectResults.Enqueue(true);t.WriteResults.Enqueue(false);
        using (BridgeSender s=new BridgeSender(t))
        {
            s.Start();s.TryEnqueue(new BridgeRecord(30,"start","POLYLINE"));
            if (!Wait(()=>s.Snapshot().Dropped==1)) return 40;
            if (t.WriteCalls!=1 || t.Writes.Count!=0 || s.Snapshot().Delivered!=0) return 41;
        }
        return 0;
    }

    private static int ReconnectOnNextRecord()
    {
        FakeTransport t=new FakeTransport();
        t.ConnectResults.Enqueue(true);t.ConnectResults.Enqueue(true);
        t.WriteResults.Enqueue(false);t.WriteResults.Enqueue(true);
        using (BridgeSender s=new BridgeSender(t))
        {
            s.Start();
            s.TryEnqueue(new BridgeRecord(40,"start","RECTANGLE"));
            if (!Wait(()=>s.Snapshot().Dropped==1)) return 50;
            s.TryEnqueue(new BridgeRecord(41,"cancel","RECTANGLE"));
            if (!Wait(()=>s.Snapshot().Delivered==1)) return 51;
            if (t.ConnectCalls!=2 || t.WriteCalls!=2 || t.Writes.Count!=1) return 52;
            if (!t.Writes[0].Contains("\"seq\":41")) return 53;
        }
        return 0;
    }

    public static int Main()
    {
        int[] results={PersistentOrderedDelivery(),BoundedConnectRetry(),ExhaustedConnectDropsOnce(),
            AmbiguousWriteFailureNeverRetriesRecord(),ReconnectOnNextRecord()};
        foreach(int result in results) if(result!=0) return result;
        Console.WriteLine("DELIVERY_RELIABILITY_PASS");
        return 0;
    }
}
