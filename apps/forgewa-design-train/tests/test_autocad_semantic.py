from pathlib import Path
from dataclasses import replace
import ast
import json
import sys
import time
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from autocad_semantic import *
from autocad_semantic_native import WindowEvidenceSource
from autocad_semantic_worker import SemanticClient
from demonstration_capture import screen_observation, safe_input_event


class Clock:
    now = 0.0
    def __call__(self): return self.now


@pytest.mark.parametrize('raw,expected',[('REGEN','REGEN'),('_line','LINE'),('_.MOVE','MOVE'),("'ZOOM",'ZOOM'),('-LAYER','-LAYER')])
def test_command_names_normalize(raw,expected):
    assert command_name(raw)==expected


@pytest.mark.parametrize('raw',['LINE 0,0 1,1','MOVE\nsecret','password123','C:\\private.dwg','(load x)','',None,True,123,'X'*65,'LINE\x00','LINE;ERASE'])
def test_arguments_text_custom_names_rejected(raw):
    assert command_name(raw) is None


def test_queue_requires_active_scope_deadline_and_retention():
    clock=Clock(); selected=[False]
    q=CommandQueue('d',clock,lambda:selected[0],10)
    assert not q.offer('begin','LINE')
    selected[0]=True
    assert q.offer('begin','_LINE')
    clock.now=10
    assert not q.offer('end','LINE')
    assert len(q.drain())==1
    q.close(); clock.now=1
    assert not q.offer('end','LINE')
    probe=CommandQueue('d',clock,lambda:True,10,retain=False)
    assert not probe.offer('begin','LINE') and not probe.drain()


def test_queue_cap_and_payload_projection():
    q=CommandQueue('d',Clock(),lambda:True,10)
    for i in range(MAX_EVENTS): assert q.offer('begin','REGEN')
    assert not q.offer('begin','REGEN') and q.overflow
    assert len(q.drain())==MAX_EVENTS
    assert not q.drain()
    assert not q.offer('unknown','SECRET VALUE')
    assert q.rejected==1


def event(sequence,phase,name='LINE',at=None,token='d'):
    return CommandEvent(sequence,phase,name,sequence if at is None else at,'fixture-time',token)


def frame(phase,at,token='d',hwnd=100,pid=200,project='Demo.dwg'):
    observation=screen_observation(phase=phase,application='autocad',project_hint=project,
        frame_bytes=(phase+str(at)).encode(),width=100,height=100,local_frame_ref='fixture_'+phase+'.png')
    return TimedFrame(observation,at,token,hwnd,pid)


def corr():
    events,spans,steps=[],[],[]
    return SemanticCorrelator('run','d',events.append,spans.append,steps.append),events,spans,steps


def test_complete_command_correlates_interaction_and_frames():
    c,events,spans,steps=corr()
    c.event(event(1,'begin'),before=frame('before',.8))
    click=safe_input_event(application='autocad',kind='mouse_click',button='left',x_norm=.2,y_norm=.3)
    assert c.interaction(click,1.1)
    c.event(event(2,'end'),after=frame('after',2.1))
    assert c.steps==c.pairs==1 and len(events)==2
    assert steps[0]['demonstration']['action']['command_name']=='LINE'
    assert steps[0]['span']['command_success'] is None
    assert steps[0]['interactions'][0]['kind']=='mouse_click'
    assert 'temporal' in steps[0]['association']


@pytest.mark.parametrize('before,after,hold',[
    (None,frame('after',2.1),'frame_pair_unavailable'),
    (frame('before',.8),None,'frame_pair_unavailable'),
    (frame('before',0),frame('after',2.1),'frame_timing_invalid'),
    (frame('before',1.1),frame('after',2.1),'frame_timing_invalid'),
    (frame('before',.8),frame('after',1.9),'frame_timing_invalid'),
    (frame('before',.8),frame('after',2.1,token='x'),'frame_binding_mismatch'),
    (frame('before',.8),frame('after',2.1,hwnd=101),'frame_binding_mismatch'),
    (frame('before',.8),frame('after',2.1,pid=201),'frame_binding_mismatch'),
    (frame('after',.8),frame('after',2.1),'frame_context_mismatch'),
    (frame('before',.8),frame('after',2.1,project='Other.dwg'),'frame_context_mismatch'),
])
def test_unsafe_frame_pairs_do_not_become_steps(before,after,hold):
    c,_,spans,steps=corr()
    c.event(event(1,'begin'),before=before)
    c.event(event(2,'end'),after=after)
    assert c.pairs==1 and steps==[] and spans[-1]['correlation_hold']==hold


def test_stop_never_fabricates_command_end():
    c,_,spans,steps=corr()
    c.event(event(1,'begin'),before=frame('before',.9))
    c.interrupt('user_stop')
    assert c.incomplete==1 and c.pairs==0 and steps==[]
    assert spans[0]['end_event'] is None and spans[0]['status']=='incomplete'


