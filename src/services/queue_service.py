from typing import Any


class QueueService:
    def __init__(self, corba_client):
        self.corba_client = corba_client

    def add_to_queue(self, patient_id: int) -> None:
        service = self.corba_client.get_queue_service()
        service.addToQueue(patient_id)

    def add_appointment_to_queue(self, appointment_id: int) -> None:
        service = self.corba_client.get_queue_service()
        service.addAppointmentToQueue(appointment_id)

    def get_next_patient(self) -> int:
        service = self.corba_client.get_queue_service()
        return service.getNextPatient()

    def peek_next_patient(self) -> int:
        service = self.corba_client.get_queue_service()
        return service.peekNextPatient()

    def get_next_entry(self) -> Any:
        service = self.corba_client.get_queue_service()
        return service.getNextQueueEntry()

    def peek_next_entry(self) -> Any:
        service = self.corba_client.get_queue_service()
        return service.peekNextQueueEntry()

    def list_queue(self) -> list[Any]:
        service = self.corba_client.get_queue_service()
        return list(service.listQueue())

    def get_queue_size(self) -> int:
        service = self.corba_client.get_queue_service()
        return service.getQueueSize()
