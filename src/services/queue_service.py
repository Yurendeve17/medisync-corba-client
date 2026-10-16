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

    def add_appointment_to_queue_with_priority(self, appointment_id: int, priority: int) -> None:
        self.corba_client.get_queue_service().addAppointmentToQueueWithPriority(appointment_id, priority)

    def add_walk_in_to_queue(self, patient_id: int, doctor: str, specialty: str, priority: int) -> Any:
        return self.corba_client.get_queue_service().addWalkInToQueue(patient_id, doctor, specialty, priority)

    def withdraw_entry(self, queue_entry_id: int, reason: str) -> None:
        self.corba_client.get_queue_service().withdrawQueueEntry(queue_entry_id, reason)

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

    def get_next_entry_for_doctor(self, doctor: str) -> Any:
        service = self.corba_client.get_queue_service()
        return service.getNextQueueEntryForDoctor(doctor)

    def call_next_entry_for_doctor(self, token: str, doctor: str) -> Any:
        return self.corba_client.get_queue_service().callNextQueueEntryForDoctor(token, doctor)

    def peek_next_entry_for_doctor(self, doctor: str) -> Any:
        service = self.corba_client.get_queue_service()
        return service.peekNextQueueEntryForDoctor(doctor)

    def list_queue(self) -> list[Any]:
        service = self.corba_client.get_queue_service()
        return list(service.listQueue())

    def get_queue_size(self) -> int:
        service = self.corba_client.get_queue_service()
        return service.getQueueSize()

    def estimated_wait_minutes(self, queue_entry_id: int) -> float:
        return float(self.corba_client.get_queue_service().estimatedWaitMinutesForQueueEntry(queue_entry_id))
