from pathlib import Path
import sys,pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import autocad_active_command_identity_probe as p

class Clock:
    def __init__(self):self.now=0
    def __call__(self):return self.now
    def sleep(self,s):self.now+=s

class Binding:
    pid=7
    def __init__(self,*_):self.rows=[]
    def foreground_identity(self):
        return self.rows.pop(0) if self.rows else {"foreground_hwnd":100,"foreground_pid":7,
            "foreground_image":"acad.exe","bound_pid":7,"same_bound_pid":True}

class Doc:
    HWND=101
    def __init__(self,outcomes):self.outcomes=list(outcomes);self.values=[]
    def GetVariable(self,name):
        assert name=="CMDNAMES";self.values.append(name)
        outcome=self.outcomes.pop(0) if self.outcomes else "success"
        if outcome=="success":return "SECRET_COMMAND_VALUE_MUST_NOT_PERSIST"
        cls=type("com_error",(Exception,),{})
        hr={"call_rejected":-2147418111,"retry_later":-2147417846,"other_com":-2147467259}[outcome]
        e=cls(hr,"PRIVATE MESSAGE");e.hresult=hr;raise e
class App:
    Version="24.3s";HWND=100
    def __init__(self,doc):self.ActiveDocument=doc

def make_probe(outcomes=("success",)):
    doc=Doc(outcomes);app=App(doc);b=Binding()
    q=p.ActiveCommandIdentityProbe(consent=True,clock=Clock(),active_object=lambda:app,
        dispatcher=lambda x:x,binding_factory=lambda *_:b)
    return q,b,doc

@pytest.mark.parametrize("outcome",["success","call_rejected","retry_later","other_com"])
def test_sample_records_only_sanitized_outcome(outcome):
    q,b,doc=make_probe((outcome,))
    row=q.sample()
    assert row["read_outcome"]==outcome
    serialized=str(row)
    assert "SECRET_COMMAND_VALUE" not in serialized and "PRIVATE MESSAGE" not in serialized

def test_non_bound_foreground_never_reads_cmdnames():
    q,b,doc=make_probe()
    b.rows=[{"foreground_hwnd":999,"foreground_pid":8,"foreground_image":"comet.exe",
        "bound_pid":7,"same_bound_pid":False}]
    row=q.sample()
    assert row["read_outcome"]=="not_bound_foreground" and doc.values==[]

def test_identity_keeps_only_basename_not_process_path():
    q,b,_=make_probe()
    b.rows=[{"foreground_hwnd":555,"foreground_pid":7,"foreground_image":"acad.exe",
        "bound_pid":7,"same_bound_pid":True}]
    assert q.sample()["foreground_image"]=="acad.exe"

class FixtureProbe:
    def __init__(self,*,consent,clock):self.clock=clock;self.bound_pid=7;self.n=0
    def sample(self):
        self.n+=1
        return {"t":self.clock(),"foreground_hwnd":100+self.n,"foreground_pid":7,
            "foreground_image":"acad.exe","same_bound_pid":True,
            "read_outcome":"call_rejected" if self.n==2 else "success"}
    def close(self):return True

def test_run_probe_records_timeline_and_no_semantics(tmp_path,monkeypatch):
    monkeypatch.setattr(p,"PROBE_SECONDS",.31);c=Clock()
    r=p.run_probe(tmp_path/"x.json",consent=True,probe_factory=FixtureProbe,clock=c,sleep=c.sleep)
    assert r["status"]=="COMPLETE" and r["sample_count"]>=3
    assert r["outcome_counts"]["call_rejected"]==1
    assert r["semantic_inference"] is False and r["cmdnames_value_recorded"] is False
    text=(tmp_path/"x.json").read_text()
    assert "begin" not in text.lower() and "end" not in text.lower()

def test_consent_required():
    with pytest.raises(PermissionError):p.ActiveCommandIdentityProbe(consent=False)
