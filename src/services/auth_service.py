from typing import Any


class AuthService:
    def __init__(self, corba_client):
        self.corba_client = corba_client

    def login(
        self,
        username: str,
        password: str,
    ) -> Any:

        service = self.corba_client.get_auth_service()

        return service.login(
            username,
            password,
        )