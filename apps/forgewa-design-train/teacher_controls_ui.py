"""Isolated Tkinter Teacher Mode panel. Opening it never starts observation."""
from __future__ import annotations

import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk

from teacher_controls import APPLICATIONS, D5_STATUS
from teacher_session_bridge import TeacherClient


def view_state(status: dict, consent: bool) -> dict:
    phase = status.get("state", "IDLE")
    alive = bool(status.get("worker_alive"))
    return {
        "start": consent is True and not alive,
        "pause": alive and phase in {"RUNNING", "PAUSED"},
        "stop": alive,
        "pause_text": "Resume" if phase == "PAUSED" else "Pause",
        "badge": {"IDLE": "NOT RECORDING", "RUNNING": "OBSERVING TITLES ONLY" if status.get("foreground") in APPLICATIONS else "WAITING FOR SELECTED APP",
                  "PAUSED": "PAUSED - NO NEW SAMPLES", "STARTING": "STARTING BOUNDED SESSION",
                  "COMPLETED": "AUTOMATICALLY STOPPED", "STOPPED": "STOPPED",
                  "INTERRUPTED": "INTERRUPTED - REVIEW EVIDENCE", "ERROR": "STOPPED WITH ERROR"}.get(phase, phase),
    }


class TeacherPanel:
    def __init__(self, window: tk.Tk, client: TeacherClient):
        self.window, self.client = window, client
        self.after_id = None
        self.closed = False
        window.title("ForgeWa Teacher Mode | Isolated candidate")
        window.geometry("1020x690")
        window.minsize(780, 570)
        style = ttk.Style(window)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("Title.TLabel", font=("Segoe UI", 23, "bold"))
        style.configure("Status.TLabel", font=("Segoe UI", 17, "bold"))
        frame = ttk.Frame(window, padding=22)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="ForgeWa  /  Teacher Mode", style="Title.TLabel").pack(anchor="w")
        ttk.Label(frame, text="ISOLATED CANDIDATE   |   AutoCAD + 3ds Max   |   No autonomous editing").pack(anchor="w", pady=(4, 16))
        self.badge = tk.StringVar(value="NOT RECORDING")
        ttk.Label(frame, textvariable=self.badge, style="Status.TLabel").pack(anchor="w")
        self.metrics = tk.StringVar(value="0 / 10 samples  |  Up to 10 seconds  |  No session started")
        ttk.Label(frame, textvariable=self.metrics).pack(anchor="w", pady=8)
        self.progress = ttk.Progressbar(frame, maximum=10)
        self.progress.pack(fill="x", pady=5)
        controls = ttk.Frame(frame)
        controls.pack(fill="x", pady=12)
        self.application = tk.StringVar(value="AutoCAD")
        self.app_select = ttk.Combobox(controls, textvariable=self.application, values=list(APPLICATIONS.values()), state="readonly", width=16)
        self.app_select.pack(side="left", padx=(0, 16))
        self.start_button = ttk.Button(controls, text="Start", command=self.start)
        self.start_button.pack(side="left", padx=4)
        self.pause_button = ttk.Button(controls, text="Pause", command=self.pause_resume)
        self.pause_button.pack(side="left", padx=4)
        self.stop_button = ttk.Button(controls, text="Stop", command=lambda: self.command("stop"))
        self.stop_button.pack(side="left", padx=4)
        self.consent = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, variable=self.consent, text="Allow title-context observation for this one bounded session.").pack(anchor="w")
        ttk.Label(frame, text="Pauses use the same 10-second budget. No screenshots, key logging, scene edits, uploads, or model training.", wraplength=920).pack(anchor="w", pady=6)
        ttk.Label(frame, text="D5: " + D5_STATUS).pack(anchor="w", pady=(0, 8))
        self.feedback = tk.StringVar(value="Start remains disabled until you provide consent. Each new session needs consent again.")
        ttk.Label(frame, textvariable=self.feedback, wraplength=920).pack(anchor="w", pady=6)
        ttk.Separator(frame).pack(fill="x", pady=10)
        ttk.Label(frame, text="Local session history (most recent 100)", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        columns = ("started", "app", "state", "samples", "project", "source")
        self.history = ttk.Treeview(frame, columns=columns, show="headings", height=6)
        for col, width in zip(columns, (190, 90, 120, 65, 290, 65)):
            self.history.heading(col, text=col.title())
            self.history.column(col, width=width, minwidth=50)
        self.history.pack(fill="both", expand=True, pady=7)
        self.history.bind("<<TreeviewSelect>>", self.show_detail)
        self.details = tk.Text(frame, height=5, wrap="word", state="disabled", font=("Consolas", 9))
        self.details.pack(fill="x")
        self.history_signature = None
        window.protocol("WM_DELETE_WINDOW", self.close)
        self.refresh()

    def start(self):
        try:
            app = next(key for key, value in APPLICATIONS.items() if value == self.application.get())
            self.client.start(app, consent=self.consent.get())
            self.consent.set(False)
            self.feedback.set("Switch to your selected application yourself. ForgeWa will not change window focus.")
        except Exception as exc:
            self.feedback.set("Start blocked: " + str(exc))

    def command(self, action):
        try:
            self.client.command(action)
        except Exception as exc:
            self.feedback.set("Control error: " + type(exc).__name__)

    def pause_resume(self):
        self.command("resume" if self.client.poll().get("state") == "PAUSED" else "pause")

    def refresh(self):
        if self.closed:
            return
        status = self.client.poll()
        view = view_state(status, self.consent.get())
        self.badge.set(view["badge"])
        self.start_button.configure(state="normal" if view["start"] else "disabled")
        self.pause_button.configure(state="normal" if view["pause"] else "disabled", text=view["pause_text"])
        self.stop_button.configure(state="normal" if view["stop"] else "disabled")
        self.app_select.configure(state="disabled" if status.get("worker_alive") else "readonly")
        self.metrics.set(f"{status.get('samples', 0)} / 10 samples  |  {status.get('remaining_seconds', 0):.1f}s remaining  |  {status.get('project_hint') or 'No selected-app title hint'}")
        self.progress["value"] = status.get("samples", 0)
        records = self.client.store.history()
        signature = json.dumps([records, status.get("worker_alive"), status.get("state")], sort_keys=True)
        if signature != self.history_signature:
            self.history_signature = signature
            self.history.delete(*self.history.get_children())
            for row in records:
                state = row.get("state")
                if state in {"RUNNING", "PAUSED"} and not (status.get("worker_alive") and row["run_id"] == status.get("run_id")):
                    state = "INTERRUPTED"
                self.history.insert("", "end", iid=row["run_id"], values=(row.get("started_at", ""), row.get("application", ""), state, row.get("samples", 0), row.get("project_hint") or "", row.get("source", "")))
        self.after_id = self.window.after(100, self.refresh)

    def show_detail(self, _event=None):
        selection = self.history.selection()
        if not selection:
            return
        try:
            record = self.client.store.detail(selection[0])
            text = json.dumps(record, indent=2, ensure_ascii=False)
        except Exception as exc:
            text = "Evidence unavailable: " + type(exc).__name__
        self.details.configure(state="normal")
        self.details.delete("1.0", "end")
        self.details.insert("1.0", text)
        self.details.configure(state="disabled")

    def close(self):
        self.closed = True
        if self.after_id:
            self.window.after_cancel(self.after_id)
        self.client.close()
        self.window.destroy()


def main():
    # No autorun, startup task, service registration, network binding or production integration.
    client = TeacherClient(Path(__file__).resolve().parent / "stores" / "training" / "teacher_controls")
    window = tk.Tk()
    TeacherPanel(window, client)
    window.mainloop()


if __name__ == "__main__":
    main()
