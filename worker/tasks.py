"""Celery tasks — wraps pipeline phases for async execution."""

import structlog
from worker.celery_app import celery

logger = structlog.get_logger(__name__)


@celery.task(bind=True, name="worker.tasks.run_pipeline")
def run_pipeline(self, pipeline_run_id: str):
    """Start or resume a pipeline execution."""
    from app import create_app
    app = create_app()

    with app.app_context():
        from app.orchestrator.engine import PipelineOrchestrator

        orchestrator = PipelineOrchestrator(pipeline_run_id)
        try:
            result = orchestrator.start()
            logger.info("task.pipeline.done", pipeline_id=pipeline_run_id, result=result)
            return result
        except Exception as e:
            logger.error("task.pipeline.failed", pipeline_id=pipeline_run_id, error=str(e))
            raise


@celery.task(bind=True, name="worker.tasks.run_phase")
def run_phase(self, pipeline_run_id: str, phase_number: int):
    """Run a specific phase of a pipeline."""
    from app import create_app
    app = create_app()

    with app.app_context():
        from app.orchestrator.engine import PipelineOrchestrator

        orchestrator = PipelineOrchestrator(pipeline_run_id)
        try:
            result = orchestrator.run_phase(phase_number)
            logger.info("task.phase.done", pipeline_id=pipeline_run_id, phase=phase_number)
            return result
        except Exception as e:
            logger.error("task.phase.failed", pipeline_id=pipeline_run_id, phase=phase_number, error=str(e))
            raise


@celery.task(bind=True, name="worker.tasks.resume_after_approval")
def resume_after_approval(self, pipeline_run_id: str, phase_number: int):
    """Resume pipeline after a phase approval."""
    from app import create_app
    app = create_app()

    with app.app_context():
        from app.orchestrator.engine import PipelineOrchestrator

        orchestrator = PipelineOrchestrator(pipeline_run_id)
        try:
            result = orchestrator.resume_after_approval(phase_number)
            logger.info("task.resume.done", pipeline_id=pipeline_run_id, phase=phase_number)
            return result
        except Exception as e:
            logger.error("task.resume.failed", pipeline_id=pipeline_run_id, phase=phase_number, error=str(e))
            raise


@celery.task(name="worker.tasks.sync_ad_performance")
def sync_ad_performance():
    """Periodic task: sync Meta Ads performance data."""
    from app import create_app
    app = create_app()

    with app.app_context():
        from app.services.learning_service import sync_all_ad_performance
        try:
            sync_all_ad_performance()
            logger.info("task.sync_ads.done")
        except Exception as e:
            logger.error("task.sync_ads.failed", error=str(e))
