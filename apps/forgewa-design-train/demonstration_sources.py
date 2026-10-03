"""R3-R1 Windows source adapters. Read-only, selected-app-only, no low-level keyboard hook."""
from __future__ import annotations
import ctypes
from ctypes import wintypes
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Callable
from demonstration_capture import safe_input_event, screen_observation
from foreground_observer import read_foreground_context
from observation import correlate_project, detect_application

OBSERVE_ONLY=True
AUTONOMOUS_ACTIONS=False
SELECTED_APP_ONLY=True
RAW_KEYSTROKES=False
INPUT_INJECTION=False
APPROVED_KEYS={0x53:"s",0x5A:"z",0x59:"y",0x43:"c",0x56:"v",0x58:"x",0x41:"a",
               0x1B:"esc",0x0D:"enter",0x09:"tab",**{0x70+i:f"f{i+1}" for i in range(12)}}
MODIFIERS=((0x11,"ctrl"),(0x12,"alt"),(0x10,"shift"))
MOUSE=((0x01,"left"),(0x02,"right"),(0x04,"middle"))

@dataclass(frozen=True)
class SelectedWindow:
    hwnd:int; pid:int; title:str; application:str; project_hint:str|None
    left:int; top:int; right:int; bottom:int

def selected_foreground(application:str, reader:Callable=read_foreground_context)->SelectedWindow|None:
    ctx=reader()
    if detect_application(ctx.executable)!=application:
        return None
    rect=wintypes.RECT()
    if not ctypes.windll.user32.GetWindowRect(ctx.hwnd,ctypes.byref(rect)):
        return None
    if rect.right<=rect.left or rect.bottom<=rect.top:
        return None
    return SelectedWindow(ctx.hwnd,ctx.pid,ctx.title,application,correlate_project(application,ctx.title),
                          rect.left,rect.top,rect.right,rect.bottom)

class SelectedWindowFrameSource:
    def __init__(self,application:str,frame_root:str|Path,reader:Callable=read_foreground_context,grabber=None):
        if application not in {"autocad","3dsmax"}: raise ValueError("unsupported_application")
        self.application=application; self.root=Path(frame_root).resolve(); self.reader=reader; self.grabber=grabber
        self.sequence=0
    def capture(self,phase:str):
        window=selected_foreground(self.application,self.reader)
        if window is None: return None
        grab=self.grabber
        if grab is None:
            from PIL import ImageGrab
            grab=lambda bbox: ImageGrab.grab(bbox=bbox,all_screens=True)
        image=grab((window.left,window.top,window.right,window.bottom))
        self.sequence+=1; self.root.mkdir(parents=True,exist_ok=True)
        path=self.root/f"{self.sequence:04d}_{phase}.png"
        image.save(path,format="PNG")
        data=path.read_bytes(); width,height=image.size
        return screen_observation(phase=phase,application=self.application,project_hint=window.project_hint,
                                  frame_bytes=data,width=width,height=height,local_frame_ref=str(path))

class SafeWindowsInputPoller:
    """Edge detector only. It never calls SetWindowsHookEx, GetKeyboardState, ToUnicode or SendInput."""
    def __init__(self,application:str,reader:Callable=read_foreground_context,key_state=None,cursor=None):
        self.application=application; self.reader=reader
        self.key_state=key_state or ctypes.windll.user32.GetAsyncKeyState
        self.cursor=cursor or self._cursor
        self.previous={}
    @staticmethod
    def _cursor():
        point=wintypes.POINT(); ctypes.windll.user32.GetCursorPos(ctypes.byref(point)); return point.x,point.y
    def _down(self,vk:int)->bool: return bool(self.key_state(vk)&0x8000)
    def poll(self):
        window=selected_foreground(self.application,self.reader)
        if window is None:
            self.previous.clear(); return ()
        events=[]
        mods=[name for vk,name in MODIFIERS if self._down(vk)]
        for vk,name in APPROVED_KEYS.items():
            down=self._down(vk); prior=self.previous.get(vk,False); self.previous[vk]=down
            if down and not prior and mods:
                shortcut="+".join(mods+[name])
                try: events.append(safe_input_event(application=self.application,kind="shortcut",shortcut=shortcut))
                except ValueError: pass
        x,y=self.cursor(); w=max(1,window.right-window.left); h=max(1,window.bottom-window.top)
        xn=min(1.0,max(0.0,(x-window.left)/w)); yn=min(1.0,max(0.0,(y-window.top)/h))
        for vk,button in MOUSE:
            down=self._down(vk); prior=self.previous.get(vk,False); self.previous[vk]=down
            if down and not prior:
                events.append(safe_input_event(application=self.application,kind="mouse_click",button=button,x_norm=xn,y_norm=yn))
        return tuple(events)

class SemanticCommandFeed:
    """Consumes already-semantic command names from an app-specific producer. No arguments/free text."""
    def __init__(self,application:str):
        self.application=application
    def accept(self,command_name:str):
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]{0,63}",command_name):
            raise ValueError("unsafe_command_name")
        return safe_input_event(application=self.application,kind="app_command",command_name=command_name)
