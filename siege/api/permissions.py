from __future__ import annotations

from dataclasses import dataclass


_COUNTRY_SLUG_BY_PAYS_CODE: dict[str, str] = {
    "BRESIL": "bresil",
    "EQUATEUR": "equateur",
    "COLOMBIE": "colombie",
}

_ALERT_RECIPIENT_BY_PAYS_CODE: dict[str, str] = {
    "SIEGE": "admin@futurekawa.com",
    "BRESIL": "resp.br@futurekawa.com",
    "EQUATEUR": "resp.eq@futurekawa.com",
    "COLOMBIE": "resp.co@futurekawa.com",
}


@dataclass(frozen=True)
class UserPermissions:
    """
    Règles dérivées UNIQUEMENT du token JWT courant: role + pays_code.
    """

    role: str
    pays_code: str | None

    @staticmethod
    def from_jwt_user(user: dict) -> "UserPermissions":
        return UserPermissions(
            role=str(user.get("role") or "USER").upper(),
            pays_code=(str(user.get("pays_code")).upper() if user.get("pays_code") else None),
        )

    def is_admin(self) -> bool:
        return self.role == "ADMIN"

    def is_siege_user(self) -> bool:
        return self.role == "USER" and (self.pays_code or "").upper() == "SIEGE"

    def can_manage_users(self) -> bool:
        return self.is_admin()

    def can_config_iot_thresholds(self) -> bool:
        return self.is_admin()

    def can_write_lots(self) -> bool:
        if self.is_admin():
            return True
        # User siège: lecture seule
        if self.is_siege_user():
            return False
        # Users pays: écriture sur leur pays uniquement (le filtrage pays se fait route/service)
        return self.role == "USER" and self.pays_code in _COUNTRY_SLUG_BY_PAYS_CODE

    def can_view_multi_pays(self) -> bool:
        return self.is_admin() or self.is_siege_user()

    def allowed_pays_slugs(self) -> set[str] | None:
        """
        - None: accès à tous les pays (ADMIN + USER/SIEGE).
        - set([...]): accès restreint aux slugs de pays autorisés.
        """
        if self.can_view_multi_pays():
            return None
        if not self.pays_code:
            return set()
        slug = _COUNTRY_SLUG_BY_PAYS_CODE.get(self.pays_code)
        return {slug} if slug else set()

    def getAlertRecipientByPays(self, pays_code: str) -> str | None:
        return _ALERT_RECIPIENT_BY_PAYS_CODE.get((pays_code or "").upper())

