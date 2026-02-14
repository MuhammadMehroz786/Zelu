import uuid
from datetime import datetime, timezone

from app import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pipeline_run_id = db.Column(db.String(36), db.ForeignKey("pipeline_runs.id"), nullable=False, index=True)
    name = db.Column(db.String(500), nullable=False)
    niche = db.Column(db.String(255), nullable=False)
    product_type = db.Column(
        db.String(50),
        nullable=False,
        default="main",
    )  # main | bonus | upsell | order_bump
    status = db.Column(
        db.String(20),
        nullable=False,
        default="draft",
        index=True,
    )  # draft | review | approved | published
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=True)
    blueprint = db.Column(db.JSON, nullable=True)  # product structure from Phase 4
    content = db.Column(db.JSON, nullable=True)  # written content from Phase 5
    assets = db.Column(db.JSON, nullable=True, default=dict)  # file paths, URLs, cover images
    funnel_url = db.Column(db.String(500), nullable=True)
    stripe_product_id = db.Column(db.String(100), nullable=True)
    stripe_price_id = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    published_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    ad_performances = db.relationship("AdPerformance", backref="product", lazy="dynamic")
    learning_logs = db.relationship("LearningLog", backref="product", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "pipeline_run_id": self.pipeline_run_id,
            "name": self.name,
            "niche": self.niche,
            "product_type": self.product_type,
            "status": self.status,
            "description": self.description,
            "price": self.price,
            "assets": self.assets,
            "funnel_url": self.funnel_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
        }
