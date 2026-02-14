"""Prompts API — CRUD for editable prompt templates."""

from datetime import datetime, timezone
from flask import Blueprint, request, jsonify

from app import db
from app.models.prompt_template import PromptTemplate

prompts_bp = Blueprint("prompts", __name__)


@prompts_bp.route("/", methods=["GET"])
def list_prompts():
    """List all active prompt templates, grouped by phase."""
    prompts = PromptTemplate.query.filter_by(is_active=True).order_by(
        PromptTemplate.phase_number, PromptTemplate.template_key
    ).all()

    grouped = {}
    for p in prompts:
        phase_key = f"phase_{p.phase_number}"
        if phase_key not in grouped:
            grouped[phase_key] = []
        grouped[phase_key].append(p.to_dict())

    return jsonify({"prompts": grouped})


@prompts_bp.route("/<prompt_id>", methods=["GET"])
def get_prompt(prompt_id):
    """Get a single prompt template."""
    prompt = PromptTemplate.query.get(prompt_id)
    if not prompt:
        return jsonify({"error": "Prompt not found"}), 404
    return jsonify(prompt.to_dict())


@prompts_bp.route("/<prompt_id>", methods=["PUT"])
def update_prompt(prompt_id):
    """Update a prompt template — creates a new version."""
    existing = PromptTemplate.query.get(prompt_id)
    if not existing:
        return jsonify({"error": "Prompt not found"}), 404

    data = request.get_json()

    # Deactivate old version
    existing.is_active = False
    db.session.flush()

    # Create new version
    new_prompt = PromptTemplate(
        phase_number=existing.phase_number,
        agent_name=existing.agent_name,
        name=existing.name,
        template_key=existing.template_key,
        template=data.get("template", existing.template),
        variables=data.get("variables", existing.variables),
        version=existing.version + 1,
        is_active=True,
    )
    db.session.add(new_prompt)
    db.session.commit()

    return jsonify(new_prompt.to_dict())


@prompts_bp.route("/", methods=["POST"])
def create_prompt():
    """Create a new prompt template."""
    data = request.get_json()

    required = ["phase_number", "agent_name", "name", "template_key", "template"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    prompt = PromptTemplate(
        phase_number=data["phase_number"],
        agent_name=data["agent_name"],
        name=data["name"],
        template_key=data["template_key"],
        template=data["template"],
        variables=data.get("variables", []),
    )
    db.session.add(prompt)
    db.session.commit()

    return jsonify(prompt.to_dict()), 201


@prompts_bp.route("/<prompt_id>/test", methods=["POST"])
def test_prompt(prompt_id):
    """Test a prompt with sample variables and return the AI response."""
    prompt = PromptTemplate.query.get(prompt_id)
    if not prompt:
        return jsonify({"error": "Prompt not found"}), 404

    data = request.get_json()
    variables = data.get("variables", {})

    rendered = prompt.render(**variables)

    # Call OpenAI to test
    from app.integrations.openai_client import call_openai
    response = call_openai(rendered, json_mode=False)

    return jsonify({
        "rendered_prompt": rendered,
        "ai_response": response,
    })


@prompts_bp.route("/<prompt_id>/history", methods=["GET"])
def prompt_history(prompt_id):
    """Get version history for a prompt template."""
    prompt = PromptTemplate.query.get(prompt_id)
    if not prompt:
        return jsonify({"error": "Prompt not found"}), 404

    versions = PromptTemplate.query.filter_by(
        template_key=prompt.template_key
    ).order_by(PromptTemplate.version.desc()).all()

    return jsonify({"versions": [v.to_dict() for v in versions]})
