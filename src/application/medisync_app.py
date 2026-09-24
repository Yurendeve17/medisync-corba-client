from typing import Any

from corba_client import CorbaClient
from services.patient_service import PatientService
from services.queue_service import QueueService
from services.appointment_service import AppointmentService


class MediSyncApp:
    def __init__(self):
        self.corba_client = CorbaClient()

        self.patient_service = PatientService(
            self.corba_client
        )

        self.queue_service = QueueService(
            self.corba_client
        )

        self.appointment_service = AppointmentService(
            self.corba_client
        )

    def close(self) -> None:
        self.corba_client.close()

    # Pacientes

    def register_patient(
        self,
        full_name: str,
        birth_date: str,
        gender: str,
        phone: str,
    ) -> Any:
        return self.patient_service.register_patient(
            full_name,
            birth_date,
            gender,
            phone,
        )

    def list_patients(self) -> list[Any]:
        return self.patient_service.list_patients()

    def find_patient_by_id(self, patient_id: int) -> Any:
        return self.patient_service.find_patient_by_id(
            patient_id
        )

    # Fila

    def add_patient_to_queue(self, patient_id: int) -> None:
        self.queue_service.add_to_queue(patient_id)

    def peek_next_patient(self) -> int:
        return self.queue_service.peek_next_patient()

    def get_next_patient(self) -> int:
        return self.queue_service.get_next_patient()

    def get_queue_size(self) -> int:
        return self.queue_service.get_queue_size()

    # Consultas

    def schedule_appointment(
        self,
        patient_id: int,
        doctor: str,
        appointment_date: str,
        specialty: str,
    ) -> Any:
        return self.appointment_service.schedule_appointment(
            patient_id,
            doctor,
            appointment_date,
            specialty,
        )

    def list_appointments(self) -> list[Any]:
        return self.appointment_service.list_appointments()

    def find_appointment_by_id(
        self,
        appointment_id: int,
    ) -> Any:
        return self.appointment_service.find_appointment_by_id(
            appointment_id
        )