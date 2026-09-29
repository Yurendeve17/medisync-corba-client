from typing import Any


class NotificationService:
    def __init__(self, corba_client):
        self.corba_client = corba_client

    def call_patient(
        self,
        appointment_id: int,
        patient_id: int,
        patient_name: str,
        doctor: str,
    ) -> Any:
        service = self.corba_client.get_notification_service()

        return service.callPatient(
            appointment_id,
            patient_id,
            patient_name,
            doctor,
        )

    def list_notifications(self) -> list[Any]:
        service = self.corba_client.get_notification_service()

        return list(service.listNotifications())

    def mark_as_read(self, notification_id: int) -> None:
        service = self.corba_client.get_notification_service()
        service.markAsRead(notification_id)

    def mark_all_as_read(self) -> None:
        service = self.corba_client.get_notification_service()
        service.markAllAsRead()
