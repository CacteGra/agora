from django.apps import AppConfig

class OikosConfig(AppConfig):
    name = 'oikos'
    def ready(self):
        from .models import WifiDevice, BluetoothDevice

        powered_bluetooth = BluetoothDevice.objects.filter(powered=True)
        powered_wifi = WifiDevice.objects.filter(active=True)
        if powered_bluetooth.count() == 0 and powered_wifi.count() == 0:
            from .bluetooth_tools import bluetooth_scan

            bluetooth_scan.turn_on()

        elif powered_bluetooth.count() == 0 and powered_wifi.count() > 0:
            from subprocess import check_output

            from .wifi_tools import wifi_scan_connect

            from .models import Wifi

            ifconfig = check_ouput('ifconfig')
            if 'inet' not in ifconfig:
                wifi.objects.all().update(available=False)
                wifi_scan_connect.scan_only(powered_wifi.name)
                available_wifis = wifi.objects.filter(available=True)
                Wifi.objects.filter([Q(mac_address__exact=available_wifi.mac_address) for available_wifi in available_wifis])
                known_wifis = Wifi.objects.filter(available=True,known=True)
                if available_wifis.count() > 0:
                    from subprocess import Popen, PIPE
                    add_hotspot.delete_hotspot(known_wifis.wifi_device.id)
                    for known_wifi in known_wifis:
                        wifi_scan_connect.connect(known_wifi.mac_address,powered_wifi.device_name)
                        Popen(['ifconfig'], stdout=PIPE, stderr=PIPE)
                        if "inet " in ifconfig:
                            break
                else:
                    wifi_scan_connect.delete_wifi(powered_wifi.name)
                    add_hotspot.main(powered_wifi.id,False)
