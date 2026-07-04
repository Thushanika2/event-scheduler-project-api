from app.extensions import db
from app.utils import utc_now


class AgendaItem(db.Model):
    __tablename__ = "agenda_items"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    attendee_id = db.Column(db.Integer, db.ForeignKey("attendees.id"), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"), nullable=False)
    added_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    attendee = db.relationship("Attendee", back_populates="agenda_items")
    session = db.relationship("Session", back_populates="agenda_items")

    __table_args__ = (
        db.UniqueConstraint("attendee_id", "session_id", name="uq_attendee_session"),
    )

    def to_dict(self, include_session=False):
        data = {
            "id": self.id,
            "attendee_id": self.attendee_id,
            "session_id": self.session_id,
            "added_at": self.added_at.isoformat() if self.added_at else None,
        }
        if include_session and self.session:
            data["session"] = self.session.to_dict(include_booking_count=True)
        return data
