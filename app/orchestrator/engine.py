"""Pipeline orchestrator — coordinates the 8-phase product creation pipeline."""

import uuid
import time
from datetime import datetime, timezone

import structlog

from app import db
from app.models.pipeline_run import PipelineRun
from app.models.phase_result import PhaseResult
from app.orchestrator.state import (
    PipelineStatus,
    PhaseStatus,
    PHASE_AGENTS,
    PHASE_NAMES,
    TOTAL_PHASES,
    can_transition_pipeline,
)
from app.orchestrator.gates import requires_approval, create_approval_gate

logger = structlog.get_logger(__name__)


class PipelineOrchestrator:
    """Manages the lifecycle of a product creation pipeline."""

    def __init__(self, pipeline_run_id: str):
        self.pipeline_run_id = pipeline_run_id
        self.trace_id = str(uuid.uuid4())[:8]

    @property
    def pipeline(self) -> PipelineRun:
        return PipelineRun.query.get(self.pipeline_run_id)

    def start(self):
        """Start or resume the pipeline from its current phase."""
        pipeline = self.pipeline
        if not pipeline:
            raise ValueError(f"Pipeline {self.pipeline_run_id} not found")

        logger.info(
            "pipeline.start",
            pipeline_id=self.pipeline_run_id,
            niche=pipeline.niche,
            current_phase=pipeline.current_phase,
            trace_id=self.trace_id,
        )

        pipeline.status = PipelineStatus.RUNNING
        pipeline.started_at = pipeline.started_at or datetime.now(timezone.utc)
        db.session.commit()

        return self.run_phase(pipeline.current_phase)

    def run_phase(self, phase_number: int):
        """Execute a single phase of the pipeline."""
        pipeline = self.pipeline

        if phase_number > TOTAL_PHASES:
            return self._complete_pipeline()

        agent_name = PHASE_AGENTS[phase_number]
        phase_name = PHASE_NAMES[phase_number]

        logger.info(
            "phase.start",
            pipeline_id=self.pipeline_run_id,
            phase=phase_number,
            phase_name=phase_name,
            agent=agent_name,
            trace_id=self.trace_id,
        )

        # Create phase result record
        phase_result = PhaseResult(
            pipeline_run_id=self.pipeline_run_id,
            phase_number=phase_number,
            agent_name=agent_name,
            status=PhaseStatus.RUNNING,
            trace_id=self.trace_id,
        )
        db.session.add(phase_result)
        pipeline.current_phase = phase_number
        db.session.commit()

        try:
            # Get the agent and execute
            agent = self._get_agent(agent_name)
            input_data = self._gather_phase_input(phase_number)

            phase_result.input_data = input_data
            db.session.commit()

            start_time = time.time()
            output_data = agent.execute(
                pipeline_run_id=self.pipeline_run_id,
                input_data=input_data,
                phase_result_id=phase_result.id,
            )
            duration = time.time() - start_time

            phase_result.output_data = output_data
            phase_result.duration_seconds = round(duration, 2)

            logger.info(
                "phase.completed",
                pipeline_id=self.pipeline_run_id,
                phase=phase_number,
                duration=duration,
                trace_id=self.trace_id,
            )

            # Check if approval is needed
            if requires_approval(phase_number, pipeline.config):
                create_approval_gate(phase_result)
                pipeline.status = PipelineStatus.PAUSED
                db.session.commit()

                logger.info(
                    "phase.waiting_approval",
                    pipeline_id=self.pipeline_run_id,
                    phase=phase_number,
                    trace_id=self.trace_id,
                )
                return {
                    "status": "paused",
                    "phase": phase_number,
                    "phase_name": phase_name,
                    "message": f"Phase {phase_number} ({phase_name}) waiting for approval",
                    "phase_result_id": phase_result.id,
                }

            # No approval needed — auto-advance
            phase_result.status = PhaseStatus.COMPLETED
            phase_result.completed_at = datetime.now(timezone.utc)
            db.session.commit()

            return self._advance_to_next_phase(phase_number)

        except Exception as e:
            logger.error(
                "phase.failed",
                pipeline_id=self.pipeline_run_id,
                phase=phase_number,
                error=str(e),
                trace_id=self.trace_id,
            )
            phase_result.status = PhaseStatus.FAILED
            phase_result.error_log = str(e)
            pipeline.status = PipelineStatus.FAILED
            pipeline.error_message = f"Phase {phase_number} failed: {str(e)}"
            db.session.commit()
            raise

    def resume_after_approval(self, phase_number: int):
        """Resume the pipeline after a phase has been approved."""
        pipeline = self.pipeline

        logger.info(
            "pipeline.resume",
            pipeline_id=self.pipeline_run_id,
            phase=phase_number,
            trace_id=self.trace_id,
        )

        # Mark phase as completed
        phase_result = PhaseResult.query.filter_by(
            pipeline_run_id=self.pipeline_run_id,
            phase_number=phase_number,
        ).order_by(PhaseResult.created_at.desc()).first()

        if phase_result:
            phase_result.status = PhaseStatus.COMPLETED
            phase_result.completed_at = datetime.now(timezone.utc)

        pipeline.status = PipelineStatus.RUNNING
        db.session.commit()

        return self._advance_to_next_phase(phase_number)

    def _advance_to_next_phase(self, current_phase: int):
        """Move to the next phase in the pipeline."""
        next_phase = current_phase + 1
        if next_phase > TOTAL_PHASES:
            return self._complete_pipeline()
        return self.run_phase(next_phase)

    def _complete_pipeline(self):
        """Mark the pipeline as completed."""
        pipeline = self.pipeline
        pipeline.status = PipelineStatus.COMPLETED
        pipeline.completed_at = datetime.now(timezone.utc)
        db.session.commit()

        logger.info(
            "pipeline.completed",
            pipeline_id=self.pipeline_run_id,
            niche=pipeline.niche,
            trace_id=self.trace_id,
        )
        return {"status": "completed", "pipeline_id": self.pipeline_run_id}

    def _get_agent(self, agent_name: str):
        """Get the agent instance for a given agent name."""
        from app.agents.trend_discovery import TrendDiscoveryAgent
        from app.agents.niche_validator import NicheValidatorAgent
        from app.agents.audience_profiler import AudienceProfilerAgent
        from app.agents.product_architect import ProductArchitectAgent
        from app.agents.content_writer import ContentWriterAgent
        from app.agents.designer import DesignerAgent
        from app.agents.funnel_builder import FunnelBuilderAgent
        from app.agents.campaign_launcher import CampaignLauncherAgent

        agents = {
            "trend_discovery": TrendDiscoveryAgent,
            "niche_validator": NicheValidatorAgent,
            "audience_profiler": AudienceProfilerAgent,
            "product_architect": ProductArchitectAgent,
            "content_writer": ContentWriterAgent,
            "designer": DesignerAgent,
            "funnel_builder": FunnelBuilderAgent,
            "campaign_launcher": CampaignLauncherAgent,
        }
        agent_class = agents.get(agent_name)
        if not agent_class:
            raise ValueError(f"Unknown agent: {agent_name}")
        return agent_class()

    def _gather_phase_input(self, phase_number: int) -> dict:
        """Gather input data for a phase from previous phase results."""
        pipeline = self.pipeline
        input_data = {
            "niche": pipeline.niche,
            "topic": pipeline.topic,
            "pipeline_config": pipeline.config,
        }

        # Collect outputs from all completed previous phases
        previous_results = PhaseResult.query.filter(
            PhaseResult.pipeline_run_id == self.pipeline_run_id,
            PhaseResult.phase_number < phase_number,
            PhaseResult.status == PhaseStatus.COMPLETED,
        ).order_by(PhaseResult.phase_number).all()

        for result in previous_results:
            key = f"phase_{result.phase_number}_output"
            input_data[key] = result.output_data

        return input_data


def create_pipeline(niche: str, topic: str = None, config: dict = None) -> PipelineRun:
    """Create a new pipeline run."""
    pipeline = PipelineRun(
        niche=niche,
        topic=topic,
        config=config or {},
        status=PipelineStatus.PENDING,
        current_phase=1,
    )
    db.session.add(pipeline)
    db.session.commit()

    logger.info("pipeline.created", pipeline_id=pipeline.id, niche=niche)
    return pipeline
