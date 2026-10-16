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
from services.user_service import UserService
from services.report_service import ReportService
from services.doctor_service import DoctorService
from services.admin_service import AdminService

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
        self.user_service = UserService(self.corba_client)
        self.report_service = ReportService(self.corba_client)
        self.doctor_service = DoctorService(self.corba_client)
        self.admin_service = AdminService(self.corba_client)

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
        token = getattr(self.current_user, "sessionToken", "")
        if token:
            try: self.corba_client.get_auth_service().logout(token)
            except Exception: pass
        self.current_user = None

    # Pacientes

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
        return self.patient_service.register_patient(
            full_name,
            birth_date,
            gender,
            phone,
            address,
            neighborhood,
            city,
        )

    def list_patients(self) -> list[Any]:
        return self.patient_service.list_patients()

    def search_patients(self, query: str) -> list[Any]:
        return self.patient_service.search_patients(query)

    def has_possible_duplicate(self, full_name: str, birth_date: str, phone: str, exclude_id: int = 0) -> bool:
        return self.patient_service.has_possible_duplicate(full_name, birth_date, phone, exclude_id)

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
        address: str,
        neighborhood: str,
        city: str,
    ) -> Any:
        return self.patient_service.update_patient(
            patient_id,
            full_name,
            birth_date,
            gender,
            phone,
            address,
            neighborhood,
            city,
        )


    # Fila

    def add_patient_to_queue(self, patient_id: int) -> None:
        self.queue_service.add_to_queue(patient_id)

    def add_appointment_to_queue(self, appointment_id: int) -> None:
        self.queue_service.add_appointment_to_queue(appointment_id)

    def check_in(self, appointment_id: int, priority: int = 0) -> None:
        self.queue_service.add_appointment_to_queue_with_priority(appointment_id, priority)

    def add_walk_in(self, patient_id: int, doctor: str, specialty: str, priority: int = 0) -> Any:
        return self.queue_service.add_walk_in_to_queue(patient_id, doctor, specialty, priority)

    def withdraw_queue_entry(self, entry_id: int, reason: str) -> None:
        self.queue_service.withdraw_entry(entry_id, reason)

    def list_queue(self) -> list[Any]:
        return self.queue_service.list_queue()

    def peek_next_queue_entry(self) -> Any:
        return self.queue_service.peek_next_entry()

    def get_next_queue_entry(self) -> Any:
        return self.queue_service.get_next_entry()

    def get_next_queue_entry_for_doctor(self, doctor_name: str) -> Any:
        return self.queue_service.get_next_entry_for_doctor(doctor_name)

    def call_next_queue_entry_for_doctor(self, doctor_name: str) -> Any:
        token = getattr(self.current_user, "sessionToken", "")
        if not token: raise RuntimeError("A sessão expirou. Inicie sessão novamente.")
        return self.queue_service.call_next_entry_for_doctor(token, doctor_name)

    def peek_next_queue_entry_for_doctor(self, doctor_name: str) -> Any:
        return self.queue_service.peek_next_entry_for_doctor(doctor_name)

    def peek_next_patient(self) -> int:
        return self.queue_service.peek_next_patient()

    def get_next_patient(self) -> int:
        return self.queue_service.get_next_patient()

    def get_queue_size(self) -> int:
        return self.queue_service.get_queue_size()

    def estimated_wait_minutes(self, queue_entry_id: int) -> float:
        return self.queue_service.estimated_wait_minutes(queue_entry_id)

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

    def reschedule_appointment_with_reason(self, appointment_id: int, appointment_date: str, reason: str = ""):
        return self.appointment_service.reschedule_with_reason(appointment_id, appointment_date, reason)

    def cancel_appointment(self, appointment_id: int, reason: str = "") -> None:
        self.appointment_service.cancel(appointment_id, reason)

    def list_appointments_for_doctor(self, doctor_name: str) -> list[Any]:
        """Lista consultas atrav?s do servi?o autenticado do m?dico."""
        token = self._doctor_token()
        if normalize_doctor_name(doctor_name) != normalize_doctor_name(getattr(self.current_user, "fullName", "")):
            raise PermissionError("S? pode consultar as suas pr?prias consultas.")
        return self.doctor_service.my_appointments(token)

    def doctor_patient_history(self, patient_id: int) -> list[Any]:
        return self.doctor_service.patient_history(self._doctor_token(), patient_id)

    def save_clinical_note(self, appointment_id: int, diagnosis: str, observations: str, prescription: str) -> Any:
        return self.doctor_service.save_note(self._doctor_token(), appointment_id, diagnosis, observations, prescription)

    def save_clinical_note_extended(self, appointment_id: int, diagnosis: str, observations: str, prescription: str, vital_signs: str, care_plan: str) -> Any:
        return self.doctor_service.save_note_extended(
            self._doctor_token(), appointment_id, diagnosis, observations, prescription, vital_signs, care_plan
        )

    def update_my_appointment_status(self, appointment_id: int, status: str) -> None:
        self.doctor_service.update_status(self._doctor_token(), appointment_id, status)

    def doctor_statistics(self, from_date: str, to_date: str) -> Any:
        return self.doctor_service.statistics(self._doctor_token(), from_date, to_date)

    def doctor_diagnosis_volumes(self, from_date: str, to_date: str) -> list[Any]:
        return self.doctor_service.diagnosis_volumes(self._doctor_token(), from_date, to_date)

    def _doctor_token(self) -> str:
        user = self.current_user
        token = getattr(user, "sessionToken", "")
        if not token or getattr(user, "role", "") != "DOCTOR":
            raise PermissionError("Esta operacao exige uma sessao de medico.")
        return token

    # Médicos e especialidades

    def list_doctors(self) -> list[Any]:
        return self.directory_service.list_doctors()

    def list_specialties(self) -> list[Any]:
        return self.directory_service.list_specialties()

    def list_all_doctors(self) -> list[Any]:
        return self.directory_service.list_all_doctors(self._admin_token())

    def list_all_specialties(self) -> list[Any]:
        return self.directory_service.list_all_specialties(self._admin_token())

    def create_doctor(self, full_name: str, specialty_id: int) -> Any:
        return self.directory_service.create_doctor(self._admin_token(), full_name, specialty_id)

    def update_doctor(self, doctor_id: int, full_name: str, specialty_id: int) -> Any:
        return self.directory_service.update_doctor(self._admin_token(), doctor_id, full_name, specialty_id)

    def set_doctor_active(self, doctor_id: int, active: bool) -> None:
        self.directory_service.set_doctor_active(self._admin_token(), doctor_id, active)

    def set_doctor_room(self, doctor_id: int, room: str) -> None:
        self.directory_service.set_doctor_room(self._admin_token(), doctor_id, room)

    def set_doctor_schedule(self, doctor_id: int, days: str, start: str, end: str) -> None:
        self.directory_service.set_doctor_schedule(self._admin_token(), doctor_id, days, start, end)

    def list_users(self) -> list[Any]:
        return self.user_service.list_users(self._admin_token())

    def create_user(self, username: str, full_name: str, role: str, password: str) -> Any:
        return self.user_service.create_user(self._admin_token(), username, full_name, role, password)

    def set_user_active(self, user_id: int, active: bool) -> None:
        self.user_service.set_active(self._admin_token(), user_id, active)

    def reset_user_password(self, user_id: int, password: str) -> None:
        self.user_service.reset_password(self._admin_token(), user_id, password)

    def change_own_password(self, current_password: str, new_password: str) -> None:
        token = getattr(self.current_user, "sessionToken", "")
        if not token: raise RuntimeError("A sessão expirou. Inicie sessão novamente.")
        self.user_service.change_password(token, current_password, new_password)

    def _admin_token(self) -> str:
        user = self.current_user
        if user is None or getattr(user, "role", "") != "ADMIN":
            raise PermissionError("Esta operação está disponível apenas para administradores.")
        token = getattr(user, "sessionToken", "")
        if not token: raise RuntimeError("A sessão expirou. Inicie sessão novamente.")
        return token

    def daily_summary(self, date: str) -> Any:
        return self.report_service.daily_summary(self._admin_token(), date)

    def average_times(self, from_date: str, to_date: str) -> list[Any]:
        return self.report_service.average_times(self._admin_token(), from_date, to_date)

    def specialty_volumes(self, from_date: str, to_date: str) -> list[Any]:
        return self.report_service.specialty_volumes(self._admin_token(), from_date, to_date)

    def reception_statistics(self, from_date: str, to_date: str) -> Any:
        user = self.current_user
        token = getattr(user, "sessionToken", "")
        if not token or getattr(user, "role", "") not in {"ADMIN", "RECEPTION"}:
            raise PermissionError("As estatísticas operacionais exigem sessão de recepção ou administração.")
        return self.report_service.reception_statistics(token, from_date, to_date)

    def audit_logs(self, from_date: str, to_date: str) -> list[Any]:
        return self.admin_service.audit_logs(self._admin_token(), from_date, to_date)

    def system_settings(self) -> list[Any]:
        return self.admin_service.settings(self._admin_token())

    def set_system_setting(self, key: str, value: str) -> None:
        self.admin_service.set_setting(self._admin_token(), key, value)

    def create_specialty(self, name: str) -> Any:
        return self.directory_service.create_specialty(self._admin_token(), name)

    def update_specialty(self, specialty_id: int, name: str) -> Any:
        return self.directory_service.update_specialty(self._admin_token(), specialty_id, name)

    def set_specialty_active(self, specialty_id: int, active: bool) -> None:
        self.directory_service.set_specialty_active(self._admin_token(), specialty_id, active)

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
