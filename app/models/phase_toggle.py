from app import db


class PhaseToggle(db.Model):
    __tablename__ = "phase_toggles"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phase_number = db.Column(db.Integer, nullable=False, unique=True)
    phase_name = db.Column(db.String(100), nullable=False)
    requires_approval = db.Column(db.Boolean, nullable=False, default=True)
    is_enabled = db.Column(db.Boolean, nullable=False, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "phase_number": self.phase_number,
            "phase_name": self.phase_name,
            "requires_approval": self.requires_approval,
            "is_enabled": self.is_enabled,
        }

    @staticmethod
    def seed_defaults(db_session):
        """Seed the default phase toggles if they don't exist."""
        defaults = [
            (1, "Trend Discovery"),
            (2, "Niche Validation"),
            (3, "Audience & Pain Points"),
            (4, "Product Structure"),
            (5, "Content Writing"),
            (6, "Visual Design"),
            (7, "Funnel & Copy"),
            (8, "Campaign Launch"),
        ]
        for phase_num, phase_name in defaults:
            existing = PhaseToggle.query.filter_by(phase_number=phase_num).first()
            if not existing:
                toggle = PhaseToggle(
                    phase_number=phase_num,
                    phase_name=phase_name,
                    requires_approval=True,
                    is_enabled=True,
                )
                db_session.add(toggle)
        db_session.commit()
