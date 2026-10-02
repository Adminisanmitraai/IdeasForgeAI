from pathlib import Path
import ast
import json
import sys
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bounded_teacher_session as b
from foreground_observer import ObservationTracker
from observation import ForegroundContext, TeacherTimeline, correlate_project

@pytest.mark.parametrize('title,expected', [
    ('Autodesk AutoCAD 2024 - [Eco_Park_Update_25_09_2026.dwg]', 'Eco_Park_Update_25_09_2026.dwg'),
    ('Autodesk AutoCAD 2024 - [Eco Park.dwg*]', 'Eco Park.dwg'),
    ('Autodesk AutoCAD 2024 - [Eco Park.dwg]*', 'Eco Park.dwg'),
    (r'Autodesk AutoCAD 2024 - [D:\Projects\Eco Park.dwg]', 'Eco Park.dwg'),
    ('"Eco Park.dwg" - Autodesk AutoCAD 2024', 'Eco Park.dwg'),
    ('AutoCAD LT 2025 - [Plan.DXF]', 'Plan.DXF'),
    ('Eco Park [Rev 2].dwg - AutoCAD', 'Eco Park [Rev 2].dwg'),
    ('[Rev 2].dwg - AutoCAD', '[Rev 2].dwg'),
    ('Autodesk AutoCAD 2024 - [Plan.dwg] (Read Only)', 'Plan.dwg'),
    ('Autodesk AutoCAD 2024 - [Drawing1]', None),
    ('Plan.dwg.bak - AutoCAD', None),
    ('Autodesk AutoCAD 2024 - [A.dwg] - [B.dwg]', None),
    ('Autodesk AutoCAD 2024', None),
    ('', None),
])
def test_autocad_name_normalization(title, expected):
    assert correlate_project('autocad', title) == expected

@pytest.mark.parametrize('app,title,expected', [
    ('3dsmax', 'Stall.max - Autodesk 3ds Max', 'Stall.max'),
    ('d5', 'Lighting.drs - D5 Render', 'Lighting.drs'),
])
def test_other_application_hints_unchanged(app, title, expected):
    assert correlate_project(app, title) == expected

def cad(name='A.dwg'):
    return ForegroundContext(10, 20, 'Autodesk AutoCAD 2024 - ['+name+']', 'acad.exe')

def rows(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]

def test_close_active_session_is_idempotent(tmp_path):
    p = tmp_path/'timeline.jsonl'
    tracker = ObservationTracker(TeacherTimeline(p))
    start = tracker.observe(cad())[0]
    end = tracker.close()[0]
    assert end.kind == 'session_end' and end.end_reason == 'bounded_stop'
    assert end.session_id == start.session_id and end.project_ref == 'A.dwg'
    assert end.observe_only is True and end.autonomous_actions is False
    assert tracker.session is None and tracker.last_context is None
    assert tracker.close() == ()
    assert [r['kind'] for r in rows(p)] == ['session_start', 'session_end']

def test_close_idle_tracker_creates_nothing(tmp_path):
    p = tmp_path/'timeline.jsonl'
    assert ObservationTracker(TeacherTimeline(p)).close() == () and not p.exists()

@pytest.mark.parametrize('count', [1, 2, 10])
def test_sample_limit_closes_without_extra_foreground_read(monkeypatch, tmp_path, count):
    calls, sleeps = [], []
    def read():
        calls.append(1)
        return cad()
    monkeypatch.setattr(b, 'read_foreground_context', read)
    monkeypatch.setattr(b.time, 'sleep', sleeps.append)
    p = tmp_path/'timeline.jsonl'
    result = b.run_bounded_session(p, count, 1.0)
    assert len(calls) == count and len(sleeps) == count-1
    assert result['samples'] == count and result['active_session_closed'] is True
    assert result['final_event_kinds'] == ['session_end']
    assert result['stop_reason'] == 'bounded_stop'
    data = rows(p)
    assert [r['kind'] for r in data] == ['session_start', 'session_end']
    assert data[-1]['end_reason'] == 'bounded_stop'
    assert data[0]['session_id'] == data[-1]['session_id']

