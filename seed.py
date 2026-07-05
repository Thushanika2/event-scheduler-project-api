"""
AgendaFlow database seeder entry point.

Runs all seeders in dependency order inside a single transaction.
Re-running this script is safe — existing records are skipped.
"""

import sys

from app import create_app
from app.extensions import db
from seeders.agenda_item_seeder import seed_agenda_items
from seeders.attendee_seeder import seed_attendees
from seeders.base import print_result, print_section, print_summary
from seeders.organiser_seeder import seed_organisers
from seeders.session_seeder import seed_sessions
from seeders.user_seeder import DEFAULT_PASSWORD, seed_users

# Seeders must run in this order to satisfy foreign key dependencies.
SEEDERS = [
    ("Users", seed_users),
    ("Organisers", seed_organisers),
    ("Attendees", seed_attendees),
    ("Sessions", seed_sessions),
    ("Agenda Items", seed_agenda_items),
]


def run_seeders() -> int:
    """Execute all seeders and return a process exit code."""

    app = create_app()

    with app.app_context():
        print_section("AgendaFlow Database Seeder")
        print(f"  Default password for seeded accounts: {DEFAULT_PASSWORD}")
        print("  Idempotent mode: existing records will be skipped.")

        results = []

        try:
            for label, seeder in SEEDERS:
                print_section(f"Seeding {label}")
                result = seeder()
                print_result(result)
                results.append(result)

            db.session.commit()
            print_summary(results)
            return 0

        except Exception as exc:
            db.session.rollback()
            print("\n" + "=" * 60)
            print("SEEDING FAILED — ALL CHANGES ROLLED BACK")
            print("=" * 60)
            print(f"  Error: {exc}")
            return 1


if __name__ == "__main__":
    sys.exit(run_seeders())
