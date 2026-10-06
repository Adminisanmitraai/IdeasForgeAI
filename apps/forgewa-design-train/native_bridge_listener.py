"""Persistent local receiver for ForgeWa AutoCAD semantic bridge v1.

Reads newline-delimited names-only records from an outbound-only plugin pipe.
Keeps each accepted connection open for multiple records and deduplicates by seq.
"""
from __future__ import annotations
import json,re
from dataclasses import dataclass

PIPE_NAME=r"\\.\pipe\ForgeWa.AutoCAD.Semantic.v1"
COMMAND=re.compile(r"^[A-Z0-9_-]{1,64}$")

@dataclass
class ListenerState:
    last_sequence:int=0
    accepted:int=0
    duplicates:int=0
    invalid:int=0
    reconnects:int=0

def validate_record(record:dict)->dict:
    if set(record)!={"v","seq","phase","command"}: raise ValueError("unexpected_fields")
    if record["v"]!=1 or not isinstance(record["seq"],int) or isinstance(record["seq"],bool) or record["seq"]<1:
        raise ValueError("invalid_sequence")
    if record["phase"] not in {"start","end","cancel"}: raise ValueError("invalid_phase")
    if not isinstance(record["command"],str) or not COMMAND.fullmatch(record["command"]):
        raise ValueError("invalid_command")
    return record

def accept_line(line:str,state:ListenerState):
    try: record=validate_record(json.loads(line))
    except (ValueError,TypeError,json.JSONDecodeError):
        state.invalid+=1; return None
    if record["seq"]<=state.last_sequence:
        state.duplicates+=1; return None
    state.last_sequence=record["seq"];state.accepted+=1
    return record
