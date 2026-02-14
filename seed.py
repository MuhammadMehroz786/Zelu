"""Seed script — initializes database with default data."""

import yaml
import os
from app import create_app, db
from app.models.phase_toggle import PhaseToggle
from app.models.prompt_template import PromptTemplate


def seed_toggles():
    """Seed default phase toggles."""
    PhaseToggle.seed_defaults(db.session)
    print("Phase toggles seeded.")


def seed_prompts():
    """Seed prompt templates from YAML config files."""
    prompts_dir = os.path.join(os.path.dirname(__file__), "config", "prompts")

    for filename in os.listdir(prompts_dir):
        if not filename.endswith(".yaml"):
            continue

        filepath = os.path.join(prompts_dir, filename)
        with open(filepath, "r") as f:
            config = yaml.safe_load(f)

        agent_name = config.get("agent", "")
        phase_number = config.get("phase", 0)
        prompt_name = config.get("name", "")
        variables = config.get("variables", [])

        for template_key, template_text in config.get("templates", {}).items():
            existing = PromptTemplate.query.filter_by(
                template_key=template_key, is_active=True
            ).first()

            if not existing:
                prompt = PromptTemplate(
                    phase_number=phase_number,
                    agent_name=agent_name,
                    name=f"{prompt_name} - {template_key}",
                    template_key=template_key,
                    template=template_text,
                    variables=variables,
                )
                db.session.add(prompt)

    db.session.commit()
    print("Prompt templates seeded.")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_toggles()
        seed_prompts()
        print("Database seeded successfully.")
