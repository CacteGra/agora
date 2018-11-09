from django.apps import AppConfig

class OikosConfig(AppConfig):
    name = 'oikos'
    def ready(self):
        from . import check_worker
        from .bluetooth_tools import bluetooth_scan

        from .models import Miband

        bluetooth_scan.main()
        miband_users = Miband.objects.filter(active=True,authenticated=True)
        for miband_user in miband_users:
            check_worker.main(miband_user.username)
