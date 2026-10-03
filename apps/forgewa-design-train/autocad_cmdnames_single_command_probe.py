"""R3-R2-R1B single-command CMDNAMES transition probe.

No frames, input observation, command injection, or callbacks. The user manually
starts and ends LINE. The probe records only allowlisted semantic command names.
"""
from __future__ import annotations
from dataclasses import asdict
import json
from pathlib import Path
import time
from autocad_semantic_native import AutoCADCmdNamesPoller

PROBE_SECONDS=15.0
TARGET_COMMAND="LINE"
OBSERVE_ONLY=True
FRAMES_ENABLED=False
INTERACTIONS_ENABLED=False

def run_probe(output_path,*,consent,source_factory=AutoCADCmdNamesPoller,clock=time.monotonic,sleep=time.sleep):
    if consent is not True: raise PermissionError("explicit_single_command_consent_required")
    started=clock(); deadline=started+PROBE_SECONDS; source=None; events=[]; error=None; released=False
    try:
        source=source_factory(deadline=deadline,consent=True,clock=clock)
        while clock()<deadline:
            rows=source.poll()
            events.extend(asdict(row) for row in rows)
            phases=[(r["phase"],r["name"]) for r in events]
            if phases==[("begin",TARGET_COMMAND),("end",TARGET_COMMAND)]:
                break
            if len(events)>2 or any(r["name"]!=TARGET_COMMAND for r in events):
                break
            sleep(.03)
    except Exception as exc:
        error=type(exc).__name__
    finally:
        if source is not None:
            try: released=source.close()
            except Exception as exc: error=error or type(exc).__name__
    polls=getattr(source,"polls",0) if source else 0
    gaps=getattr(getattr(source,"detector",None),"gaps",0) if source else 0
    phases=[(r["phase"],r["name"]) for r in events]
    passed=(error is None and released and polls>0 and gaps==0 and
            phases==[("begin",TARGET_COMMAND),("end",TARGET_COMMAND)])
    result={"schema":"forgewa.cmdnames-single-command-probe.v1","status":"PASS" if passed else "FAIL",
        "target_command":TARGET_COMMAND,"events":events,"event_count":len(events),
        "poll_count":polls,"binding_gaps":gaps,"source_released":released,"error_type":error,
        "frames_enabled":False,"interactions_enabled":False,"command_injection":False,
        "raw_text_recording":False,"autonomous_actions":False,"production_activation":False,
        "binding":getattr(source,"metadata",None) if source else None}
    Path(output_path).write_text(json.dumps(result,indent=2),encoding="utf-8")
    return result
