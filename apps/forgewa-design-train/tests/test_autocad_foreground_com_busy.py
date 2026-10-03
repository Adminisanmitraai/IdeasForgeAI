from pathlib import Path
import sys,pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import autocad_semantic_native as n

class U:
    def __init__(self,fg): self.fg=fg
    def GetForegroundWindow(self): return self.fg
    def IsWindow(self,hwnd): return True

def binding(fg,pids):
    b=n.WindowsBinding.__new__(n.WindowsBinding)
    b.hwnd=100; b.document_hwnd=101; b.pid=7; b.u=U(fg)
    b.window_pid=lambda hwnd:pids.get(hwnd,0)
    return b

def test_main_hwnd_foreground_is_active():
    assert binding(100,{100:7,101:7}).active()

def test_child_hwnd_same_bound_acad_pid_is_active():
    b=binding(555,{100:7,101:7,555:7})
    assert b.active()
    assert b.foreground_identity()=={"foreground_hwnd":555,"foreground_pid":7,"bound_pid":7,"same_bound_pid":True}

@pytest.mark.parametrize("fg,pids",[(555,{100:7,101:7,555:8}),(0,{100:7,101:7}),(555,{100:8,101:7,555:7})])
def test_non_bound_pid_or_broken_binding_rejected(fg,pids):
    assert not binding(fg,pids).active()

def com_error(hr):
    cls=type("com_error",(Exception,),{})
    e=cls(hr,"PRIVATE COM MESSAGE MUST NOT PERSIST")
    e.hresult=hr
    return e

@pytest.mark.parametrize("hr,category",[
    (-2147418111,"call_rejected"),(0x80010001,"call_rejected"),
    (-2147417846,"retry_later"),(0x8001010A,"retry_later"),
    (-2147467259,"other_com")])
def test_com_classification_is_sanitized(hr,category):
    e=com_error(hr)
    assert n.classify_com_exception(e)==category
    assert "PRIVATE" not in n.classify_com_exception(e)

def test_non_com_exception_not_classified():
    assert n.classify_com_exception(RuntimeError("private")) is None

class Clock:
    now=0.0
    def __call__(self): return self.now

class Detector:
    def __init__(self): self.gaps=0; self.interrupts=0
    def interrupt(self): self.gaps+=1; self.interrupts+=1
    def feed(self,raw): raise AssertionError("busy sample must not reach transition detector")

class Doc:
    def __init__(self,exc): self.exc=exc; self.calls=0
    def GetVariable(self,name):
        assert name=="CMDNAMES"; self.calls+=1; raise self.exc

class Active:
    def active(self): return True

def poller_with(exc):
    p=n.AutoCADCmdNamesPoller.__new__(n.AutoCADCmdNamesPoller)
    p.clock=Clock(); p.deadline=10; p.retain=True; p.next_poll=0
    p.polls=p.events=p.foreground_gaps=p.com_missing_samples=0
    p.last_com_category=None; p.binding=Active(); p.detector=Detector(); p.doc=Doc(exc)
    return p

@pytest.mark.parametrize("hr,category",[(-2147418111,"call_rejected"),(-2147417846,"retry_later")])
def test_transient_com_busy_is_missing_sample_not_event(hr,category):
    p=poller_with(com_error(hr))
    assert p.poll()==()
    assert p.polls==1 and p.events==0 and p.com_missing_samples==1
    assert p.last_com_category==category and p.detector.interrupts==1

def test_nontransient_com_error_fails_closed():
    p=poller_with(com_error(-2147467259))
    with pytest.raises(Exception) as info:p.poll()
    assert type(info.value).__name__=="com_error"
    assert p.events==0 and p.com_missing_samples==0
