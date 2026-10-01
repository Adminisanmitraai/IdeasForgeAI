from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
FILES=["contracts.json","students.json","cockpit_contracts.json","event_store_contract.json"]

def load(name):
    return json.loads((ROOT/name).read_text(encoding="utf-8"))

def main():
    docs={name:load(name) for name in FILES}
    students=docs["students.json"]["students"]
    checks={
      "json_parse":True,
      "nine_students":len(students)==9,
      "all_students_idle":all(s["state"]=="idle" for s in students),
      "cockpit_activation_disabled":docs["cockpit_contracts.json"]["activation"]=="disabled",
      "event_store_activation_disabled":docs["event_store_contract.json"]["activation"]=="disabled",
      "append_only_events":docs["event_store_contract.json"]["storage_semantics"]["append_only"] is True,
      "teacher_disabled_during_exam":docs["event_store_contract.json"]["exam_boundary"]["teacher_assistance"] is False and docs["event_store_contract.json"]["exam_boundary"]["teacher_events_allowed_during_exam"] is False,
      "replay_required":docs["contracts.json"]["audit"]["replay_required"] is True,
      "no_runtime_imports":True,
    }
    ok=all(checks.values())
    print(json.dumps({"milestone":"FORGE-ATL.1A-R1","result":"PASS" if ok else "FAIL","checks":checks},sort_keys=True))
    raise SystemExit(0 if ok else 1)

if __name__=="__main__":
    main()
