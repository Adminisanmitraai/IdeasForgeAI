"""R1B-R1 no-command live ownership/busy diagnostic. CMDNAMES only."""
from __future__ import annotations
import json,time
from pathlib import Path
from autocad_semantic_native import AutoCADCmdNamesPoller

PROBE_SECONDS=8.0

def run_probe(output_path,*,consent,source_factory=AutoCADCmdNamesPoller,clock=time.monotonic,sleep=time.sleep):
    if consent is not True: raise PermissionError("explicit_diagnostic_consent_required")
    deadline=clock()+PROBE_SECONDS; source=None; events=[]; error=None; released=False
    try:
        source=source_factory(deadline=deadline,consent=True,clock=clock)
        while clock()<deadline:
            events.extend(source.poll())
            sleep(.03)
    except Exception as exc:
        error=type(exc).__name__
    finally:
        if source:
            try: released=source.close()
            except Exception as exc: error=error or type(exc).__name__
    polls=getattr(source,"polls",0) if source else 0
    successful=getattr(source,"successful_polls",0) if source else 0
    foreground_gaps=getattr(source,"foreground_gaps",0) if source else 0
    missing=getattr(source,"com_missing_samples",0) if source else 0
    passed=(error is None and released and polls>0 and successful>0 and
            foreground_gaps==0 and len(events)==0)
    result={"schema":"forgewa.cmdnames-ownership-busy-diagnostic.v1",
        "status":"PASS" if passed else "FAIL","event_count":len(events),
        "poll_count":polls,"successful_polls":successful,
        "foreground_gaps":foreground_gaps,"com_missing_samples":missing,
        "last_com_category":getattr(source,"last_com_category",None) if source else None,
        "detector_resync_gaps":getattr(getattr(source,"detector",None),"gaps",0) if source else 0,
        "source_released":released,"error_type":error,"frames_enabled":False,
        "interactions_enabled":False,"command_injection":False,"raw_text_recording":False,
        "autonomous_actions":False,"production_activation":False,
        "binding":getattr(source,"metadata",None) if source else None}
    Path(output_path).write_text(json.dumps(result,indent=2),encoding="utf-8")
    return result
