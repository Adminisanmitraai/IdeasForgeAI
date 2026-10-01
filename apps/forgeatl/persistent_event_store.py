from __future__ import annotations
import hashlib,json,os
from dataclasses import asdict
from pathlib import Path
from event_store import Event,BoundaryViolation,EventStoreError

class CorruptStore(EventStoreError): pass
class PersistentStudentEventStore:
    def __init__(self,path:Path):
        self.path=Path(path); self._events=[]; self._ids=set(); self._load()
    @staticmethod
    def _canonical(d): return json.dumps(d,sort_keys=True,separators=(",",":"))
    @classmethod
    def _digest(cls,record): return hashlib.sha256(cls._canonical(record).encode()).hexdigest()
    def _load(self):
        if not self.path.exists(): return
        prev="GENESIS"
        for n,line in enumerate(self.path.read_text(encoding="utf-8").splitlines(),1):
            try: row=json.loads(line)
            except Exception as e: raise CorruptStore(f"invalid json line {n}") from e
            body=row.get("event"); digest=row.get("digest")
            if row.get("prev_digest")!=prev or digest!=self._digest({"prev_digest":prev,"event":body}):
                raise CorruptStore(f"hash chain mismatch line {n}")
            e=Event(**body)
            if e.sequence!=n or e.event_id in self._ids: raise CorruptStore(f"sequence/id corruption line {n}")
            if e.phase=="examination" and e.actor=="teacher": raise CorruptStore(f"exam boundary corruption line {n}")
            self._events.append(e); self._ids.add(e.event_id); prev=digest
    def append(self,e:Event):
        if e.event_id in self._ids:
            existing=next(x for x in self._events if x.event_id==e.event_id)
            if existing==e: return existing
            raise EventStoreError("event_id collision")
        if e.sequence!=len(self._events)+1: raise EventStoreError("invalid sequence")
        if e.phase=="examination" and e.actor=="teacher": raise BoundaryViolation("FAIL_CLOSED")
        self.path.parent.mkdir(parents=True,exist_ok=True)
        prev="GENESIS" if not self._events else self._last_digest()
        body=asdict(e); core={"prev_digest":prev,"event":body}; row={**core,"digest":self._digest(core)}
        with self.path.open("a",encoding="utf-8",newline="\n") as f:
            f.write(self._canonical(row)+"\n"); f.flush(); os.fsync(f.fileno())
        self._events.append(e); self._ids.add(e.event_id); return e
    def _last_digest(self):
        line=self.path.read_text(encoding="utf-8").splitlines()[-1]; return json.loads(line)["digest"]
    def all(self): return tuple(self._events)
    def replay(self,student_id,session_id): return tuple(e for e in self._events if e.student_id==student_id and e.session_id==session_id)
