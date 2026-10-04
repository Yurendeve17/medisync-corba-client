import re
import unicodedata
from typing import Any

from corba_client import CorbaClient
from services.auth_service import AuthService
from services.patient_service import PatientService
from services.queue_service import QueueService
from services.appointment_service import AppointmentService
from services.notification_service import NotificationService
from services.directory_service import DirectoryService

def normalize_doctor_name(name: str) -> str:
    """'Dr. Carlos Silva' e 'Carlos Silva' passam a ser o mesmo nome."""
    text = unicodedata.normalize("NFKD", name or "")
    text = "".join(c for c in text if not unicodedata.combining(c)).lower()
    text = re.sub(r"\b(dr|dra|doutor|doutora)\b\.?", " ", text)
    return " ".join(text.split())


class MediSyncApp:
    def __init__(self):
        self.corba_client = CorbaClient()

        self.auth_service = AuthService(
            self.corba_client
        )

        self.patient_service = PatientService(
            self.corba_client
        )

        self.queue_service = QueueService(
            self.corba_client
        )

        self.appointment_service = AppointmentService(
            self.corba_client
        )

        self.notification_service = NotificationService(
            self.corba_client
        )

        self.directory_service = DirectoryService(self.corba_client)

        self.current_user = None

    def close(self) -> None:
        self.corba_client.close()

    # Auteticação

    def login(
        self,
        username: str,
        password: str,
    ):
        user = self.auth_service.login(
            username,
            password,
        )

        self.current_user = user

        return user

    def logout(self) -> None:
        self.current_user = None

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

    def update_patient(
        self,
        patient_id: int,
        full_name: str,
        birth_date: str,
        gender: str,
        phone: str,
    ) -> Any:
        return self.patient_service.update_patient(
            patient_id, full_name, birth_date, gender, phone
        )


    # Fila

    def add_patient_to_queue(self, patient_id: int) -> None:
        self.queue_service.add_to_queue(patient_id)

    def add_appointment_to_queue(self, appointment_id: int) -> None:
        self.queue_service.add_appointment_to_queue(appointment_id)

    def list_queue(self) -> list[Any]:
        return self.queue_service.list_queue()

    def peek_next_queue_entry(self) -> Any:
        return self.queue_service.peek_next_entry()

    def get_next_queue_entry(self) -> Any:
        return self.queue_service.get_next_entry()

    def get_next_queue_entry_for_doctor(self, doctor_name: str) -> Any:
        return self.queue_service.get_next_entry_for_doctor(doctor_name)

    def peek_next_queue_entry_for_doctor(self, doctor_name: str) -> Any:
        return self.queue_service.peek_next_entry_for_doctor(doctor_name)

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

    def update_appointment_status(self, appointment_id: int, status: str) -> None:
        self.appointment_service.update_status(appointment_id, status)

    def reschedule_appointment(self, appointment_id: int, appointment_date: str):
        return self.appointment_service.reschedule(appointment_id, appointment_date)

    def list_appointments_for_doctor(self, doctor_name: str) -> list[Any]:
        """Consultas agendadas para o médico indicado (ignora Dr./Dra.)."""
        wanted = normalize_doctor_name(doctor_name)

        if not wanted:
            return []

        return [
            appointment
            for appointment in self.list_appointments()
            if normalize_doctor_name(appointment.doctor) == wanted
        ]

    # Médicos e especialidades

    def list_doctors(self) -> list[Any]:
        return self.directory_service.list_doctors()

    def list_specialties(self) -> list[Any]:
        return self.directory_service.list_specialties()

    def list_all_doctors(self) -> list[Any]:
        return self.directory_service.list_all_doctors()

    def list_all_specialties(self) -> list[Any]:
        return self.directory_service.list_all_specialties()

    def create_doctor(self, full_name: str, specialty_id: int) -> Any:
        return self.directory_service.create_doctor(full_name, specialty_id)

    def update_doctor(self, doctor_id: int, full_name: str, specialty_id: int) -> Any:
        return self.directory_service.update_doctor(doctor_id, full_name, specialty_id)

    def set_doctor_active(self, doctor_id: int, active: bool) -> None:
        self.directory_service.set_doctor_active(doctor_id, active)

    def create_specialty(self, name: str) -> Any:
        return self.directory_service.create_specialty(name)

    def update_specialty(self, specialty_id: int, name: str) -> Any:
        return self.directory_service.update_specialty(specialty_id, name)

    def set_specialty_active(self, specialty_id: int, active: bool) -> None:
        self.directory_service.set_specialty_active(specialty_id, active)

    # Notificações

    def call_patient(
        self,
        appointment: Any,
        patient_name: str,
    ) -> Any:
        return self.notification_service.call_patient(
            appointment.id,
            appointment.patientId,
            patient_name,
            appointment.doctor,
        )

    def list_notifications(self) -> list[Any]:
        return self.notification_service.list_notifications()

    def mark_notification_read(self, notification_id: int) -> None:
        self.notification_service.mark_as_read(notification_id)

    def mark_all_notifications_read(self) -> None:
        self.notification_service.mark_all_as_read()
