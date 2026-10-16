from typing import Any


class UserService:
    def __init__(self, corba_client):
        self.corba_client = corba_client

    def list_users(self, token: str) -> list[Any]:
        return list(self.corba_client.get_user_service().listUsers(token))

    def create_user(self, token: str, username: str, full_name: str, role: str, initial_password: str) -> Any:
        return self.corba_client.get_user_service().createUser(token, username, full_name, role, initial_password)

    def set_active(self, token: str, user_id: int, active: bool) -> None:
        self.corba_client.get_user_service().setUserActive(token, user_id, active)

    def reset_password(self, token: str, user_id: int, password: str) -> None:
        self.corba_client.get_user_service().resetPassword(token, user_id, password)

    def change_password(self, token: str, current_password: str, new_password: str) -> None:
        self.corba_client.get_user_service().changePassword(token, current_password, new_password)
