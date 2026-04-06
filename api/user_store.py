import json
import re
from datetime import datetime
from pathlib import Path

from sqlalchemy import desc
from sqlalchemy.orm import Session

from api.db_models import User, UserBadge, WorkoutHistory


ALLOWED_NAME_RE = re.compile(r"^[A-Za-z0-9 _.-]+$")


def normalize_name(name: str) -> str:
    """Normalize and validate username.

    Args:
        name: Raw username input.

    Returns:
        str: Cleaned username.

    Raises:
        ValueError: If name is empty, too long, or contains invalid characters.
    """
    cleaned = str(name or "").strip()
    if not cleaned:
        raise ValueError("User name cannot be empty")
    if len(cleaned) > 40:
        raise ValueError("User name cannot exceed 40 characters")
    if not ALLOWED_NAME_RE.match(cleaned):
        raise ValueError(
            "User name can contain only letters, numbers, spaces, _, -, and .")
    return cleaned


def create_user_if_missing(db: Session, name: str) -> User:
    """Create user if not exists, else return existing.

    Args:
        db: Database session.
        name: Username.

    Returns:
        User: User instance (new or existing).
    """
    cleaned_name = normalize_name(name)
    user = db.query(User).filter(User.name == cleaned_name).first()
    if user:
        return user

    user = User(name=cleaned_name, xp=0, level=1)
    db.add(user)
    db.flush()
    return user


def get_user_by_name(db: Session, name: str) -> User | None:
    """Fetch user from database by name.

    Args:
        db: Database session.
        name: Username.

    Returns:
        User or None if not found.
    """
    cleaned_name = normalize_name(name)
    return db.query(User).filter(User.name == cleaned_name).first()


def user_to_dict(user: User, include_history: bool = True) -> dict:
    """Convert User object to dictionary payload.

    Args:
        user: User instance.
        include_history: Whether to include workout history.

    Returns:
        dict: User data with XP, level, badges, and optionally history.
    """
    payload = {
        "xp": int(user.xp or 0),
        "level": int(user.level or 1),
        "badges": sorted([badge.badge_name for badge in user.badges]),
    }

    if include_history:
        payload["history"] = [
            {
                "date": item.performed_at.isoformat(),
                "reps": int(item.reps or 0),
                "exercise": item.exercise,
            }
            for item in sorted(user.history, key=lambda h: h.performed_at)
        ]

    return payload


def list_users_payload(db: Session) -> dict:
    users = db.query(User).order_by(User.name.asc()).all()
    payload = {user.name: user_to_dict(user, include_history=True) for user in users}
    return {"count": len(payload), "users": payload}


def update_user(
    db: Session,
    user: User,
    xp: int | None = None,
    level: int | None = None,
) -> User:
    """Update user XP and level.

    Args:
        db: Database session.
        user: User to update.
        xp: New XP value (must be >= 0).
        level: New level (must be >= 1).

    Returns:
        User: Updated user instance.
    """
    if xp is not None:
        user.xp = max(0, int(xp))
    if level is not None:
        user.level = max(1, int(level))
    db.flush()
    return user


def set_user_badges(db: Session, user: User, badges: list[str]) -> None:
    unique_badges = sorted(set(str(b).strip() for b in badges if str(b).strip()))

    existing = {badge.badge_name: badge for badge in user.badges}
    for badge_name, badge_row in existing.items():
        if badge_name not in unique_badges:
            db.delete(badge_row)

    for badge_name in unique_badges:
        if badge_name in existing:
            continue
        db.add(UserBadge(user_id=user.id, badge_name=badge_name))

    db.flush()


def add_badges(db: Session, user: User, new_badges: list[str]) -> None:
    """Add new badges to user, skipping duplicates.

    Args:
        db: Database session.
        user: User instance.
        new_badges: List of badge names to add.
    """
    existing = {badge.badge_name for badge in user.badges}
    for badge_name in set(new_badges):
        clean = str(badge_name).strip()
        if not clean or clean in existing:
            continue
        db.add(UserBadge(user_id=user.id, badge_name=clean))
    db.flush()


def add_history_item(
    db: Session,
    user: User,
    reps: int,
    exercise: str,
    when: datetime | None = None,
) -> None:
    """Record workout entry in user history.

    Args:
        db: Database session.
        user: User instance.
        reps: Reps completed.
        exercise: Exercise name.
        when: Timestamp (defaults to now).
    """
    clean_exercise = str(exercise or "").strip()
    if not clean_exercise:
        raise ValueError("Exercise cannot be empty")

    clean_reps = int(reps)
    if clean_reps < 0:
        raise ValueError("Reps must be 0 or greater")

    db.add(
        WorkoutHistory(
            user_id=user.id,
            reps=clean_reps,
            exercise=clean_exercise,
            performed_at=when or datetime.utcnow(),
        )
    )
    db.flush()


def get_user_history_payload(db: Session, name: str) -> list[dict]:
    user = get_user_by_name(db, name)
    if not user:
        return []

    rows = (
        db.query(WorkoutHistory)
        .filter(WorkoutHistory.user_id == user.id)
        .order_by(WorkoutHistory.performed_at.asc())
        .all()
    )

    return [
        {
            "date": row.performed_at.isoformat(),
            "reps": int(row.reps or 0),
            "exercise": row.exercise,
        }
        for row in rows
    ]


def get_leaderboard_payload(db: Session, top_n: int = 10) -> list[dict]:
    """Get top N users ranked by XP.

    Args:
        db: Database session.
        top_n: Number of top users to return.

    Returns:
        list: User objects sorted by XP descending.
    """
    rows = db.query(User).order_by(desc(User.xp), User.name.asc()).limit(top_n).all()
    return [{"name": row.name, "xp": int(row.xp or 0)} for row in rows]


def import_legacy_json_if_empty(db: Session, json_path: Path) -> int:
    """One-time migration: import legacy JSON data to database if db is empty.

    Args:
        db: Database session.
        json_path: Path to legacy players.json file.

    Returns:
        int: Number of users imported (0 if none).
    """
    user_count = db.query(User).count()
    if user_count > 0 or not json_path.exists():
        return 0

    try:
        with open(json_path, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return 0

    if not isinstance(raw, dict):
        return 0

    imported = 0
    for name, record in raw.items():
        if not isinstance(record, dict):
            continue

        try:
            user = create_user_if_missing(db, str(name))
        except ValueError:
            continue

        update_user(db, user, xp=int(record.get("xp", 0) or 0),
                    level=int(record.get("level", 1) or 1))

        badges = record.get("badges", [])
        if isinstance(badges, list):
            set_user_badges(db, user, [str(b) for b in badges])

        history = record.get("history", [])
        if isinstance(history, list):
            for entry in history:
                if not isinstance(entry, dict):
                    continue
                raw_date = str(entry.get("date", "")).strip()
                parsed_date = None
                if raw_date:
                    try:
                        parsed_date = datetime.fromisoformat(raw_date)
                    except ValueError:
                        parsed_date = None

                add_history_item(
                    db,
                    user,
                    reps=int(entry.get("reps", 0) or 0),
                    exercise=str(entry.get("exercise", "Unknown")),
                    when=parsed_date,
                )

        imported += 1

    return imported
