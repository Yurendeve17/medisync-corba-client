from typing import Any

class DirectoryService:
    def __init__(self, corba_client): self.corba_client=corba_client
    def list_doctors(self) -> list[Any]: return list(self.corba_client.get_directory_service().listDoctors())
    def list_specialties(self) -> list[Any]: return list(self.corba_client.get_directory_service().listSpecialties())
