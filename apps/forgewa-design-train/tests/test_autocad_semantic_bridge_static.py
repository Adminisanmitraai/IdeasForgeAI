from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
BRIDGE=ROOT/"autocad_semantic_bridge"/"ForgeWaSemanticBridge.cs"
MANIFEST=ROOT/"autocad_semantic_bridge"/"PackageContents.candidate.xml"

def source():
    return BRIDGE.read_text(encoding="utf-8")

def test_only_three_native_command_events_are_subscribed():
    text=source()
    assert text.count("CommandWillStart +=")==1
    assert text.count("CommandEnded +=")==1
    assert text.count("CommandCancelled +=")==1
    assert "CommandFailed +=" not in text
    assert "DocumentCreated +=" in text

def test_no_autocad_mutation_or_drawing_object_apis():
    text=source()
    forbidden=["SendStringToExecute","SendCommand","acedCommand","acedCmd","LockDocument",
        "Transaction","Database","Editor.","GetObject","OpenMode","SetSystemVariable",
        "GetSystemVariable","DocumentLock","CommandMethod","LispFunction"]
    assert [x for x in forbidden if x in text]==[]

def test_event_handler_payload_is_names_only():
    text=source()
    assert "args.GlobalCommandName" in text
    assert "BridgeRecord(id, phase, name)" in text
    forbidden=["args.ToString","Document.Name","Filename","FullName","CommandLine","Prompt"]
    assert [x for x in forbidden if x in text]==[]

def test_outbound_ipc_is_local_and_write_only():
    text=source()
    assert 'NamedPipeClientStream(\n                    ".", PipeName, PipeDirection.Out' in text
    assert "PipeDirection.InOut" not in text
    assert ".Read(" not in text and "ReadLine(" not in text
    assert "Connect(25)" in text
    assert "Capacity = 256" in text

def test_event_handler_does_not_perform_pipe_io_directly():
    text=source()
    emit=re.search(r"private void Emit\(.*?\n        \}",text,re.S).group(0)
    assert "TryEnqueue" in emit
    assert "NamedPipe" not in emit and ".Write(" not in emit and ".Connect(" not in emit

def test_manifest_is_candidate_only_for_autocad_2024():
    root=ET.parse(MANIFEST).getroot()
    runtime=root.find(".//RuntimeRequirements")
    assert runtime.attrib["SeriesMin"]=="R24.3" and runtime.attrib["SeriesMax"]=="R24.3"
    component=root.find(".//ComponentEntry")
    assert component.attrib["ModuleName"].endswith("ForgeWa.AutoCAD.Semantic.dll")

def test_no_real_binary_or_bundle_is_present():
    folder=BRIDGE.parent
    assert list(folder.glob("*.dll"))==[]
    assert list(folder.glob("*.bundle"))==[]
