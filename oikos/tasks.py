from celery import shared_task

def file_naming(usr_id, file_type, file_extension):
    file_name = os.path.join(os.path.dirname(os.getcwd())) + '/proto/mainapp/static/users/{0}/{0}_{1}.{2}'.format(usr_id, file_type, file_extension)
    return file_name

@shared_task
def miband(miband_address):
    import sys
    from datetime import datetime, timedelta
    from os import popen
    from pytz import utc
    from wifi import Cell
    from requests import get

    from oikos.wifi_tools import wifi_scan_connect
    from oikos.miband.base import MiBand2
    from oikos.miband.constants import ALERT_TYPES

    from bluepy.btle import BTLEException

    from oikos.models import MibandEntry, Miband, Wifi, WifiDevice

    MibandEntry.objects.all().delete()

    succeeded = False

    while not succeeded:
        try:
            band = MiBand2(miband_address, debug=True)
            succeeded = True
        except BTLEException:
            continue
        band.setSecurityLevel(level="medium")
        miband_device = Miband.objects.get(mac_address=miband_address)
        if not miband_device.authenticated:
            if band.initialize():
                print("Init OK")
            band.disconnect()
            miband_device.authenticated = True
            miband_device.save()
        else:
            band.authenticate()

    while True:
        print('event')
        try:
            band.get_event_info()
            print('got envent info')
            m = MibandEntry.objects.all().order_by('date')
            n = m.count()
            print(n)
            if n > 0:
                if m[0].date + timedelta(seconds=10) < utc.localize(datetime.utcnow()):
                    if n == 7:
                        available_interfaces = popen("ip -br addr show | awk '{print $1}'").read()
                        for available_interface in available_interfaces.split('\n'):
                            if ('wlan' in available_interface) and (available_interface in popen('ifconfig').read()):
                                print(available_interface)
                                wifi_device, created = WifiDevice.objects.get_or_create(name=available_interface)
                                wifi_device.active = True
                                wifi_device.save()
                            elif ('wlan' in available_interface) and (available_interface not in popen('ifconfig').read()):
                                print(available_interface)
                                wifi_device, created = WifiDevice.objects.get_or_create(name=available_interface)
                                wifi_device.active = False
                                wifi_device.save()
                        wifi_devices = WifiDevice.objects.filter(active=True)
                        for wifi_device in wifi_devices:
                            if not wifi_device.wifi:
                                if wifi_device.name in popen('ifconfig').read():
                                    popen('ifconfig {} down'.format(wifi_device.name))
                                    add_hotspot.delete(id)
                                else:
                                    popen('ifconfig {} down'.format(wifi_device.name))
                                    popen('ifconfig {} up'.format(wifi_device.name))
                                    wifi_scan_connect.main(wifi_device.name)
                                    MibandEntry.objects.all().delete()
                    else:
                        continue
                elif m[0].date + timedelta(seconds=20) < utc.localize(datetime.utcnow()):
                    MibandEntry.objects.all().delete()

        except BTLEException:
            print('did not get_event_info')
            succeeded = False
            while not succeeded:
                try:
                    band = MiBand2(miband_address, debug=True)
                    band.authenticate()
                    succeeded = True
                except BTLEException:
                    continue

    band.disconnect()
