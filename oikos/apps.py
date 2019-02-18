from django.apps import AppConfig

class OikosConfig(AppConfig):
    name = 'oikos'
    def ready(self):
        from .hotspot import add_hotspot

        from .models import WifiDevice, BluetoothDevice, Hotspot

        all_hotspots = Hotspot.objects.filter(on_boot=True)
        if all_hotspots.count() == 0:
            for all_hotspot in all_hotspots:
                add_hotspot.delete(all_hotspot.wifi_device.name)

        powered_wifi = WifiDevice.objects.filter(active=True)

        if powered_wifi.count() > 0 and all_hotspots.count() == 0:
            from subprocess import check_output

            from .wifi_tools import wifi_scan_connect

            from .models import Wifi

            ifconfig = check_output('ifconfig').decode('utf-8')
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
                    wifi_scan_connect.turn_off(powered_wifi.name)
                    add_hotspot.main(powered_wifi.id,False)

        powered_bluetooth = BluetoothDevice.objects.filter(powered=True)

        if powered_bluetooth.count() == 0 and powered_wifi.count() > 0 and all_hotspots.count() > 0:
            from subprocess import Popen, PIPE
            from .bluetooth_tools import bluetooth_scan
            is_active, err = Popen(['sudo', 'systemctl', 'is-active', 'bluetooth'], stdout=PIPE, stderr=PIPE).communicate()
            if is_active.decode('utf-8').replace('\n', '') != 'active':
                print('turning on')
                bluetooth_scan.turn_on()
