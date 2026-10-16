from typing import Any


class DoctorService:
    def __init__(self, corba_client):
        self.corba_client = corba_client

    def my_appointments(self, token: str) -> list[Any]:
        return list(self.corba_client.get_doctor_service().myAppointments(token))

    def patient_history(self, token: str, patient_id: int) -> list[Any]:
        return list(self.corba_client.get_doctor_service().patientHistory(token, patient_id))

    def save_note(self, token: str, appointment_id: int, diagnosis: str, observations: str, prescription: str) -> Any:
        return self.corba_client.get_doctor_service().saveClinicalNote(token, appointment_id, diagnosis, observations, prescription)

    def save_note_extended(self, token: str, appointment_id: int, diagnosis: str, observations: str, prescription: str, vital_signs: str, care_plan: str) -> Any:
        return self.corba_client.get_doctor_service().saveClinicalNoteExtended(
            token, appointment_id, diagnosis, observations, prescription, vital_signs, care_plan
        )

    def update_status(self, token: str, appointment_id: int, status: str) -> None:
        self.corba_client.get_doctor_service().updateMyAppointmentStatus(token, appointment_id, status)

    def statistics(self, token: str, from_date: str, to_date: str) -> Any:
        return self.corba_client.get_doctor_service().myStatistics(token, from_date, to_date)

    def diagnosis_volumes(self, token: str, from_date: str, to_date: str) -> list[Any]:
        return list(self.corba_client.get_doctor_service().diagnosisVolumes(token, from_date, to_date))
