"""R3-R1 isolated live panel. Opening is idle; only user Start arms selected-app capture."""
from __future__ import annotations
from dataclasses import asdict
from datetime import datetime,timezone
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk
import uuid
from demonstration_recorder import BoundedDemonstrationRecorder
from demonstration_sources import SelectedWindowFrameSource,SafeWindowsInputPoller

def utc_now(): return datetime.now(timezone.utc).isoformat()

class DemonstrationPanel:
    def __init__(self,window:tk.Tk,root:Path):
        self.window=window; self.root=root; self.recorder=None; self.run_dir=None; self.after_id=None
        window.title("ForgeWa Demonstration Capture | AutoCAD | Isolated")
        window.geometry("860x430")
        frame=ttk.Frame(window,padding=22); frame.pack(fill="both",expand=True)
        ttk.Label(frame,text="ForgeWa / AutoCAD Demonstration Capture",font=("Segoe UI",20,"bold")).pack(anchor="w")
        ttk.Label(frame,text="OBSERVATION ONLY  |  AutoCAD first  |  D5 deferred to RTX machine").pack(anchor="w",pady=(3,14))
        self.status=tk.StringVar(value="IDLE — NOT CAPTURING")
        ttk.Label(frame,textvariable=self.status,font=("Segoe UI",15,"bold")).pack(anchor="w")
        self.metrics=tk.StringVar(value="0 steps | 0.0s remaining | No run")
        ttk.Label(frame,textvariable=self.metrics).pack(anchor="w",pady=8)
        self.consent=tk.BooleanVar(value=False)
        ttk.Checkbutton(frame,variable=self.consent,text="Allow one bounded AutoCAD demonstration capture (window frames + safe mouse/shortcut events).").pack(anchor="w",pady=5)
        buttons=ttk.Frame(frame); buttons.pack(anchor="w",pady=10)
        self.start=ttk.Button(buttons,text="Start",command=self.start_run); self.start.pack(side="left",padx=(0,8))
        self.stop=ttk.Button(buttons,text="Stop",command=self.stop_run); self.stop.pack(side="left")
        self.note=tk.StringVar(value="Opening this panel does not capture anything. Switch to AutoCAD yourself after Start.")
        ttk.Label(frame,textvariable=self.note,wraplength=800).pack(anchor="w",pady=8)
        ttk.Label(frame,text="Privacy: no raw typed text, no global key hook, no screenshots outside selected AutoCAD foreground, no input injection.",wraplength=800).pack(anchor="w")
        ttk.Label(frame,text="Semantic AutoCAD command-name feed is contract-ready but not live-connected in this panel.",wraplength=800).pack(anchor="w",pady=(4,0))
        self._refresh_buttons(); window.protocol("WM_DELETE_WINDOW",self.close); self.refresh()

    def _refresh_buttons(self):
        running=bool(self.recorder and self.recorder.state=="RUNNING")
        self.start.configure(state="normal" if self.consent.get() and not running else "disabled")
        self.stop.configure(state="normal" if running else "disabled")

    def start_run(self):
        if not self.consent.get() or (self.recorder and self.recorder.state=="RUNNING"): return
        self.run_dir=self.root/("run_"+uuid.uuid4().hex); frames=self.run_dir/"frames"; self.run_dir.mkdir(parents=True)
        source=SelectedWindowFrameSource("autocad",frames)
        actions=SafeWindowsInputPoller("autocad")
        self.recorder=BoundedDemonstrationRecorder("autocad",source,actions,self.run_dir/"steps.jsonl")
        self.recorder.start(consent=True,session_id=self.run_dir.name)
        self.consent.set(False); self.note.set("Capture armed. Switch to AutoCAD yourself; it will stop automatically by the bounded limit.")
        self._write_summary("running"); self._refresh_buttons()

    def _write_summary(self,phase):
        if not self.run_dir or not self.recorder: return
        data={**self.recorder.snapshot(),"phase":phase,"run_id":self.run_dir.name,"updated_at":utc_now(),
              "raw_keystrokes":False,"input_injection":False,"semantic_command_live_connected":False}
        (self.run_dir/"summary.json").write_text(json.dumps(data,sort_keys=True),encoding="utf-8")

    def stop_run(self):
        if self.recorder and self.recorder.state=="RUNNING":
            self.recorder.stop("user_stop"); self._write_summary("stopped")
            self.note.set("Stopped by user. No application was closed or modified.")
        self._refresh_buttons()

    def refresh(self):
        if self.recorder:
            if self.recorder.state=="RUNNING":
                try: self.recorder.tick()
                except Exception as exc:
                    self.recorder.stop("source_error"); self.note.set("Capture stopped with source error: "+type(exc).__name__)
                self._write_summary("running" if self.recorder.state=="RUNNING" else "final")
            snap=self.recorder.snapshot()
            self.status.set({"RUNNING":"CAPTURING — SELECTED AUTOCAD ONLY","STOPPED":"STOPPED","COMPLETED":"AUTOMATICALLY STOPPED","ERROR":"STOPPED WITH ERROR"}.get(snap["state"],snap["state"]))
            self.metrics.set(f'{snap["steps"]} steps | {snap["remaining_seconds"]:.1f}s remaining | {self.run_dir.name if self.run_dir else "No run"}')
        self._refresh_buttons()
        self.after_id=self.window.after(50,self.refresh)

    def close(self):
        if self.after_id: self.window.after_cancel(self.after_id)
        if self.recorder and self.recorder.state=="RUNNING":
            self.recorder.stop("user_stop"); self._write_summary("window_closed")
        self.window.destroy()

def main():
    root=Path(__file__).resolve().parent/"stores"/"training"/"demonstrations"
    window=tk.Tk(); panel=DemonstrationPanel(window,root)
    panel.consent.trace_add("write",lambda *_:panel._refresh_buttons())
    window.mainloop()

if __name__=="__main__": main()
