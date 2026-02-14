import uuid
from datetime import datetime, timezone

from app import db


class AdPerformance(db.Model):
    __tablename__ = "ad_performance"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = db.Column(db.String(36), db.ForeignKey("products.id"), nullable=False, index=True)
    campaign_id = db.Column(db.String(100), nullable=True)
    ad_set_id = db.Column(db.String(100), nullable=True)
    ad_id = db.Column(db.String(100), nullable=True)
    creative_variant = db.Column(db.String(100), nullable=True)  # which hook/angle was used
    impressions = db.Column(db.Integer, nullable=True, default=0)
    clicks = db.Column(db.Integer, nullable=True, default=0)
    ctr = db.Column(db.Float, nullable=True)
    cpc = db.Column(db.Float, nullable=True)
    conversions = db.Column(db.Integer, nullable=True, default=0)
    roas = db.Column(db.Float, nullable=True)
    spend = db.Column(db.Float, nullable=True, default=0.0)
    revenue = db.Column(db.Float, nullable=True, default=0.0)
    date = db.Column(db.Date, nullable=False)
    fetched_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "campaign_id": self.campaign_id,
            "ad_set_id": self.ad_set_id,
            "ad_id": self.ad_id,
            "creative_variant": self.creative_variant,
            "impressions": self.impressions,
            "clicks": self.clicks,
            "ctr": self.ctr,
            "cpc": self.cpc,
            "conversions": self.conversions,
            "roas": self.roas,
            "spend": self.spend,
            "revenue": self.revenue,
            "date": self.date.isoformat() if self.date else None,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
        }
