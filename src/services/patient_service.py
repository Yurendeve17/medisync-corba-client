from typing import Any


class PatientService:
    def __init__(self, corba_client):
        self.corba_client = corba_client

    def register_patient(
        self,
        full_name: str,
        birth_date: str,
        gender: str,
        phone: str,
        address: str,
        neighborhood: str,
        city: str,
    ) -> Any:
        service = self.corba_client.get_patient_service()
        return service.registerPatient(
            full_name,
            birth_date,
            gender,
            phone,
            address,
            neighborhood,
            city,
        )

    def find_patient_by_id(self, patient_id: int) -> Any:
        service = self.corba_client.get_patient_service()
        return service.findPatientById(patient_id)

    def list_patients(self) -> list[Any]:
        service = self.corba_client.get_patient_service()
        return list(service.listPatients())

    def update_patient(
        self,
        patient_id: int,
        full_name: str,
        birth_date: str,
        gender: str,
        phone: str,
        address: str,
        neighborhood: str,
        city: str,
    ) -> Any:
        service = self.corba_client.get_patient_service()
        return service.updatePatient(
            patient_id,
            full_name,
            birth_date,
            gender,
            phone,
            address,
            neighborhood,
            city,
        )
