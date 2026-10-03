from pathlib import Path
import ast,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from demonstration_capture_ui import DemonstrationPanel

def test_withdrawn_panel_opens_idle_without_capture(tmp_path):
    import tkinter as tk
    w=tk.Tk(); w.withdraw(); p=DemonstrationPanel(w,tmp_path/"runs")
    try:
        w.update_idletasks()
        assert p.recorder is None and p.run_dir is None
        assert not (tmp_path/"runs").exists()
        assert p.status.get()=="IDLE — NOT CAPTURING"
        assert str(p.start["state"])=="disabled" and str(p.stop["state"])=="disabled"
    finally: p.close()

def test_ui_has_no_application_control_calls():
    root=Path(__file__).resolve().parents[1]
    tree=ast.parse((root/"demonstration_capture_ui.py").read_text())
    denied={"SendInput","SetForegroundWindow","ShowWindow","ShellExecuteW","mouse_event","keybd_event","Popen","system","exec","eval"}
    hits=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.Call):
            name=getattr(n.func,"attr",getattr(n.func,"id",""))
            if name in denied: hits.append(name)
    assert hits==[]
