"""Names-only AutoCAD command evidence. No command execution or native capture."""
from __future__ import annotations
from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import math
import re
from demonstration_capture import ScreenObservation, SafeInputEvent, build_step, safe_input_event

MAX_SECONDS = 10.0
MAX_EVENTS = 128
MAX_STEPS = 20
MAX_INTERACTIONS = 40
MAX_BEFORE_AGE = 0.75
COMMANDS = frozenset('LINE PLINE CIRCLE ARC RECTANG MOVE COPY ROTATE SCALE STRETCH OFFSET TRIM EXTEND ERASE HATCH DIM DIMALIGNED DIMLINEAR DIMEDIT MATCHPROP PROPERTIES LAYER -LAYER BLOCK INSERT EXPLODE JOIN PEDIT FILLET CHAMFER REGEN REGENALL ZOOM PAN SELECT QSELECT QSAVE UNDO U REDO MREDO'.split())


def command_name(value):
    if type(value) is not str or len(value) > 64:
        return None
    if not re.fullmatch(r"[_.']{0,3}-?[A-Za-z][A-Za-z0-9_]{0,47}", value):
        return None
    name = value.lstrip("_.'").upper()
    return name if name in COMMANDS else None


@dataclass(frozen=True)
class CommandEvent:
    sequence: int
    phase: str
    name: str
    monotonic_at: float
    occurred_at: str
    document_token: str
    source: str = 'autocad_activex_document_event'


@dataclass(frozen=True)
class TimedFrame:
    observation: ScreenObservation
    captured_at: float
    document_token: str
    hwnd: int
    pid: int


class CommandQueue:
    """COM callback target: bounded metadata only; no IO or COM calls."""
    def __init__(self, token, clock, gate, deadline, *, retain=True):
        self.token, self.clock, self.gate, self.deadline = token, clock, gate, deadline
        self.retain = retain
        self.active = True
        self.events = deque()
        self.accepted = self.rejected = self.filtered = 0
        self.gaps = 0
        self.overflow = False

    def offer(self, phase, raw_name):
        if not self.active or not self.retain:
            return False
        now = self.clock()
        if now >= self.deadline or not self.gate():
            self.filtered += 1
            self.gaps += 1
            return False
        name = command_name(raw_name)
        if phase not in {'begin', 'end'} or name is None:
            self.rejected += 1
            self.gaps += 1
            return False
        if self.accepted >= MAX_EVENTS:
            self.overflow = True
            self.gaps += 1
            return False
        self.accepted += 1
        self.events.append(CommandEvent(self.accepted, phase, name, now,
            datetime.now(timezone.utc).isoformat(), self.token))
        return True

    def drain(self):
        rows = tuple(self.events)
        self.events.clear()
        return rows

    def close(self):
        self.active = False


