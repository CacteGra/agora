from django.apps import AppConfig

class OikosConfig(AppConfig):
    name = 'oikos'
    def ready(self):
        from .bluetooth_tools import bluetooth_scan

        bluetooth_scan.main()
