"""R3-R2-R1A: no-command live baseline probe.

This module never captures frames, polls mouse/keyboard state, or executes an
AutoCAD command. It reads CMDNAMES only through AutoCADCmdNamesPoller.
"""
from __future__ import annotations
from dataclasses import asdict
import json
from pathlib import Path
import time
from autocad_semantic_native import AutoCADCmdNamesPoller

PROBE_SECONDS=5.0
OBSERVE_ONLY=True
AUTONOMOUS_ACTIONS=False
FRAMES_ENABLED=False
INTERACTIONS_ENABLED=False


def run_probe(output_path:str|Path, *, consent:bool, source_factory=AutoCADCmdNamesPoller,
              clock=time.monotonic, sleep=time.sleep):
    if consent is not True:
        raise PermissionError('explicit_baseline_probe_consent_required')
    started=clock(); deadline=started+PROBE_SECONDS
    source=None; events=[]; error=None; released=False
    try:
        source=source_factory(deadline=deadline,consent=True,clock=clock)
        while clock()<deadline:
            rows=source.poll()
            events.extend(asdict(row) for row in rows)
            sleep(0.03)
    except Exception as exc:
        error=type(exc).__name__
    finally:
        if source is not None:
            try: released=source.close()
            except Exception as exc:
                error=error or type(exc).__name__
    result={'schema':'forgewa.cmdnames-baseline-probe.v1',
        'status':'PASS' if error is None and released and len(events)==0 else 'FAIL',
        'error_type':error,'events':events,'event_count':len(events),
        'poll_count':getattr(source,'polls',0) if source else 0,
        'source_released':released,'observe_only':True,'autonomous_actions':False,
        'frames_enabled':False,'interactions_enabled':False,'command_injection':False,
        'raw_text_recording':False,'production_activation':False,
        'binding':getattr(source,'metadata',None) if source else None}
    Path(output_path).write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result
