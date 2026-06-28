from __future__ import annotations

from dataclasses import dataclass

_ADMIN_ROLES = frozenset({"ADMIN", "SUPER_ADMIN"})


_COUNTRY_SLUG_BY_PAYS_CODE: dict[str, str] = {
    "BRESIL": "bresil",
    "EQUATEUR": "equateur",
    "COLOMBIE": "colombie",
}

_PAYS_CODE_TO_COUNTRY_CODE: dict[str, str] = {
    "BRESIL": "BR",
    "EQUATEUR": "EC",
    "COLOMBIE": "CO",
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
    Regles derivees du token JWT courant: role + pays_code.

    Hierarchie :
    - SUPER_ADMIN : proprietaire plateforme (gestion utilisateurs incluse)
    - ADMIN       : administration operationnelle (seuils, lots, multi-pays)
    - USER        : acces selon pays (SIEGE lecture multi-pays, pays local ecriture lots)
    """

    role: str
    pays_code: str | None

    @staticmethod
    def from_jwt_user(user: dict) -> "UserPermissions":
        return UserPermissions(
            role=str(user.get("role") or "USER").upper(),
            pays_code=(str(user.get("pays_code")).upper() if user.get("pays_code") else None),
        )

    def is_super_admin(self) -> bool:
        return self.role == "SUPER_ADMIN"

    def is_admin(self) -> bool:
        return self.role in _ADMIN_ROLES

    def is_siege_user(self) -> bool:
        return self.role == "USER" and (self.pays_code or "").upper() == "SIEGE"

    def can_manage_users(self) -> bool:
        return self.is_super_admin()

    def can_manage_global_webhook(self) -> bool:
        return self.is_super_admin()

    def can_config_iot_thresholds(self) -> bool:
        if self.is_super_admin():
            return True
        if self.role != "ADMIN" or not self.pays_code:
            return False
        pays = self.pays_code.upper()
        return pays == "SIEGE" or pays in _PAYS_CODE_TO_COUNTRY_CODE

    def allowed_config_country_codes(self) -> set[str] | None:
        """None = tous les pays. Sinon codes BR/EC/CO autorises."""
        if not self.can_config_iot_thresholds():
            return set()
        if self.is_super_admin():
            return None
        pays = (self.pays_code or "").upper()
        if pays == "SIEGE":
            return None
        code = _PAYS_CODE_TO_COUNTRY_CODE.get(pays)
        return {code} if code else set()

    def can_config_iot_thresholds_for(self, country_code: str) -> bool:
        allowed = self.allowed_config_country_codes()
        if not self.can_config_iot_thresholds():
            return False
        if allowed is None:
            return True
        return country_code.upper() in allowed

    def can_write_lots(self) -> bool:
        if self.is_super_admin():
            return True
        if self.role == "ADMIN":
            pays = (self.pays_code or "").upper()
            return pays == "SIEGE" or pays in _PAYS_CODE_TO_COUNTRY_CODE
        if self.is_siege_user():
            return False
        return self.role == "USER" and self.pays_code in _COUNTRY_SLUG_BY_PAYS_CODE

    def can_view_multi_pays(self) -> bool:
        if self.is_super_admin():
            return True
        if self.role == "ADMIN" and (self.pays_code or "").upper() == "SIEGE":
            return True
        return self.is_siege_user()

    def allowed_pays_slugs(self) -> set[str] | None:
        if self.can_view_multi_pays():
            return None
        if not self.pays_code:
            return set()
        slug = _COUNTRY_SLUG_BY_PAYS_CODE.get(self.pays_code)
        return {slug} if slug else set()

    def get_alert_recipient_by_pays(self, pays_code: str) -> str | None:
        return _ALERT_RECIPIENT_BY_PAYS_CODE.get((pays_code or "").upper())
