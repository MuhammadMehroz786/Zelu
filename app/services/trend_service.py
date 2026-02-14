"""Trend analysis service — scoring and ranking trend signals."""

import structlog

logger = structlog.get_logger(__name__)


def score_trend_signals(signals: dict) -> list:
    """Score and rank trend signals for digital product potential."""
    scored = []

    # Google Trends signals
    trends = signals.get("google_trends", {})
    if isinstance(trends, dict) and "interest_over_time" in trends:
        timeline = trends["interest_over_time"].get("timeline_data", [])
        if timeline:
            # Check if trend is growing
            values = [int(t.get("values", [{}])[0].get("value", 0)) for t in timeline[-6:]]
            if len(values) >= 2:
                growth = (values[-1] - values[0]) / max(values[0], 1) * 100
                scored.append({
                    "source": "google_trends",
                    "growth_percent": round(growth, 1),
                    "recent_interest": values[-1],
                    "signal": "growing" if growth > 10 else "stable" if growth > -10 else "declining",
                })

    # Reddit signals
    reddit = signals.get("reddit", [])
    if isinstance(reddit, list) and reddit:
        avg_score = sum(p.get("score", 0) for p in reddit) / len(reddit)
        avg_comments = sum(p.get("num_comments", 0) for p in reddit) / len(reddit)
        scored.append({
            "source": "reddit",
            "avg_engagement": round(avg_score, 1),
            "avg_discussion": round(avg_comments, 1),
            "signal": "high_interest" if avg_comments > 20 else "moderate" if avg_comments > 5 else "low",
        })

    # Hotmart signals
    hotmart = signals.get("hotmart", {})
    products = hotmart.get("products", [])
    if products:
        scored.append({
            "source": "hotmart",
            "existing_products": len(products),
            "signal": "validated_market" if len(products) > 3 else "emerging",
        })

    return scored
