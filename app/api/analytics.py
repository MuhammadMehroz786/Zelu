"""Analytics API — learning logs, ad performance, system stats."""

from flask import Blueprint, request, jsonify
from sqlalchemy import func

from app import db
from app.models.learning import LearningLog
from app.models.ad_performance import AdPerformance
from app.models.product import Product
from app.models.pipeline_run import PipelineRun
from app.models.phase_toggle import PhaseToggle

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/learning", methods=["GET"])
def learning_logs():
    """Get learning logs with filters."""
    niche = request.args.get("niche")
    phase = request.args.get("phase", type=int)
    feedback = request.args.get("feedback")

    query = LearningLog.query.order_by(LearningLog.created_at.desc())

    if niche:
        query = query.filter(LearningLog.niche == niche)
    if phase:
        query = query.filter(LearningLog.phase_number == phase)
    if feedback:
        query = query.filter(LearningLog.feedback == feedback)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    pagination = query.paginate(page=page, per_page=per_page)

    return jsonify({
        "logs": [l.to_dict() for l in pagination.items],
        "total": pagination.total,
        "page": page,
    })


@analytics_bp.route("/ads", methods=["GET"])
def ad_performance():
    """Get ad performance data."""
    product_id = request.args.get("product_id")

    query = AdPerformance.query.order_by(AdPerformance.date.desc())

    if product_id:
        query = query.filter(AdPerformance.product_id == product_id)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    pagination = query.paginate(page=page, per_page=per_page)

    return jsonify({
        "performance": [p.to_dict() for p in pagination.items],
        "total": pagination.total,
        "page": page,
    })


@analytics_bp.route("/dashboard", methods=["GET"])
def dashboard_stats():
    """Get dashboard summary statistics."""
    total_pipelines = PipelineRun.query.count()
    completed_pipelines = PipelineRun.query.filter_by(status="completed").count()
    total_products = Product.query.count()
    published_products = Product.query.filter_by(status="published").count()

    # Top niches by product count
    top_niches = db.session.query(
        Product.niche, func.count(Product.id).label("count")
    ).group_by(Product.niche).order_by(func.count(Product.id).desc()).limit(10).all()

    # Approval rate by phase
    approval_stats = db.session.query(
        LearningLog.phase_number,
        LearningLog.feedback,
        func.count(LearningLog.id).label("count"),
    ).group_by(LearningLog.phase_number, LearningLog.feedback).all()

    # Total ad spend and revenue
    ad_totals = db.session.query(
        func.sum(AdPerformance.spend).label("total_spend"),
        func.sum(AdPerformance.revenue).label("total_revenue"),
        func.sum(AdPerformance.clicks).label("total_clicks"),
        func.sum(AdPerformance.impressions).label("total_impressions"),
    ).first()

    return jsonify({
        "pipelines": {
            "total": total_pipelines,
            "completed": completed_pipelines,
        },
        "products": {
            "total": total_products,
            "published": published_products,
        },
        "top_niches": [{"niche": n, "count": c} for n, c in top_niches],
        "approval_stats": [
            {"phase": p, "feedback": f, "count": c}
            for p, f, c in approval_stats
        ],
        "ad_totals": {
            "spend": float(ad_totals.total_spend or 0),
            "revenue": float(ad_totals.total_revenue or 0),
            "clicks": int(ad_totals.total_clicks or 0),
            "impressions": int(ad_totals.total_impressions or 0),
        },
    })


@analytics_bp.route("/toggles", methods=["GET"])
def get_toggles():
    """Get all phase toggle settings."""
    toggles = PhaseToggle.query.order_by(PhaseToggle.phase_number).all()
    return jsonify({"toggles": [t.to_dict() for t in toggles]})


@analytics_bp.route("/toggles", methods=["PUT"])
def update_toggles():
    """Update phase toggle settings."""
    data = request.get_json()
    toggles_data = data.get("toggles", [])

    for toggle_data in toggles_data:
        toggle = PhaseToggle.query.filter_by(
            phase_number=toggle_data["phase_number"]
        ).first()

        if toggle:
            if "requires_approval" in toggle_data:
                toggle.requires_approval = toggle_data["requires_approval"]
            if "is_enabled" in toggle_data:
                toggle.is_enabled = toggle_data["is_enabled"]

    db.session.commit()

    toggles = PhaseToggle.query.order_by(PhaseToggle.phase_number).all()
    return jsonify({"toggles": [t.to_dict() for t in toggles]})
