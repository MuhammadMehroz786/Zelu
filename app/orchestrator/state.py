"""Pipeline state machine — manages transitions between phases."""

from enum import Enum


class PipelineStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"  # waiting for human approval
    COMPLETED = "completed"
    FAILED = "failed"


class PhaseStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"


# Valid transitions for pipeline status
PIPELINE_TRANSITIONS = {
    PipelineStatus.PENDING: [PipelineStatus.RUNNING, PipelineStatus.FAILED],
    PipelineStatus.RUNNING: [PipelineStatus.PAUSED, PipelineStatus.COMPLETED, PipelineStatus.FAILED],
    PipelineStatus.PAUSED: [PipelineStatus.RUNNING, PipelineStatus.FAILED],
    PipelineStatus.COMPLETED: [],
    PipelineStatus.FAILED: [PipelineStatus.PENDING],  # allow retry
}

# Valid transitions for phase status
PHASE_TRANSITIONS = {
    PhaseStatus.PENDING: [PhaseStatus.RUNNING],
    PhaseStatus.RUNNING: [PhaseStatus.WAITING_APPROVAL, PhaseStatus.COMPLETED, PhaseStatus.FAILED],
    PhaseStatus.WAITING_APPROVAL: [PhaseStatus.APPROVED, PhaseStatus.REJECTED],
    PhaseStatus.APPROVED: [PhaseStatus.COMPLETED],
    PhaseStatus.REJECTED: [PhaseStatus.RUNNING],  # re-run with edits
    PhaseStatus.COMPLETED: [],
    PhaseStatus.FAILED: [PhaseStatus.PENDING],  # allow retry
}

PHASE_NAMES = {
    1: "Trend Discovery",
    2: "Niche Validation",
    3: "Audience & Pain Points",
    4: "Product Structure",
    5: "Content Writing",
    6: "Visual Design",
    7: "Funnel & Copy",
    8: "Campaign Launch",
}

PHASE_AGENTS = {
    1: "trend_discovery",
    2: "niche_validator",
    3: "audience_profiler",
    4: "product_architect",
    5: "content_writer",
    6: "designer",
    7: "funnel_builder",
    8: "campaign_launcher",
}

TOTAL_PHASES = 8


def can_transition_pipeline(current: str, target: str) -> bool:
    current_status = PipelineStatus(current)
    target_status = PipelineStatus(target)
    return target_status in PIPELINE_TRANSITIONS.get(current_status, [])


def can_transition_phase(current: str, target: str) -> bool:
    current_status = PhaseStatus(current)
    target_status = PhaseStatus(target)
    return target_status in PHASE_TRANSITIONS.get(current_status, [])
