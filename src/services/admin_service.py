from typing import Any


class AdminService:
    def __init__(self, corba_client):
        self.corba_client = corba_client

    def audit_logs(self, token: str, from_date: str, to_date: str) -> list[Any]:
        return list(self.corba_client.get_admin_service().listAuditLogs(token, from_date, to_date))

    def settings(self, token: str) -> list[Any]:
        return list(self.corba_client.get_admin_service().listSettings(token))

    def set_setting(self, token: str, key: str, value: str) -> None:
        self.corba_client.get_admin_service().setSetting(token, key, value)
