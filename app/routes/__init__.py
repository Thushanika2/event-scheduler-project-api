def register_blueprints(app):
    from app.routes.agenda_routes import agenda_bp
    from app.routes.attendee_routes import attendees_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.organiser_routes import organisers_bp
    from app.routes.session_routes import organiser_sessions_bp, sessions_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(attendees_bp)
    app.register_blueprint(organisers_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(organiser_sessions_bp)
    app.register_blueprint(agenda_bp)
