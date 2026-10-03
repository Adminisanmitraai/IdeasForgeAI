"""R1B-R2-R2 binding-reason diagnostic. No semantic inference or CMDNAMES value storage."""
from __future__ import annotations
import json,time
from pathlib import Path
from autocad_active_command_identity_probe import ActiveCommandIdentityProbe
from autocad_semantic_native import classify_com_exception

PROBE_SECONDS=20.0
SAMPLE_INTERVAL_SECONDS=0.10

class BindingReasonProbe(ActiveCommandIdentityProbe):
    def sample(self):
        state=self.binding.binding_state()
        outcome="not_foreground_owned"
        if state["foreground_owned"]:
            try:
                self.doc.GetVariable("CMDNAMES")
                outcome="success"
            except Exception as exc:
                category=classify_com_exception(exc)
                outcome=category if category in {"call_rejected","retry_later"} else "other_com"
        return {"t":round(self.clock(),6),
            "foreground_hwnd":state["foreground_hwnd"],"foreground_pid":state["foreground_pid"],
            "foreground_owned":state["foreground_owned"],
            "main_hwnd":state["main_hwnd"],"main_pid":state["main_pid"],
            "main_pid_integrity":state["main_pid_integrity"],
            "document_hwnd":state["document_hwnd"],"document_valid":state["document_valid"],
            "document_pid":state["document_pid"],"document_pid_integrity":state["document_pid_integrity"],
            "active_equivalent":state["foreground_owned"] and state["main_pid_integrity"] and
                state["document_valid"] and state["document_pid_integrity"],
            "read_outcome":outcome}

def run_probe(output_path,*,consent,probe_factory=BindingReasonProbe,clock=time.monotonic,sleep=time.sleep):
    probe=None;rows=[];error=None;released=False;deadline=clock()+PROBE_SECONDS
    try:
        probe=probe_factory(consent=consent,clock=clock)
        while clock()<deadline:
            rows.append(probe.sample());sleep(SAMPLE_INTERVAL_SECONDS)
    except Exception as exc:error=type(exc).__name__
    finally:
        if probe:
            try:released=probe.close()
            except Exception as exc:error=error or type(exc).__name__
    false_counts={k:sum(not bool(row[k]) for row in rows) for k in
        ("foreground_owned","main_pid_integrity","document_valid","document_pid_integrity","active_equivalent")}
    outcomes={}
    for row in rows:outcomes[row["read_outcome"]]=outcomes.get(row["read_outcome"],0)+1
    result={"schema":"forgewa.binding-reason-diagnostic.v1",
        "status":"COMPLETE" if rows and released and error is None else "ERROR",
        "samples":rows,"sample_count":len(rows),"false_counts":false_counts,
        "outcome_counts":outcomes,"source_released":released,"error_type":error,
        "semantic_inference":False,"cmdnames_value_recorded":False,"frames_enabled":False,
        "interactions_enabled":False,"command_injection":False,"autonomous_actions":False,
        "production_activation":False,"bound_pid":getattr(probe,"bound_pid",None)}
    Path(output_path).write_text(json.dumps(result,indent=2),encoding="utf-8")
    return result
