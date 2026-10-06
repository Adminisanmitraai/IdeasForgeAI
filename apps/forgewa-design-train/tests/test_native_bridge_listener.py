from pathlib import Path
import json,sys,pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import native_bridge_listener as n

def line(seq,phase="start",command="LINE"):
    return json.dumps({"v":1,"seq":seq,"phase":phase,"command":command})

def test_ordered_records_accepted():
    s=n.ListenerState()
    assert n.accept_line(line(1),s)["seq"]==1
    assert n.accept_line(line(2,"end"),s)["seq"]==2
    assert s.accepted==2 and s.duplicates==0

def test_duplicate_and_old_sequences_dropped():
    s=n.ListenerState()
    assert n.accept_line(line(4),s)
    assert n.accept_line(line(4),s) is None
    assert n.accept_line(line(3),s) is None
    assert s.accepted==1 and s.duplicates==2 and s.last_sequence==4

@pytest.mark.parametrize("row",[
    {"v":1,"seq":1,"phase":"start","command":"LINE","args":"0,0"},
    {"v":1,"seq":True,"phase":"start","command":"LINE"},
    {"v":1,"seq":1,"phase":"other","command":"LINE"},
    {"v":1,"seq":1,"phase":"start","command":"LINE 0,0"},
])
def test_invalid_payloads_fail_closed(row):
    s=n.ListenerState()
    assert n.accept_line(json.dumps(row),s) is None and s.invalid==1

def test_reconnect_does_not_reset_sequence_authority():
    s=n.ListenerState()
    assert n.accept_line(line(10),s)
    s.reconnects+=1
    assert n.accept_line(line(10),s) is None
    assert n.accept_line(line(11,"cancel"),s)["seq"]==11
    assert s.reconnects==1 and s.duplicates==1 and s.accepted==2
