from typing import Any


class AppointmentService:
    def __init__(self, corba_client):
        self.corba_client = corba_client

    def schedule_appointment(
        self,
        patient_id: int,
        doctor: str,
        appointment_date: str,
        specialty: str,
    ) -> Any:
        service = self.corba_client.get_appointment_service()

        return service.scheduleAppointment(
            patient_id,
            doctor,
            appointment_date,
            specialty,
        )

    def find_appointment_by_id(self, appointment_id: int) -> Any:
        service = self.corba_client.get_appointment_service()

        return service.findAppointmentById(appointment_id)

    def list_appointments(self) -> list[Any]:
        service = self.corba_client.get_appointment_service()

        return list(service.listAppointments())
    def update_status(self, appointment_id: int, status: str) -> None:
        service = self.corba_client.get_appointment_service()
        service.updateAppointmentStatus(appointment_id, status)
