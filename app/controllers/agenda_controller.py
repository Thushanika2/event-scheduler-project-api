from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.extensions import db
from app.models.agenda_item_model import AgendaItem
from app.models.session_model import Session


def _sessions_overlap(session_a, session_b):
    return session_a.start_time < session_b.end_time and session_b.start_time < session_a.end_time


def add_to_agenda(attendee_id, data):
    session_id = data.get("session_id")
    if not session_id:
        return {"errors": ["Session ID is required."]}, 400

    session = Session.query.get(session_id)
    if not session:
        return {"error": "Session not found."}, 404

    existing = AgendaItem.query.filter_by(
        attendee_id=attendee_id, session_id=session_id
    ).first()
    if existing:
        return {"error": "Session is already in your agenda."}, 400

    booking_count = AgendaItem.query.filter_by(session_id=session_id).count()
    if booking_count >= session.capacity:
        return {"error": "Session is full."}, 400

    existing_items = (
        AgendaItem.query.filter_by(attendee_id=attendee_id)
        .join(Session)
        .all()
    )

    clash_sessions = []
    for item in existing_items:
        if _sessions_overlap(item.session, session):
            clash_sessions.append(item.session.title)

    try:
        agenda_item = AgendaItem(attendee_id=attendee_id, session_id=session_id)
        db.session.add(agenda_item)
        db.session.commit()

        response = {
            "message": "Session added to agenda.",
            "agenda_item": agenda_item.to_dict(include_session=True),
        }
        if clash_sessions:
            response["warning"] = (
                f"Time clash detected with: {', '.join(clash_sessions)}"
            )
        return response, 201
    except Exception:
        db.session.rollback()
        return {"error": "Failed to add session to agenda."}, 500


def get_my_agenda(attendee_id):
    items = (
        AgendaItem.query.filter_by(attendee_id=attendee_id)
        .join(Session)
        .order_by(Session.start_time.asc())
        .all()
    )
    return {
        "agenda_items": [item.to_dict(include_session=True) for item in items],
    }, 200


def delete_agenda_item(agenda_item_id, attendee_id):
    item = AgendaItem.query.get(agenda_item_id)
    if not item:
        return {"error": "Agenda item not found."}, 404
    if item.attendee_id != attendee_id:
        return {"error": "Forbidden."}, 403

    try:
        db.session.delete(item)
        db.session.commit()
        return {"message": "Session removed from agenda."}, 200
    except Exception:
        db.session.rollback()
        return {"error": "Failed to remove session from agenda."}, 500


def download_my_agenda(attendee_id):
    items = (
        AgendaItem.query.filter_by(attendee_id=attendee_id)
        .join(Session)
        .order_by(Session.start_time.asc())
        .all()
    )

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph("My Agenda", styles["Title"]), Spacer(1, 12)]

    if not items:
        story.append(Paragraph("No sessions in your agenda.", styles["Normal"]))
    else:
        for item in items:
            session = item.session
            line = (
                f"<b>{session.title}</b> — {session.speaker}<br/>"
                f"Track: {session.track} | Room: {session.room}<br/>"
                f"{session.start_time.strftime('%Y-%m-%d %H:%M')} – "
                f"{session.end_time.strftime('%H:%M')}"
            )
            story.append(Paragraph(line, styles["Normal"]))
            story.append(Spacer(1, 8))

    doc.build(story)
    buffer.seek(0)
    return buffer, f"agenda_{attendee_id}.pdf"
