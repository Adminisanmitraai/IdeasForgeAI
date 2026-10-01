from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Iterable

class BoundaryViolation(RuntimeError): pass
class EventStoreError(RuntimeError): pass

@dataclass(frozen=True)
class Event:
    event_id:str; sequence:int; student_id:str; session_id:str
    timestamp:str; phase:str; actor:str; event_type:str; summary:str
    payload_ref:str; correlation_id:str; data:dict[str,Any]

class StudentEventStore:
    def __init__(self): self._events:list[Event]=[]; self._ids:set[str]=set()
    def append(self,event:Event)->Event:
        if event.event_id in self._ids: raise EventStoreError("duplicate event_id")
        expected=len(self._events)+1
        if event.sequence!=expected: raise EventStoreError(f"sequence must be {expected}")
        if event.phase=="examination" and event.actor=="teacher":
            raise BoundaryViolation("FAIL_CLOSED: teacher event prohibited during examination")
        self._events.append(event); self._ids.add(event.event_id); return event
    def replay(self,student_id:str,session_id:str)->tuple[Event,...]:
        return tuple(e for e in self._events if e.student_id==student_id and e.session_id==session_id)
    def all(self)->tuple[Event,...]: return tuple(self._events)
