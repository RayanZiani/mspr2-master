"""Accès lecture au compte utilisateur en base."""

from sqlalchemy import text

from api.db.database import SessionLocal


GET_USER_SQL = text("""
    SELECT username, password_hash, role, active, pays_code, email
    FROM user_account
    WHERE username = :username
    LIMIT 1
""")


async def get_user_account(username: str) -> dict | None:
    """Charge un compte utilisateur par nom d'utilisateur."""
    async with SessionLocal() as session:
        result = await session.execute(GET_USER_SQL, {"username": username})
        row = result.mappings().first()
        return dict(row) if row else None
