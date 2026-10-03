"""R1B-R2 LINE transition recertification over callback-free CMDNAMES polling."""
from __future__ import annotations
from dataclasses import asdict
import json,time
from pathlib import Path
from autocad_semantic_native import AutoCADCmdNamesPoller

PROBE_SECONDS=20.0
TARGET="LINE"

def run_probe(output_path,*,consent,source_factory=AutoCADCmdNamesPoller,clock=time.monotonic,sleep=time.sleep):
    if consent is not True: raise PermissionError("explicit_line_recert_consent_required")
    deadline=clock()+PROBE_SECONDS; source=None; events=[]; error=None; released=False
    try:
        source=source_factory(deadline=deadline,consent=True,clock=clock)
        while clock()<deadline:
            events.extend(asdict(x) for x in source.poll())
            pairs=[(x["phase"],x["name"]) for x in events]
            if pairs==[("begin",TARGET),("end",TARGET)]: break
            if len(events)>2 or any(x["name"]!=TARGET for x in events): break
            sleep(.03)
    except Exception as exc:
        error=type(exc).__name__
    finally:
        if source:
            try: released=source.close()
            except Exception as exc:error=error or type(exc).__name__
    polls=getattr(source,"polls",0) if source else 0
    successful=getattr(source,"successful_polls",0) if source else 0
    fg=getattr(source,"foreground_gaps",0) if source else 0
    missing=getattr(source,"com_missing_samples",0) if source else 0
    pairs=[(x["phase"],x["name"]) for x in events]
    balanced=pairs==[("begin",TARGET),("end",TARGET)]
    missing_only=(missing>0 and len(events)==0)
    acceptable=(error is None and released and polls>0 and successful>0 and fg==0 and (balanced or missing_only))
    outcome="BALANCED_LINE" if balanced else "TRANSIENT_MISSING_NO_EVENTS" if missing_only else "UNACCEPTABLE"
    result={"schema":"forgewa.cmdnames-line-recert.v1","status":"PASS" if acceptable else "FAIL",
        "outcome":outcome,"target_command":TARGET,"events":events,"event_count":len(events),
        "poll_count":polls,"successful_polls":successful,"foreground_gaps":fg,
        "com_missing_samples":missing,"last_com_category":getattr(source,"last_com_category",None) if source else None,
        "detector_resync_gaps":getattr(getattr(source,"detector",None),"gaps",0) if source else 0,
        "source_released":released,"error_type":error,"frames_enabled":False,"interactions_enabled":False,
        "command_injection":False,"raw_text_recording":False,"autonomous_actions":False,
        "production_activation":False,"binding":getattr(source,"metadata",None) if source else None}
    Path(output_path).write_text(json.dumps(result,indent=2),encoding="utf-8")
    return result