def test_unmatched_end_and_nested_commands_not_mislabeled():
    c,_,spans,steps=corr()
    c.event(event(1,'end'))
    c.event(event(2,'begin'),before=frame('before',1.9))
    c.event(event(3,'begin','ZOOM'),before=frame('before',2.9))
    c.event(event(4,'end','ZOOM'),after=frame('after',4.1))
    c.event(event(5,'end'),after=frame('after',5.1))
    assert c.unmatched==1 and c.pairs==2 and steps==[]
    assert all(r['correlation_hold']=='nested_command_ambiguous' for r in spans)


@pytest.mark.parametrize('bad',[event(1,'begin',token='other'),event(1,'garbage'),event(1,'begin',name='SECRET'),event(1,'begin',at=float('nan'))])
def test_invalid_source_events_fail_closed(bad):
    c,events,_,_=corr()
    with pytest.raises(ValueError): c.event(bad)
    assert events==[]


def test_replay_and_mismatched_end_fail_closed():
    c,_,spans,steps=corr()
    c.event(event(1,'begin'))
    with pytest.raises(ValueError): c.event(event(1,'begin'))
    assert c.incomplete==1 and not steps
    c.event(event(2,'begin'))
    c.event(event(3,'end','MOVE'))
    assert c.unmatched==1 and c.incomplete==2


def test_repeated_commands_have_fresh_phase_and_sequence():
    c,_,_,steps=corr()
    for i in range(3):
        c.event(event(i*2+1,'begin'),before=frame('before',i*2+.9))
        c.event(event(i*2+2,'end'),after=frame('after',i*2+2.1))
    assert [r['demonstration']['sequence'] for r in steps]==[1,2,3]
    assert all(r['demonstration']['before']['phase']=='before' for r in steps)


def test_interactions_are_projected_and_bounded():
    c,_,_,_=corr(); c.event(event(1,'begin'))
    e=safe_input_event(application='autocad',kind='shortcut',shortcut='ctrl+s')
    assert not c.interaction(replace(e,raw_text='SECRET'),1.1)
    assert not c.interaction(replace(e,application='3dsmax'),1.1)
    assert not c.interaction(e,.5)
    for i in range(MAX_INTERACTIONS): assert c.interaction(e,1.1)
    assert not c.interaction(e,1.1)
    assert 'SECRET' not in json.dumps(c.stack[-1]['interactions'])


class Binding:
    hwnd,pid=100,200
    def __init__(self): self.enabled=True
    def active(self): return self.enabled
class Sub:
    token,project_hint='d','Demo.dwg'
    def __init__(self): self.binding=Binding()


def test_native_frame_uses_hwnd_not_desktop_bbox(tmp_path):
    from PIL import Image
    calls=[]
    def grab(**kwargs):
        calls.append(kwargs)
        return Image.new('RGB',(100,100))
    src=WindowEvidenceSource(Sub(),tmp_path/'frames',10,grabber=grab,clock=Clock())
    shot=src.capture('before')
    assert calls==[{'window':100,'include_layered_windows':False}]
    assert shot and Path(shot.observation.local_frame_ref).is_file()


def test_focus_change_during_capture_discards_pixels(tmp_path):
    from PIL import Image
    sub=Sub()
    def grab(**kwargs):
        sub.binding.enabled=False
        return Image.new('RGB',(100,100))
    src=WindowEvidenceSource(sub,tmp_path/'frames',10,grabber=grab,clock=Clock())
    assert src.capture('before') is None and not (tmp_path/'frames').exists()


def test_idle_and_invalid_consent_cannot_spawn_or_write(tmp_path):
    client=SemanticClient(tmp_path/'runs')
    assert client.poll()['state']=='IDLE' and client.process is None
    with pytest.raises(PermissionError): client.start(consent=False)
    assert not (tmp_path/'runs').exists()
    client.stop(); client.close()


def test_semantic_sources_have_no_command_or_input_injection():
    root=Path(__file__).resolve().parents[1]
    prohibited={'SendCommand','PostCommand','SendStringToExecute','SetVariable','AddLine','SendInput','SetForegroundWindow','mouse_event','keybd_event','CreateObject','EnsureDispatch','CoCreateInstance','GetKeyboardState','ToUnicode','ToUnicodeEx','GetString','GetPoint'}
    for path in root.glob('autocad_semantic*.py'):
        tree=ast.parse(path.read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node,ast.Call):
                assert getattr(node.func,'attr',getattr(node.func,'id','')) not in prohibited


def test_hidden_panel_stays_idle(tmp_path):
    import tkinter as tk
    from autocad_semantic_ui import SemanticPanel
    w=tk.Tk(); w.withdraw()
    client=SemanticClient(tmp_path/'idle')
    panel=SemanticPanel(w,client)
    try:
        w.update_idletasks()
        assert panel.heading.get()=='IDLE - NOT POLLING / NOT CAPTURING'
        assert str(panel.start_button['state'])=='disabled'
        assert client.process is None and not (tmp_path/'idle').exists()
    finally:
        panel.close()
