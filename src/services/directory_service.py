from typing import Any

class DirectoryService:
    def __init__(self, corba_client):
        self.corba_client = corba_client

    def list_doctors(self) -> list[Any]:
        return list(self.corba_client.get_directory_service().listDoctors())

    def list_specialties(self) -> list[Any]:
        return list(self.corba_client.get_directory_service().listSpecialties())

    def list_all_doctors(self, token: str) -> list[Any]:
        return list(self.corba_client.get_directory_service().listAllDoctors(token))

    def list_all_specialties(self, token: str) -> list[Any]:
        return list(self.corba_client.get_directory_service().listAllSpecialties(token))

    def create_doctor(self, token: str, full_name: str, specialty_id: int) -> Any:
        return self.corba_client.get_directory_service().createDoctor(token, full_name, specialty_id)

    def update_doctor(self, token: str, doctor_id: int, full_name: str, specialty_id: int) -> Any:
        return self.corba_client.get_directory_service().updateDoctor(token, doctor_id, full_name, specialty_id)

    def set_doctor_active(self, token: str, doctor_id: int, active: bool) -> None:
        self.corba_client.get_directory_service().setDoctorActive(token, doctor_id, active)

    def set_doctor_room(self, token: str, doctor_id: int, room: str) -> None:
        self.corba_client.get_directory_service().setDoctorRoom(token, doctor_id, room)

    def set_doctor_schedule(self, token: str, doctor_id: int, days: str, start: str, end: str) -> None:
        self.corba_client.get_directory_service().setDoctorSchedule(token, doctor_id, days, start, end)

    def create_specialty(self, token: str, name: str) -> Any:
        return self.corba_client.get_directory_service().createSpecialty(token, name)

    def update_specialty(self, token: str, specialty_id: int, name: str) -> Any:
        return self.corba_client.get_directory_service().updateSpecialty(token, specialty_id, name)

    def set_specialty_active(self, token: str, specialty_id: int, active: bool) -> None:
        self.corba_client.get_directory_service().setSpecialtyActive(token, specialty_id, active)
