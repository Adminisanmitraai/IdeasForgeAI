from pathlib import Path
import re

SOURCE=Path(__file__).resolve().parents[1]/"autocad-plugin"/"ForgeWaCommandObserver.cs"

def text(): return SOURCE.read_text(encoding="utf-8")

def test_uses_only_command_lifecycle_events():
    s=text()
    for name in ["CommandWillStart","CommandEnded","CommandCancelled","CommandFailed","GlobalCommandName"]:
        assert name in s

def test_loading_does_not_arm():
    s=text()
    init=s[s.index("public void Initialize()"):s.index("public void Terminate()")]
    assert "Armed = true" not in init

def test_no_editor_prompt_or_command_execution_api():
    s=text()
    denied=["SendStringToExecute","Editor.","GetString(","GetPoint(","CommandAsync","acedCommand","SendCommand",
            "TransactionManager","OpenMode.ForWrite","AppendEntity","DatabaseServices","SetSystemVariable"]
    assert [x for x in denied if x in s]==[]

def test_only_name_and_lifecycle_fields_are_written():
    s=text()
    assert '\\"command_name\\":' in s and '\\"phase\\":' in s and '\\"drawing_hint\\":' in s
    for bad in ["argument","prompt_text","typed_text","coordinates"]:
        assert bad not in s.lower()

def test_observer_controls_are_namespaced_and_nonediting():
    s=text()
    assert 'CommandMethod("FORGEWA_OBSERVE_START"' in s
    assert 'CommandMethod("FORGEWA_OBSERVE_STOP"' in s
    assert "Armed = true" in s and "Armed = false" in s

def test_sanitizer_is_restricted_identifier():
    assert '^[A-Z][A-Z0-9_.-]{0,63}$' in text()
