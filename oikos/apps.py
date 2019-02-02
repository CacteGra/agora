from django.apps import AppConfig

class OikosConfig(AppConfig):
    name = 'oikos'
    def ready(self):
        from . import check_worker
        from .bluetooth_tools import bluetooth_scan

        bluetooth_scan.main()