class SemanticCorrelator:
    """Only complete, same-document, single-command spans become steps.

    EndCommand means an end event was observed, not proof of successful editing.
    A frame hash difference means differing image bytes, not a verified CAD change.
    """
    def __init__(self, run_id, token, write_event, write_span, write_step):
        self.run_id, self.token = run_id, token
        self.write_event, self.write_span, self.write_step = write_event, write_span, write_step
        self.stack = []
        self.steps = self.pairs = self.incomplete = self.unmatched = 0
        self.last_sequence = 0
        self.last_time = -math.inf

    def interrupt(self, reason):
        for item in self.stack:
            self.write_span({'command': item['begin'].name, 'begin_event': asdict(item['begin']),
                'end_event': None, 'status': 'incomplete', 'reason': reason,
                'command_success': None, 'training_eligible': False})
            self.incomplete += 1
        self.stack.clear()

    def event(self, event, *, before=None, after=None):
        if (event.document_token != self.token or event.name not in COMMANDS or
            event.phase not in {'begin', 'end'} or event.sequence <= self.last_sequence or
            not math.isfinite(event.monotonic_at) or event.monotonic_at < self.last_time):
            self.interrupt('invalid_event_order_or_binding')
            raise ValueError('invalid_command_event')
        self.last_sequence, self.last_time = event.sequence, event.monotonic_at
        self.write_event(asdict(event))
        if event.phase == 'begin':
            for item in self.stack:
                item['ambiguous'] = True
            self.stack.append({'begin': event, 'before': before, 'interactions': [], 'ambiguous': bool(self.stack)})
            return None
        if not self.stack or self.stack[-1]['begin'].name != event.name:
            self.unmatched += 1
            self.interrupt('unmatched_end')
            return None
        item = self.stack.pop()
        self.pairs += 1
        begin, first = item['begin'], item['before']
        reason = None
        if item['ambiguous']:
            reason = 'nested_command_ambiguous'
        elif first is None or after is None:
            reason = 'frame_pair_unavailable'
        elif (first.document_token != self.token or after.document_token != self.token or
              (first.hwnd, first.pid) != (after.hwnd, after.pid)):
            reason = 'frame_binding_mismatch'
        elif not (0 <= begin.monotonic_at - first.captured_at <= MAX_BEFORE_AGE and after.captured_at >= event.monotonic_at):
            reason = 'frame_timing_invalid'
        elif (first.observation.phase != 'before' or after.observation.phase != 'after' or
              first.observation.application != 'autocad' or after.observation.application != 'autocad' or
              first.observation.project_hint != after.observation.project_hint):
            reason = 'frame_context_mismatch'
        elif event.name.startswith('-'):
            # Preserve the true command name in the span; do not relabel it or
            # bypass the stricter identifier contract of the earlier step model.
            reason = 'command_identifier_outside_legacy_step_contract'
        elif self.steps >= MAX_STEPS:
            reason = 'step_limit'
        span = {'command': event.name, 'begin_event': asdict(begin), 'end_event': asdict(event),
                'status': 'end_event_observed', 'command_success': None,
                'training_eligible': reason is None, 'correlation_hold': reason}
        self.write_span(span)
        if reason:
            return None
        action = safe_input_event(application='autocad', kind='app_command', command_name=event.name, occurred_at=begin.occurred_at)
        step = build_step(session_id=self.run_id, sequence=self.steps + 1,
                          before=first.observation, action=action, after=after.observation)
        record = {'schema': 'forgewa.semantic-demonstration.v1', 'span': span,
                  'demonstration': asdict(step), 'interactions': item['interactions'],
                  'association': 'temporal_same_document_not_causal_proof',
                  'before_captured_at': first.captured_at, 'after_captured_at': after.captured_at,
                  'observe_only': True, 'autonomous_actions': False}
        self.write_step(record)
        self.steps += 1
        return record

    def interaction(self, event: SafeInputEvent, at: float):
        if not self.stack or self.stack[-1]['ambiguous']:
            return False
        item = self.stack[-1]
        if (event.application != 'autocad' or event.raw_text is not None or event.command_name is not None or
            event.kind not in {'mouse_click', 'shortcut'} or not math.isfinite(at) or at < item['begin'].monotonic_at or
            len(item['interactions']) >= MAX_INTERACTIONS):
            return False
        if event.kind == 'mouse_click' and (event.button not in {'left', 'right', 'middle'} or
            any(type(v) not in (int, float) or not 0 <= v <= 1 for v in (event.x_norm, event.y_norm))):
            return False
        if event.kind == 'shortcut' and event.shortcut not in {'ctrl+s','ctrl+z','ctrl+y','ctrl+c','ctrl+v','ctrl+x','ctrl+a'}:
            return False
        item['interactions'].append({'kind': event.kind, 'button': event.button if event.kind == 'mouse_click' else None,
            'shortcut': event.shortcut if event.kind == 'shortcut' else None,
            'x_norm': event.x_norm if event.kind == 'mouse_click' else None,
            'y_norm': event.y_norm if event.kind == 'mouse_click' else None, 'monotonic_at': at})
        return True
