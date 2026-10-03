"""Owned finite CMDNAMES semantic observer. No callbacks or command injection."""
from __future__ import annotations
import hashlib
import json
import multiprocessing as mp
from pathlib import Path
import threading
import time
import uuid
from autocad_semantic import MAX_SECONDS, MAX_STEPS, SemanticCorrelator


def worker(connection, directory, absolute_deadline, factories=None):
    directory = Path(directory)
    source = correlator = None
    reason, error, released = 'time_limit', None, False
    created = False
    before = None
    try:
        from autocad_semantic_native import AutoCADCmdNamesPoller, WindowEvidenceSource, ScopedInteractions
        Source, Frames, Inputs = factories or (AutoCADCmdNamesPoller, WindowEvidenceSource, ScopedInteractions)
        directory.mkdir(parents=True, exist_ok=False)
        created = True
        def write(name, record):
            with (directory/name).open('a',encoding='utf-8') as out:
                out.write(json.dumps(record,sort_keys=True,allow_nan=False)+'\n')
        deadline = absolute_deadline - 0.35
        source = Source(deadline=deadline,consent=True)
        frames = Frames(source,directory/'frames',deadline)
        inputs = Inputs(source.binding)
        correlator = SemanticCorrelator(directory.name,source.token,
            lambda r: write('command_events.jsonl',r),
            lambda r: write('command_spans.jsonl',r),
            lambda r: write('semantic_steps.jsonl',r))
        connection.send({'state':'ARMED','commands':0,'pairs':0,'steps':0,'run_dir':str(directory),
                         'semantic_source':'cmdnames_poll','callbacks':False})
        next_frame, last_gaps = 0.0, 0
        while time.monotonic() < deadline:
            if connection.poll():
                reason = 'user_stop' if connection.recv() == 'stop' else 'invalid_control'
                break
            events = source.poll()
            if source.detector.gaps != last_gaps:
                correlator.interrupt('cmdnames_gap_or_resync')
                before = None
                events = ()
                last_gaps = source.detector.gaps
            if not source.binding.active():
                correlator.interrupt('foreground_lost')
                before = None
                events = ()
            for event in events:
                if time.monotonic() >= deadline:
                    reason = 'time_limit'
                    break
                after = frames.capture('after') if event.phase == 'end' else None
                correlator.event(event,before=before,after=after)
                if event.phase == 'end':
                    before = None
            if correlator.steps >= MAX_STEPS:
                reason = 'step_limit'
                break
            for interaction in inputs.poll():
                correlator.interaction(interaction,time.monotonic())
            if not correlator.stack and time.monotonic() >= next_frame:
                before = frames.capture('before')
                next_frame = time.monotonic() + 0.4
            connection.send({'state':'OBSERVING' if source.binding.active() else 'WAITING_FOR_AUTOCAD',
                'commands':source.events,'pairs':correlator.pairs,'steps':correlator.steps,
                'run_dir':str(directory),'semantic_source':'cmdnames_poll','callbacks':False})
            time.sleep(0.03)
    except Exception as exc:
        reason, error = 'observer_error', type(exc).__name__
    finally:
        try:
            if correlator:
                correlator.interrupt(reason)
        except Exception as exc:
            reason, error = 'final_evidence_error', type(exc).__name__
        finally:
            if source:
                try:
                    released = source.close()
                except Exception as exc:
                    reason, error, released = 'source_release_error', type(exc).__name__, False
        status = {'state':'STOPPED' if reason=='user_stop' else 'COMPLETED' if reason in {'time_limit','step_limit'} else 'ERROR',
            'stop_reason':reason,'error_type':error,'run_dir':str(directory),
            'commands':source.events if source else 0,'pairs':correlator.pairs if correlator else 0,
            'steps':correlator.steps if correlator else 0,
            'incomplete_spans':correlator.incomplete if correlator else 0,
            'unmatched_end_events':correlator.unmatched if correlator else 0,
            'source_released':released,'observe_only':True,'autonomous_actions':False,
            'command_injection':False,'raw_text_recording':False,'production_activation':False,
            'source':'fixture' if factories else 'live_cmdnames_poll','command_success_inferred':False,
            'binding':getattr(source,'metadata',None),'summary_saved':False,'callbacks':False,
            'connection_point':False}
        if source and not released:
            status.update(state='ERROR',stop_reason='source_release_not_confirmed')
        if created:
            try:
                hashes = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.glob('*.jsonl')}
                status['evidence_sha256'] = hashes
                status['summary_saved'] = True
                with (directory/'summary.json').open('x',encoding='utf-8') as stream:
                    stream.write(json.dumps(status,indent=2))
            except Exception as exc:
                status.update(state='ERROR',stop_reason='summary_write_error',summary_saved=False,error_type=type(exc).__name__)
        try:
            connection.send(status)
        except (BrokenPipeError,EOFError,OSError):
            pass
        finally:
            connection.close()


class SemanticClient:
    def __init__(self, root, *, factories=None):
        self.root, self.factories = Path(root), factories
        self.process = self.connection = self.timer = None
        self.started = 0.0
        self.status = {'state':'IDLE','commands':0,'pairs':0,'steps':0,'worker_alive':False}
        self.timed_out = False
        self.lock = threading.Lock()

    def _terminate_owned(self, owned):
        with self.lock:
            if owned is self.process and owned.is_alive():
                self.timed_out = True
                owned.terminate()

    def start(self, *, consent):
        if consent is not True:
            raise PermissionError('explicit_semantic_and_frame_consent_required')
        if self.process and self.process.is_alive():
            raise RuntimeError('run_already_active')
        if self.timer: self.timer.cancel()
        if self.connection: self.connection.close()
        if self.process: self.process.join(0)
        ctx = mp.get_context('spawn')
        self.connection, child = ctx.Pipe()
        directory = self.root / ('run_' + uuid.uuid4().hex)
        self.started, self.timed_out = time.monotonic(), False
        self.process = ctx.Process(target=worker,args=(child,str(directory),self.started+MAX_SECONDS,self.factories),daemon=True)
        self.status = {'state':'STARTING','commands':0,'pairs':0,'steps':0,'run_dir':str(directory)}
        self.process.start(); child.close()
        self.timer = threading.Timer(max(0,MAX_SECONDS-(time.monotonic()-self.started)),self._terminate_owned,args=(self.process,))
        self.timer.daemon = True; self.timer.start()

    def stop(self):
        if self.process and self.process.is_alive():
            try: self.connection.send('stop')
            except (BrokenPipeError,EOFError,OSError): self._terminate_owned(self.process)

    def poll(self):
        if self.connection:
            try:
                while self.connection.poll(): self.status = self.connection.recv()
            except (BrokenPipeError,EOFError,OSError): pass
        alive = bool(self.process and self.process.is_alive())
        if self.process and not alive:
            self.process.join(0)
            if self.timer: self.timer.cancel()
            if self.timed_out or self.status.get('state') in {'STARTING','ARMED','OBSERVING','WAITING_FOR_AUTOCAD'}:
                self.status.update(state='INTERRUPTED',stop_reason='watchdog_or_unexpected_exit',source_released=False)
        return {**self.status,'worker_alive':alive,
                'remaining_seconds':max(0,MAX_SECONDS-(time.monotonic()-self.started)) if alive else 0,
                'watchdog_timeout':self.timed_out}

    def close(self):
        self.stop()
        if self.process:
            self.process.join(0.3)
            if self.process.is_alive():
                self._terminate_owned(self.process); self.process.join(0.3)
        if self.timer: self.timer.cancel()
        self.poll()
        if self.connection:
            self.connection.close(); self.connection=None
