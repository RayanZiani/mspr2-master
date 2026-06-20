"""Applique database/migrations/001_add_super_admin_role.sql sur Aiven."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from aiven_mysql import connect_aiven


def main() -> int:
    cnx = connect_aiven(autocommit=True)
    cur = cnx.cursor()
    try:
        cur.execute(
            """
            ALTER TABLE user_account
            MODIFY role ENUM('SUPER_ADMIN', 'ADMIN', 'USER') NOT NULL DEFAULT 'USER'
            """
        )
        print("OK: ALTER TABLE user_account ... SUPER_ADMIN")
        cur.execute(
            """
            UPDATE user_account
            SET role = 'SUPER_ADMIN'
            WHERE username = 'admin_siege' AND role = 'ADMIN'
            """
        )
        print(f"OK: UPDATE admin_siege ({cur.rowcount} row(s))")
        cur.execute("SELECT username, role FROM user_account WHERE username = %s", ("admin_siege",))
        row = cur.fetchone()
        print(f"admin_siege -> role={row[1] if row else 'NOT FOUND'}")
    finally:
        cur.close()
        cnx.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
