"""Pipeline API — create, list, start, and manage pipelines."""

from flask import Blueprint, request, jsonify

from app import db
from app.models.pipeline_run import PipelineRun
from app.models.phase_result import PhaseResult
from app.models.product import Product
from app.orchestrator.engine import create_pipeline

pipeline_bp = Blueprint("pipeline", __name__)


@pipeline_bp.route("/", methods=["GET"])
def list_pipelines():
    """List all pipeline runs."""
    status_filter = request.args.get("status")
    query = PipelineRun.query.order_by(PipelineRun.created_at.desc())

    if status_filter:
        query = query.filter_by(status=status_filter)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    pagination = query.paginate(page=page, per_page=per_page)

    return jsonify({
        "pipelines": [p.to_dict() for p in pagination.items],
        "total": pagination.total,
        "page": page,
        "pages": pagination.pages,
    })


@pipeline_bp.route("/", methods=["POST"])
def create_new_pipeline():
    """Create and optionally start a new pipeline."""
    data = request.get_json()

    if not data or not data.get("niche"):
        return jsonify({"error": "niche is required"}), 400

    pipeline = create_pipeline(
        niche=data["niche"],
        topic=data.get("topic"),
        config=data.get("config", {}),
    )

    # Auto-start if requested
    if data.get("auto_start", False):
        from worker.tasks import run_pipeline
        run_pipeline.delay(pipeline.id)

    return jsonify(pipeline.to_dict()), 201


@pipeline_bp.route("/<pipeline_id>", methods=["GET"])
def get_pipeline(pipeline_id):
    """Get a pipeline with all phase results."""
    pipeline = PipelineRun.query.get(pipeline_id)
    if not pipeline:
        return jsonify({"error": "Pipeline not found"}), 404

    phases = PhaseResult.query.filter_by(
        pipeline_run_id=pipeline_id
    ).order_by(PhaseResult.phase_number).all()

    products = Product.query.filter_by(pipeline_run_id=pipeline_id).all()

    return jsonify({
        **pipeline.to_dict(),
        "phases": [p.to_dict() for p in phases],
        "products": [p.to_dict() for p in products],
    })


@pipeline_bp.route("/<pipeline_id>/start", methods=["POST"])
def start_pipeline(pipeline_id):
    """Start or resume a pipeline."""
    pipeline = PipelineRun.query.get(pipeline_id)
    if not pipeline:
        return jsonify({"error": "Pipeline not found"}), 404

    from worker.tasks import run_pipeline
    task = run_pipeline.delay(pipeline_id)

    return jsonify({
        "message": "Pipeline started",
        "pipeline_id": pipeline_id,
        "task_id": task.id,
    })


@pipeline_bp.route("/<pipeline_id>/stop", methods=["POST"])
def stop_pipeline(pipeline_id):
    """Stop a running pipeline."""
    pipeline = PipelineRun.query.get(pipeline_id)
    if not pipeline:
        return jsonify({"error": "Pipeline not found"}), 404

    pipeline.status = "failed"
    pipeline.error_message = "Manually stopped by user"
    db.session.commit()

    return jsonify({"message": "Pipeline stopped", "pipeline_id": pipeline_id})


@pipeline_bp.route("/stats", methods=["GET"])
def pipeline_stats():
    """Get pipeline statistics for the dashboard."""
    total = PipelineRun.query.count()
    running = PipelineRun.query.filter_by(status="running").count()
    paused = PipelineRun.query.filter_by(status="paused").count()
    completed = PipelineRun.query.filter_by(status="completed").count()
    failed = PipelineRun.query.filter_by(status="failed").count()
    total_products = Product.query.count()

    return jsonify({
        "total_pipelines": total,
        "running": running,
        "paused": paused,
        "completed": completed,
        "failed": failed,
        "total_products": total_products,
    })
