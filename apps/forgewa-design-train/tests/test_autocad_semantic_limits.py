from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from autocad_semantic_native import WindowEvidenceSource, MAX_FRAMES
from test_autocad_semantic import corr, event, frame, Sub, Clock


def test_dash_command_keeps_true_span_without_fabricating_legacy_step():
    c,events,spans,steps=corr()
    c.event(event(1,'begin','-LAYER'),before=frame('before',.8))
    c.event(event(2,'end','-LAYER'),after=frame('after',2.1))
    assert c.pairs==1 and steps==[]
    assert spans[0]['command']=='-LAYER'
    assert spans[0]['correlation_hold']=='command_identifier_outside_legacy_step_contract'
    assert not spans[0]['training_eligible']


@pytest.mark.parametrize('mode',['deadline','unselected','frame_limit'])
def test_frame_boundary_does_not_invoke_capture(tmp_path,mode):
    clock=Clock(); sub=Sub(); calls=[]
    source=WindowEvidenceSource(sub,tmp_path/'frames',10,clock=clock,grabber=lambda **kw:calls.append(kw))
    if mode=='deadline': clock.now=10
    if mode=='unselected': sub.binding.enabled=False
    if mode=='frame_limit': source.count=MAX_FRAMES
    assert source.capture('before') is None and calls==[]
    assert not (tmp_path/'frames').exists()


def test_invalid_frame_phase_is_rejected_before_capture(tmp_path):
    calls=[]
    source=WindowEvidenceSource(Sub(),tmp_path/'frames',10,clock=Clock(),grabber=lambda **kw:calls.append(kw))
    with pytest.raises(ValueError): source.capture('arbitrary')
    assert calls==[] and not (tmp_path/'frames').exists()
