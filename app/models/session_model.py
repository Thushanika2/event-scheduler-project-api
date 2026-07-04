from app.extensions import db


class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    organiser_id = db.Column(db.Integer, db.ForeignKey("organisers.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    speaker = db.Column(db.String(255), nullable=False)
    track = db.Column(db.String(100), nullable=False)
    room = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    organiser = db.relationship("Organiser", back_populates="sessions")
    agenda_items = db.relationship("AgendaItem", back_populates="session")

    def to_dict(self, include_booking_count=False):
        data = {
            "id": self.id,
            "organiser_id": self.organiser_id,
            "title": self.title,
            "speaker": self.speaker,
            "track": self.track,
            "room": self.room,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "capacity": self.capacity,
        }
        if include_booking_count:
            booking_count = len(self.agenda_items)
            data["booking_count"] = booking_count
            data["is_full"] = booking_count >= self.capacity
        return data
