import uuid
from datetime import datetime, timezone

from app import db


class LearningLog(db.Model):
    __tablename__ = "learning_logs"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = db.Column(db.String(36), db.ForeignKey("products.id"), nullable=True, index=True)
    pipeline_run_id = db.Column(db.String(36), db.ForeignKey("pipeline_runs.id"), nullable=False, index=True)
    phase_number = db.Column(db.Integer, nullable=False)
    agent_name = db.Column(db.String(100), nullable=False)
    prompt_used = db.Column(db.Text, nullable=True)
    output_summary = db.Column(db.Text, nullable=True)
    feedback = db.Column(
        db.String(20),
        nullable=True,
    )  # approved | rejected | edited
    performance_score = db.Column(db.Float, nullable=True)  # filled later from ad_performance
    niche = db.Column(db.String(255), nullable=True, index=True)
    tags = db.Column(db.JSON, nullable=True, default=list)
    metadata = db.Column(db.JSON, nullable=True, default=dict)  # extra context
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "pipeline_run_id": self.pipeline_run_id,
            "phase_number": self.phase_number,
            "agent_name": self.agent_name,
            "output_summary": self.output_summary,
            "feedback": self.feedback,
            "performance_score": self.performance_score,
            "niche": self.niche,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
