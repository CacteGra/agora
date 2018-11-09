from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Add MiBand2 MAC address'

    def add_arguments(self, parser):
        parser.add_argument('mac_address', type=str)

    def handle(self, *args, **options):
        from oikos.models import Miband
        try:
            miband = Miband.objects.get(mac_address=options['mac_address'])
            print('Got miband by MAC address')
        except Miband.DoesNotExist:
            Miband.objects.create(user='ulysse',mac_address=options['mac_address'])
            print('Created Miband device')
