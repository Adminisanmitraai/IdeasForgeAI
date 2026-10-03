"""Synthetic-only crash-safe CMDNAMES polling tests. Never attach to AutoCAD."""
from pathlib import Path
import ast
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from autocad_semantic import CmdNamesTransitionDetector, parse_cmdnames
import autocad_semantic_native as native


class Clock:
    def __init__(self): self.now=0.0
    def __call__(self): return self.now


@pytest.mark.parametrize("raw,expected",[
    ("",()),("LINE",("LINE",)),("LINE'ZOOM",("LINE","ZOOM")),
    ("_LINE",("LINE",)),("_.MOVE",("MOVE",)),("-LAYER",("-LAYER",))
])
def test_cmdnames_parser(raw,expected):
    assert parse_cmdnames(raw)==expected


@pytest.mark.parametrize("raw",[
    None,True,123,"LINE 0,0","LINE''ZOOM","UNKNOWN","C:\\private.dwg",
    "(load x)","LINE;ERASE","X"*257
])
def test_cmdnames_parser_rejects_unsafe_or_unknown(raw):
    assert parse_cmdnames(raw) is None


def test_first_nonempty_sample_is_baseline_only():
    c=Clock(); d=CmdNamesTransitionDetector("doc",clock=c,occurred_at=lambda:"fixture")
    assert d.feed("LINE")==()
    c.now=.25
    assert d.feed("")==()
    c.now=.5
    rows=d.feed("MOVE")
    assert [(r.phase,r.name) for r in rows]==[("begin","MOVE")]


def test_simple_begin_end_transitions():
    c=Clock(); d=CmdNamesTransitionDetector("doc",clock=c,occurred_at=lambda:"fixture")
    assert d.feed("")==()
    c.now=.25; begin=d.feed("LINE")
    c.now=.5; end=d.feed("")
    assert [(x.phase,x.name) for x in begin+end]==[("begin","LINE"),("end","LINE")]
    assert [x.sequence for x in begin+end]==[1,2]
    assert all(x.source=="autocad_cmdnames_poll" for x in begin+end)


def test_transparent_nested_transition():
    c=Clock(); d=CmdNamesTransitionDetector("doc",clock=c,occurred_at=lambda:"fixture")
    d.feed("")
    c.now=.25; a=d.feed("LINE")
    c.now=.5; b=d.feed("LINE'ZOOM")
    c.now=.75; crows=d.feed("LINE")
    c.now=1.0; e=d.feed("")
    assert [(x.phase,x.name) for x in a+b+crows+e]==[
        ("begin","LINE"),("begin","ZOOM"),("end","ZOOM"),("end","LINE")]


def test_direct_root_replacement_is_gap_not_fabricated_boundary():
    c=Clock(); d=CmdNamesTransitionDetector("doc",clock=c,occurred_at=lambda:"fixture")
    d.feed(""); c.now=.25
    assert [(x.phase,x.name) for x in d.feed("LINE")]==[("begin","LINE")]
    c.now=.5
    assert d.feed("MOVE")==()
    assert d.gaps==1
    c.now=.75
    assert d.feed("")==()
    c.now=1.0
    assert [(x.phase,x.name) for x in d.feed("COPY")]==[("begin","COPY")]


def test_malformed_snapshot_forces_resync():
    c=Clock(); d=CmdNamesTransitionDetector("doc",clock=c,occurred_at=lambda:"fixture")
    d.feed(""); c.now=.25
    assert d.feed("LINE")
    c.now=.5
    assert d.feed("SECRET ARGUMENT")==() and d.gaps==1
    c.now=.75
    assert d.feed("")==()
    c.now=1
    assert d.feed("REGEN")[0].name=="REGEN"


class FakeBinding:
    hwnd=100; document_hwnd=101; pid=200
    def __init__(self): self.enabled=True
    def active(self): return self.enabled


class FakeDoc:
    HWND=101; Name="Demo.dwg"
    def __init__(self,values): self.values=list(values); self.calls=[]
    def GetVariable(self,name):
        self.calls.append(name)
        return self.values.pop(0)


class FakeApp:
    Version="24.3s"
    HWND=100
    def __init__(self,doc): self.ActiveDocument=doc


def make_source(monkeypatch,clock,values):
    doc=FakeDoc(values); app=FakeApp(doc)
    monkeypatch.setattr(native,"WindowsBinding",lambda *_:FakeBinding())
    source=native.AutoCADCmdNamesPoller(deadline=10,consent=True,clock=clock,
        active_object=lambda:app,dispatcher=lambda value:value)
    return source,doc


def test_poller_reads_only_cmdnames_at_low_frequency(monkeypatch):
    c=Clock(); source,doc=make_source(monkeypatch,c,["","LINE",""])
    assert source.poll()==()
    c.now=.1; assert source.poll()==()
    c.now=.25; assert source.poll()[0].name=="LINE"
    c.now=.5; assert source.poll()[0].phase=="end"
    assert doc.calls==["CMDNAMES","CMDNAMES","CMDNAMES"]
    assert source.polls==3 and source.events==2
    assert source.metadata["connection_point"] is False
    assert source.metadata["callbacks"] is False


def test_poller_never_reads_when_not_foreground(monkeypatch):
    c=Clock(); source,doc=make_source(monkeypatch,c,[""])
    source.binding.enabled=False
    assert source.poll()==() and doc.calls==[]
    assert source.detector.gaps==1


def test_poller_deadline_and_retain_false_do_not_read(monkeypatch):
    c=Clock(); source,doc=make_source(monkeypatch,c,[""])
    c.now=10
    assert source.poll()==() and doc.calls==[]
    source2,doc2=make_source(monkeypatch,Clock(),[""])
    source2.retain=False
    assert source2.poll()==() and doc2.calls==[]


def test_close_releases_without_unsubscribe(monkeypatch):
    c=Clock(); source,_=make_source(monkeypatch,c,[""])
    assert source.close() is True and source.released
    assert source.doc is None and source.app is None


def test_native_source_has_no_connectionpoint_or_mutation_calls():
    root=Path(__file__).resolve().parents[1]
    path=root/"autocad_semantic_native.py"
    text=path.read_text(encoding="utf-8")
    forbidden_text=["Advise(","Unadvise(","FindConnectionPoint","IConnectionPointContainer",
                    "SetVariable(","SendCommand(","PostCommand(","SendStringToExecute(",
                    "CreateObject(","CoCreateInstance(","SetWindowsHookEx"]
    assert [item for item in forbidden_text if item in text]==[]
    tree=ast.parse(text)
    getvars=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Call):
            name=getattr(node.func,"attr",getattr(node.func,"id",""))
            if name=="GetVariable":
                getvars.append(node)
    assert len(getvars)==1
    assert isinstance(getvars[0].args[0],ast.Constant)
    assert getvars[0].args[0].value=="CMDNAMES"
