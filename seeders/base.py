"""Shared helpers for idempotent database seeding."""

from dataclasses import dataclass, field

from app.extensions import db


@dataclass
class SeedResult:
    """Tracks inserted and skipped records for a single seeder."""

    name: str
    inserted: int = 0
    skipped: int = 0
    messages: list[str] = field(default_factory=list)

    def record_insert(self, message: str) -> None:
        self.inserted += 1
        self.messages.append(f"  + {message}")

    def record_skip(self, message: str) -> None:
        self.skipped += 1
        self.messages.append(f"  ~ {message}")


def print_section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(title)
    print("=" * 60)


def print_result(result: SeedResult) -> None:
    for message in result.messages:
        print(message)
    print(
        f"  => {result.name}: {result.inserted} inserted, "
        f"{result.skipped} skipped"
    )


def print_summary(results: list[SeedResult]) -> None:
    total_inserted = sum(r.inserted for r in results)
    total_skipped = sum(r.skipped for r in results)

    print(f"\n{'=' * 60}")
    print("SEEDING COMPLETE")
    print("=" * 60)
    print(f"  Total inserted : {total_inserted}")
    print(f"  Total skipped  : {total_skipped}")
    print(f"  Seeders run    : {len(results)}")
    print("=" * 60)


def flush_session() -> None:
    """Flush pending changes so auto-generated IDs are available downstream."""

    db.session.flush()