def test_app_exit_does_not_duplicate_end(monkeypatch, tmp_path):
    contexts = iter([cad(), ForegroundContext(30, 40, 'PRIVATE NOTES', 'notepad.exe')])
    monkeypatch.setattr(b, 'read_foreground_context', lambda: next(contexts))
    p = tmp_path/'timeline.jsonl'
    result = b.run_bounded_session(p, 2, 0)
    assert result['final_event_kinds'] == [] and result['active_session_closed'] is True
    assert [r['kind'] for r in rows(p)] == ['session_start', 'session_end']
    assert 'PRIVATE NOTES' not in p.read_text(encoding='utf-8')

def test_leave_return_has_two_balanced_sessions(monkeypatch, tmp_path):
    contexts = iter([cad(), ForegroundContext(30, 40, 'Notes', 'notepad.exe'), cad()])
    monkeypatch.setattr(b, 'read_foreground_context', lambda: next(contexts))
    p = tmp_path/'timeline.jsonl'
    result = b.run_bounded_session(p, 3, 0)
    data = rows(p)
    assert [r['kind'] for r in data] == ['session_start','session_end','session_start','session_end']
    assert data[0]['session_id'] == data[1]['session_id']
    assert data[2]['session_id'] == data[3]['session_id']
    assert data[0]['session_id'] != data[2]['session_id']
    assert result['active_session_closed'] is True

def test_final_event_uses_latest_drawing_context(monkeypatch, tmp_path):
    contexts = iter([cad('A.dwg'), cad('B.dwg')])
    monkeypatch.setattr(b, 'read_foreground_context', lambda: next(contexts))
    p = tmp_path/'timeline.jsonl'
    b.run_bounded_session(p, 2, 0)
    assert [r['project_ref'] for r in rows(p)] == ['A.dwg','B.dwg','B.dwg']

def test_read_error_closes_session_and_propagates(monkeypatch, tmp_path):
    contexts = iter([cad()])
    monkeypatch.setattr(b, 'read_foreground_context', lambda: next(contexts))
    p = tmp_path/'timeline.jsonl'
    with pytest.raises(StopIteration):
        b.run_bounded_session(p, 2, 0)
    assert [r['kind'] for r in rows(p)] == ['session_start','session_end']
    assert rows(p)[-1]['end_reason'] == 'observer_error'

@pytest.mark.parametrize('samples', [-1, 0, 11, True, 1.5, '2'])
def test_invalid_sample_limits_never_read(monkeypatch, tmp_path, samples):
    monkeypatch.setattr(b, 'read_foreground_context', lambda: pytest.fail('unexpected_foreground_read'))
    with pytest.raises(ValueError, match='samples_out_of_bounds'):
        b.run_bounded_session(tmp_path/'timeline.jsonl', samples, 0)

@pytest.mark.parametrize('interval', [-0.1, 1.1, float('nan'), float('inf'), -float('inf'), True, '1'])
def test_invalid_intervals_never_read(monkeypatch, tmp_path, interval):
    monkeypatch.setattr(b, 'read_foreground_context', lambda: pytest.fail('unexpected_foreground_read'))
    with pytest.raises(ValueError, match='interval_out_of_bounds'):
        b.run_bounded_session(tmp_path/'timeline.jsonl', 1, interval)

def test_observer_sources_have_no_control_imports_or_calls():
    root = Path(__file__).resolve().parents[1]
    allowed = {'__future__','dataclasses','datetime','hashlib','json','pathlib','re','typing','ctypes','observation','foreground_observer','math','time'}
    forbidden = {'SetForegroundWindow','ShowWindow','SendInput','mouse_event','keybd_event','ShellExecuteW','Popen','system','startfile','exec','eval','__import__'}
    for name in ('observation.py','foreground_observer.py','bounded_teacher_session.py'):
        tree = ast.parse((root/name).read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(item.name.split('.')[0] in allowed for item in node.names)
            if isinstance(node, ast.ImportFrom):
                assert node.module.split('.')[0] in allowed
            if isinstance(node, ast.Call):
                called = getattr(node.func, 'attr', getattr(node.func, 'id', ''))
                assert called not in forbidden
