"""Legal workflows package for AI Consumer Lawyer.

Exports the core legal workflow engines:
- Mode 1: CaseBuilder (fact intake, timeline extraction, evidence audit)
- Mode 2: LegalAdvisor (legal standing, 4-step pathway, statutory calculations)
- Mode 3: DocumentDrafter (Grievance Email, 15-day Legal Notice, e-Daakhil Complaint)
- Mode 4: OpposingCounselSimulator (adversarial practice, defense rebuttal, scoring)
"""

from __future__ import annotations

from legal_assistant.workflows.advisor import LegalAdvisor, LegalAnalysisResult
from legal_assistant.workflows.case_builder import CaseBuilder, OutOfScopeDisputeError
from legal_assistant.workflows.drafter import DocumentDrafter, DraftDocument
from legal_assistant.workflows.simulator import (
    ArgumentFeedback,
    DefenseTacticType,
    OpposingCounselSimulator,
    SimulatorState,
    SimulatorTurn,
)

__all__ = [
    "ArgumentFeedback",
    "CaseBuilder",
    "DefenseTacticType",
    "DocumentDrafter",
    "DraftDocument",
    "LegalAdvisor",
    "LegalAnalysisResult",
    "OpposingCounselSimulator",
    "OutOfScopeDisputeError",
    "SimulatorState",
    "SimulatorTurn",
]
