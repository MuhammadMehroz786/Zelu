"""Learning service — feedback loops and performance tracking."""

import structlog
from datetime import date, timedelta

from app import db
from app.models.learning import LearningLog
from app.models.ad_performance import AdPerformance
from app.models.product import Product

logger = structlog.get_logger(__name__)


def get_niche_insights(niche: str, phase_number: int = None) -> dict:
    """Get accumulated learning insights for a niche."""
    query = LearningLog.query.filter(
        LearningLog.niche == niche,
        LearningLog.feedback.in_(["approved", "edited"]),
    )

    if phase_number:
        query = query.filter(LearningLog.phase_number == phase_number)

    logs = query.order_by(LearningLog.performance_score.desc().nullslast()).limit(10).all()

    return {
        "niche": niche,
        "total_data_points": len(logs),
        "insights": [
            {
                "phase": log.phase_number,
                "summary": log.output_summary,
                "score": log.performance_score,
                "feedback": log.feedback,
            }
            for log in logs
        ],
    }


def sync_all_ad_performance():
    """Sync Meta Ads performance data for all active products."""
    products = Product.query.filter_by(status="published").all()

    for product in products:
        if not product.assets:
            continue

        campaign_id = (product.assets or {}).get("campaign_id")
        if not campaign_id:
            continue

        try:
            from app.integrations.meta_ads import get_campaign_insights
            insights = get_campaign_insights(campaign_id)

            for day_data in insights.get("data", []):
                _save_daily_performance(product.id, campaign_id, day_data)

            # Update learning log scores
            _update_learning_scores(product)

        except Exception as e:
            logger.warning("sync.product.failed", product_id=product.id, error=str(e))


def _save_daily_performance(product_id: str, campaign_id: str, data: dict):
    """Save daily ad performance data."""
    today = date.today()

    existing = AdPerformance.query.filter_by(
        product_id=product_id,
        campaign_id=campaign_id,
        date=today,
    ).first()

    if existing:
        existing.impressions = int(data.get("impressions", 0))
        existing.clicks = int(data.get("clicks", 0))
        existing.spend = float(data.get("spend", 0))
        existing.ctr = float(data.get("ctr", 0))
        existing.cpc = float(data.get("cpc", 0))
    else:
        perf = AdPerformance(
            product_id=product_id,
            campaign_id=campaign_id,
            impressions=int(data.get("impressions", 0)),
            clicks=int(data.get("clicks", 0)),
            spend=float(data.get("spend", 0)),
            ctr=float(data.get("ctr", 0)),
            cpc=float(data.get("cpc", 0)),
            date=today,
        )
        db.session.add(perf)

    db.session.commit()


def _update_learning_scores(product: Product):
    """Back-fill performance scores on learning logs based on ad data."""
    # Calculate average ROAS for this product
    performances = AdPerformance.query.filter_by(product_id=product.id).all()
    if not performances:
        return

    total_spend = sum(p.spend or 0 for p in performances)
    total_revenue = sum(p.revenue or 0 for p in performances)

    if total_spend > 0:
        roas = total_revenue / total_spend
        # Normalize to 0-100 score (ROAS of 3x = score of 75)
        score = min(100, roas * 25)
    else:
        score = None

    # Update learning logs for this product's pipeline
    logs = LearningLog.query.filter_by(
        pipeline_run_id=product.pipeline_run_id
    ).all()

    for log in logs:
        log.performance_score = score

    db.session.commit()
    logger.info("learning.scores_updated", product_id=product.id, score=score)
