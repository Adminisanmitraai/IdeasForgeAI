"""Compatibility adapters over existing IdeasForgeAI backend capabilities."""

from .terminal_approval_adapter import TerminalApprovalAdapter
from .terminal_audit_adapter import TerminalAuditAdapter
from .terminal_event_adapter import TerminalEventAdapter
from .terminal_execution_adapter import TerminalExecutionAdapter
from .terminal_planning_adapter import TerminalPlanningAdapter
from .terminal_session_adapter import TerminalSessionAdapter

__all__ = [
    "TerminalApprovalAdapter",
    "TerminalAuditAdapter",
    "TerminalEventAdapter",
    "TerminalExecutionAdapter",
    "TerminalPlanningAdapter",
    "TerminalSessionAdapter",
]
