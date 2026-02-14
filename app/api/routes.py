"""Main API blueprint — registers all route modules."""

from flask import Blueprint

api_bp = Blueprint("api", __name__)

# Import and register sub-routes
from app.api.pipeline import pipeline_bp
from app.api.prompts import prompts_bp
from app.api.approvals import approvals_bp
from app.api.analytics import analytics_bp

api_bp.register_blueprint(pipeline_bp, url_prefix="/pipelines")
api_bp.register_blueprint(prompts_bp, url_prefix="/prompts")
api_bp.register_blueprint(approvals_bp, url_prefix="/approvals")
api_bp.register_blueprint(analytics_bp, url_prefix="/analytics")
