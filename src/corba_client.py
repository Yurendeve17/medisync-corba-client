import os
import socket
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
        self.orb = None
        try:
            print(
                f"[CORBA] A verificar TCP em {NAME_SERVICE_HOST}:{NAME_SERVICE_PORT}...",
                flush=True,
            )
            try:
                with socket.create_connection(
                    (NAME_SERVICE_HOST, int(NAME_SERVICE_PORT)), timeout=3
                ):
                    pass
            except OSError as error:
                raise RuntimeError(
                    f"O endereco {NAME_SERVICE_HOST}:{NAME_SERVICE_PORT} nao aceitou conexao TCP. "
                    "Verifique se o Naming Service esta ativo e se a porta 1050 esta liberada "
                    "entre as maquinas."
                ) from error

            print("[CORBA] TCP acessivel; a iniciar omniORB.", flush=True)
            self.orb = CORBA.ORB_init(
                [
                    "-ORBInitRef", f"NameService={NAME_SERVICE}",
                    "-ORBclientCallTimeOutPeriod", "15000",
                    "-ORBclientConnectTimeOutPeriod", "5000",
                ],
                CORBA.ORB_ID,
            )
            naming_object = self.orb.resolve_initial_references("NameService")
            self.naming_context = naming_object._narrow(CosNaming.NamingContext)
            if self.naming_context is None:
                raise RuntimeError("O Naming Service nao devolveu um NamingContext valido.")
            print("[CORBA] Naming Service pronto.", flush=True)
        except Exception as error:
            if self.orb is not None:
                try:
                    self.orb.destroy()
                except Exception:
                    pass
            raise RuntimeError(
                f"Falha ao ligar ao Naming Service em {NAME_SERVICE_HOST}:{NAME_SERVICE_PORT}. "
                "Confirme que o servidor esta ligado, que este endereco pertence a maquina do servidor "
                "e que a porta TCP esta acessivel pela rede. "
                f"Detalhe: {type(error).__name__}: {error}"
            ) from error

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

    def get_user_service(self):
        return self._resolve_service("UserService", Hospital.UserService)

    def get_report_service(self):
        return self._resolve_service("ReportService", Hospital.ReportService)

    def get_doctor_service(self):
        return self._resolve_service("DoctorService", Hospital.DoctorService)

    def get_admin_service(self):
        return self._resolve_service("AdminService", Hospital.AdminService)

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
