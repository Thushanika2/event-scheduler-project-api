from app.extensions import db


class Organiser(db.Model):
    __tablename__ = "organisers"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    organisation = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50), nullable=True)

    user = db.relationship("User", back_populates="organiser")
    sessions = db.relationship("Session", back_populates="organiser")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "full_name": self.full_name,
            "organisation": self.organisation,
            "phone": self.phone,
        }
