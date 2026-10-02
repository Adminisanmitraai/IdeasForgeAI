from __future__ import annotations
import json
import math
from pathlib import Path
import time

from foreground_observer import ObservationTracker, read_foreground_context
from observation import TeacherTimeline, detect_application

OBSERVE_ONLY = True
AUTONOMOUS_ACTIONS = False
DEFAULT_SAMPLES = 10
DEFAULT_INTERVAL_SECONDS = 1.0

def run_bounded_session(timeline_path: str | Path, samples: int = DEFAULT_SAMPLES, interval_seconds: float = DEFAULT_INTERVAL_SECONDS):
    if type(samples) is not int or samples < 1 or samples > DEFAULT_SAMPLES:
        raise ValueError("samples_out_of_bounds")
    if type(interval_seconds) not in (int, float) or not math.isfinite(interval_seconds) or not 0 <= interval_seconds <= DEFAULT_INTERVAL_SECONDS:
        raise ValueError("interval_out_of_bounds")
    tracker = ObservationTracker(TeacherTimeline(timeline_path))
    observations = []
    stop_reason = "observer_error"
    started = time.monotonic()
    try:
        for index in range(samples):
            ctx = read_foreground_context()
            app = detect_application(ctx.executable)
            events = tracker.observe(ctx) if app != "other" or tracker.session is not None else ()
            observations.append({
                "sample": index + 1,
                "application": app,
                "supported_foreground": app != "other",
                "event_kinds": [event.kind for event in events],
            })
            if index + 1 < samples:
                time.sleep(interval_seconds)
        stop_reason = "bounded_stop"
    finally:
        final_events = tracker.close(reason=stop_reason)
    return {
        "status": "COMPLETE",
        "observe_only": OBSERVE_ONLY,
        "autonomous_actions": AUTONOMOUS_ACTIONS,
        "samples": len(observations),
        "interval_seconds": interval_seconds,
        "observations": observations,
        "stop_reason": stop_reason,
        "final_event_kinds": [event.kind for event in final_events],
        "active_session_closed": tracker.session is None,
        "observation_elapsed_seconds": time.monotonic() - started,
    }

if __name__ == "__main__":
    evidence = Path(__file__).resolve().parent/"stores"/"training"/"bounded_teacher_timeline.jsonl"
    print(json.dumps(run_bounded_session(evidence), sort_keys=True, separators=(",", ":")))
