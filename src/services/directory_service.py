from typing import Any

class DirectoryService:
    def __init__(self, corba_client):
        self.corba_client = corba_client

    def list_doctors(self) -> list[Any]:
        return list(self.corba_client.get_directory_service().listDoctors())

    def list_specialties(self) -> list[Any]:
        return list(self.corba_client.get_directory_service().listSpecialties())

    def list_all_doctors(self) -> list[Any]:
        return list(self.corba_client.get_directory_service().listAllDoctors())

    def list_all_specialties(self) -> list[Any]:
        return list(self.corba_client.get_directory_service().listAllSpecialties())

    def create_doctor(self, full_name: str, specialty_id: int) -> Any:
        return self.corba_client.get_directory_service().createDoctor(full_name, specialty_id)

    def update_doctor(self, doctor_id: int, full_name: str, specialty_id: int) -> Any:
        return self.corba_client.get_directory_service().updateDoctor(doctor_id, full_name, specialty_id)

    def set_doctor_active(self, doctor_id: int, active: bool) -> None:
        self.corba_client.get_directory_service().setDoctorActive(doctor_id, active)

    def create_specialty(self, name: str) -> Any:
        return self.corba_client.get_directory_service().createSpecialty(name)

    def update_specialty(self, specialty_id: int, name: str) -> Any:
        return self.corba_client.get_directory_service().updateSpecialty(specialty_id, name)

    def set_specialty_active(self, specialty_id: int, active: bool) -> None:
        self.corba_client.get_directory_service().setSpecialtyActive(specialty_id, active)
