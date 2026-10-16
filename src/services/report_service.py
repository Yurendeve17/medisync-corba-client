from typing import Any


class ReportService:
    def __init__(self, corba_client):
        self.corba_client = corba_client

    def daily_summary(self, token: str, date: str) -> Any:
        return self.corba_client.get_report_service().dailySummary(token, date)

    def average_times(self, token: str, from_date: str, to_date: str) -> list[Any]:
        return list(self.corba_client.get_report_service().averageTimes(token, from_date, to_date))

    def specialty_volumes(self, token: str, from_date: str, to_date: str) -> list[Any]:
        return list(self.corba_client.get_report_service().specialtyVolumes(token, from_date, to_date))

    def reception_statistics(self, token: str, from_date: str, to_date: str) -> Any:
        return self.corba_client.get_report_service().receptionStatistics(token, from_date, to_date)
