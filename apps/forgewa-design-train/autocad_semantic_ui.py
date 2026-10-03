"""Isolated AutoCAD semantic observer UI. Imports and opening do not subscribe."""
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from autocad_semantic_worker import SemanticClient


class SemanticPanel:
    def __init__(self, window, client):
        self.window, self.client, self.after_id = window, client, None
        window.title('ForgeWa Semantic Command Capture | AutoCAD | Isolated')
        window.geometry('960x520')
        frame = ttk.Frame(window,padding=22)
        frame.pack(fill='both',expand=True)
        ttk.Label(frame,text='ForgeWa / AutoCAD Semantic Command Capture',font=('Segoe UI',20,'bold')).pack(anchor='w')
        ttk.Label(frame,text='READ-ONLY OBSERVER  |  Existing AutoCAD 2024 document  |  D5 deferred').pack(anchor='w',pady=8)
        self.heading = tk.StringVar(value='IDLE - NOT SUBSCRIBED / NOT CAPTURING')
        self.metrics = tk.StringVar(value='0 events | 0 paired commands | 0 visual steps')
        ttk.Label(frame,textvariable=self.heading,font=('Segoe UI',14,'bold')).pack(anchor='w',pady=12)
        ttk.Label(frame,textvariable=self.metrics).pack(anchor='w')
        self.consent = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame,variable=self.consent,text='Allow one 10-second run: command names, window frames and limited mouse/Ctrl-shortcut events.').pack(anchor='w',pady=14)
        buttons = ttk.Frame(frame)
        buttons.pack(anchor='w')
        self.start_button = ttk.Button(buttons,text='Start',command=self.start)
        self.start_button.pack(side='left',padx=(0,10))
        self.stop_button = ttk.Button(buttons,text='Stop',command=self.client.stop)
        self.stop_button.pack(side='left')
        self.note = tk.StringVar(value='No automatic recording. Open a saved drawing yourself, then Start and return to AutoCAD.')
        ttk.Label(frame,textvariable=self.note,wraplength=900).pack(anchor='w',pady=14)
        ttk.Label(frame,text='First trial: run REGEN yourself in AutoCAD. A command must begin and end during this run.',wraplength=900).pack(anchor='w')
        ttk.Label(frame,text='Command payloads contain names only, not arguments or typed text. Images can contain visible drawing/UI text.',wraplength=900).pack(anchor='w',pady=8)
        ttk.Label(frame,text='No command injection, drawing edits by ForgeWa, plugin loading, uploads, or model training.\nStop ends this listener, never AutoCAD. An end event is not proof of successful editing.',wraplength=900).pack(anchor='w')
        window.protocol('WM_DELETE_WINDOW',self.close)
        self.refresh()

    def start(self):
        try:
            self.client.start(consent=self.consent.get())
            self.consent.set(False)
            self.note.set('Return to AutoCAD yourself. Run REGEN, or perform a simple command in a test drawing. The listener stops automatically.')
        except Exception as exc:
            self.note.set('Start blocked: '+type(exc).__name__)

    def refresh(self):
        status = self.client.poll()
        alive = status.get('worker_alive',False)
        phase = status['state']
        self.start_button.configure(state='normal' if self.consent.get() and not alive else 'disabled')
        self.stop_button.configure(state='normal' if alive else 'disabled')
        self.heading.set({'IDLE':'IDLE - NOT SUBSCRIBED / NOT CAPTURING','STARTING':'CONNECTING TO EXISTING AUTOCAD',
            'ARMED':'ARMED - SWITCH TO AUTOCAD','OBSERVING':'OBSERVING COMMAND NAMES + WINDOW FRAMES',
            'WAITING_FOR_AUTOCAD':'WAITING FOR SELECTED AUTOCAD WINDOW','COMPLETED':'AUTOMATICALLY STOPPED',
            'STOPPED':'STOPPED BY USER','ERROR':'STOPPED WITH ERROR','INTERRUPTED':'INTERRUPTED - NOT CERTIFIED'}.get(phase,phase))
        self.metrics.set(f"{status.get('commands',0)} events | {status.get('pairs',0)} paired commands | {status.get('steps',0)} visual steps | {status.get('remaining_seconds',0):.1f}s remaining")
        if phase in {'COMPLETED','STOPPED','ERROR','INTERRUPTED'}:
            self.note.set(f"Reason: {status.get('stop_reason')} | Unsubscribe confirmed: {status.get('subscription_detached',False)}\nEvidence: {status.get('run_dir','No run')}\nA zero-pair run does not certify command capture.")
        self.after_id = self.window.after(100,self.refresh)

    def close(self):
        if self.after_id:
            self.window.after_cancel(self.after_id)
        self.client.close()
        self.window.destroy()


def main():
    root = Path(__file__).resolve().parent/'stores'/'training'/'semantic_commands'
    window = tk.Tk()
    SemanticPanel(window,SemanticClient(root))
    window.mainloop()


if __name__ == '__main__':
    main()
