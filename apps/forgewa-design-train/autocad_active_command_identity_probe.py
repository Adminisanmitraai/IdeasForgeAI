"""R1B-R2-R1 active-command identity diagnostic.

Records only time, foreground HWND/PID/process image, and sanitized CMDNAMES read
outcome. The CMDNAMES value is deliberately discarded. No semantic inference.
"""
from __future__ import annotations
import json,time,uuid
from pathlib import Path
from autocad_semantic_native import WindowsBinding,classify_com_exception

PROBE_SECONDS=20.0
SAMPLE_INTERVAL_SECONDS=0.10

class ActiveCommandIdentityProbe:
    def __init__(self,*,consent,clock=time.monotonic,active_object=None,dispatcher=None,binding_factory=WindowsBinding):
        if consent is not True: raise PermissionError("explicit_identity_diagnostic_consent_required")
        self.clock=clock; self.pc=None; self.initialized=False; self.app=self.doc=None
        if active_object is None or dispatcher is None:
            import pythoncom
            from win32com.client import dynamic
            self.pc=pythoncom; pythoncom.CoInitialize(); self.initialized=True
            active_object=active_object or (lambda:pythoncom.GetActiveObject("AutoCAD.Application").QueryInterface(pythoncom.IID_IDispatch))
            dispatcher=dispatcher or dynamic.Dispatch
        try:
            self.app=dispatcher(active_object())
            if not str(self.app.Version).startswith("24.3"):raise RuntimeError("uncertified_autocad_version")
            self.doc=self.app.ActiveDocument
            self.binding=binding_factory(self.app.HWND,self.doc.HWND)
            self.bound_pid=self.binding.pid
            self.token="identity_"+uuid.uuid4().hex
        except Exception:
            self.close();raise

    def sample(self):
        identity=self.binding.foreground_identity()
        outcome="not_bound_foreground"
        if identity["same_bound_pid"]:
            try:
                self.doc.GetVariable("CMDNAMES")
                outcome="success"
            except Exception as exc:
                category=classify_com_exception(exc)
                outcome=category if category in {"call_rejected","retry_later"} else "other_com"
        return {"t":round(self.clock(),6),"foreground_hwnd":identity["foreground_hwnd"],
            "foreground_pid":identity["foreground_pid"],"foreground_image":identity["foreground_image"],
            "same_bound_pid":identity["same_bound_pid"],"read_outcome":outcome}

    def close(self):
        self.doc=self.app=None
        if self.initialized:
            self.pc.CoUninitialize();self.initialized=False
        return True

def run_probe(output_path,*,consent,probe_factory=ActiveCommandIdentityProbe,clock=time.monotonic,sleep=time.sleep):
    probe=None;rows=[];error=None;released=False;deadline=clock()+PROBE_SECONDS
    try:
        probe=probe_factory(consent=consent,clock=clock)
        while clock()<deadline:
            rows.append(probe.sample());sleep(SAMPLE_INTERVAL_SECONDS)
    except Exception as exc:
        error=type(exc).__name__
    finally:
        if probe:
            try:released=probe.close()
            except Exception as exc:error=error or type(exc).__name__
    counts={}
    for row in rows:counts[row["read_outcome"]]=counts.get(row["read_outcome"],0)+1
    result={"schema":"forgewa.active-command-identity-diagnostic.v1",
        "status":"COMPLETE" if error is None and released and rows else "ERROR",
        "samples":rows,"sample_count":len(rows),"outcome_counts":counts,
        "source_released":released,"error_type":error,
        "semantic_inference":False,"cmdnames_value_recorded":False,
        "frames_enabled":False,"interactions_enabled":False,"command_injection":False,
        "raw_text_recording":False,"autonomous_actions":False,"production_activation":False,
        "bound_pid":getattr(probe,"bound_pid",None)}
    Path(output_path).write_text(json.dumps(result,indent=2),encoding="utf-8")
    return result
