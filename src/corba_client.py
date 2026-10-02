import os
import sys
from pathlib import Path

from omniORB import CORBA
import CosNaming

ROOT_DIR = Path(__file__).resolve().parent.parent
GENERATED_DIR = ROOT_DIR / "generated"

sys.path.insert(0, str(GENERATED_DIR))

import Hospital


NAME_SERVICE_HOST = os.getenv("CORBA_NAME_SERVICE_HOST")

NAME_SERVICE_PORT = os.getenv(
    "CORBA_NAME_SERVICE_PORT",
    "1050",
)

if not NAME_SERVICE_HOST:
    raise RuntimeError(
        "A variável CORBA_NAME_SERVICE_HOST não está configurada."
    )

NAME_SERVICE = (
    f"corbaloc::{NAME_SERVICE_HOST}:{NAME_SERVICE_PORT}/NameService"
)


class CorbaClient:
    def __init__(self):
        self.orb = CORBA.ORB_init(
            ["-ORBInitRef", f"NameService={NAME_SERVICE}"],
            CORBA.ORB_ID,
        )

        naming_object = self.orb.resolve_initial_references(
            "NameService"
        )

        self.naming_context = naming_object._narrow(
            CosNaming.NamingContext
        )

        if self.naming_context is None:
            raise RuntimeError(
                "Não foi possível obter o NamingContext."
            )

    def _resolve_service(self, service_name, service_type):
        name = [
            CosNaming.NameComponent(service_name, "")
        ]

        service_object = self.naming_context.resolve(name)

        service = service_object._narrow(service_type)

        if service is None:
            raise RuntimeError(
                f"Não foi possível obter {service_name}."
            )

        return service

    def get_hello_service(self):
        return self._resolve_service(
            "HelloService",
            Hospital.HelloService,
        )

    def get_auth_service(self):
        return self._resolve_service(
            "AuthService",
            Hospital.AuthService,
        )

    def get_patient_service(self):
        return self._resolve_service(
            "PatientService",
            Hospital.PatientService,
        )

    def get_directory_service(self):
        return self._resolve_service("DirectoryService", Hospital.DirectoryService)

    def get_queue_service(self):
        return self._resolve_service(
            "QueueService",
            Hospital.QueueService,
        )

    def get_appointment_service(self):
        return self._resolve_service(
            "AppointmentService",
            Hospital.AppointmentService,
        )

    def get_notification_service(self):
        return self._resolve_service(
            "NotificationService",
            Hospital.NotificationService,
        )

    def close(self):
        self.orb.destroy()