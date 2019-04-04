from django.apps import AppConfig

class OikosConfig(AppConfig):
    name = 'oikos'
    def ready(self):
        from .hotspot import add_hotspot
        from .bluetooth_tools import bluetooth_scan

        from .models import WifiDevice, Bluetooth, BluetoothDevice, Hotspot

        all_hotspots = Hotspot.objects.filter(on_boot=True)
        if all_hotspots.count() == 0:
            all_hotspots = Hotspot.objects.all()
            for all_hotspot in all_hotspots:
                add_hotspot.delete(all_hotspot.wifi_device.id)

        powered_bluetooth = BluetoothDevice.objects.filter(powered=True)
        powered_wifis = WifiDevice.objects.filter(active=True)

        if powered_bluetooth.count() == 0 and powered_wifis.count() > 0 and all_hotspots.count() > 0:
            from subprocess import Popen, PIPE
            from .bluetooth_tools import bluetooth_scan
            is_active, err = Popen(['sudo', 'systemctl', 'is-active', 'bluetooth'], stdout=PIPE, stderr=PIPE).communicate()
            if is_active.decode('utf-8').replace('\n', '') != 'active':
                bluetooth_scan.turn_on()

        bluetooth_scan.main()
        bluetooth_devices = Bluetooth.objects.filter(available=True,paired=True)
        if bluetooth_devices.count() == 0:
            if not powered_wifis:
                wifi_devices = WifiDevice.objects.all()
            else:
                wifi_devices = powered_wifis
            for wifi_device in wifi_devices:
                from subprocess import check_output

                from django.db.models import Q

                from .wifi_tools import wifi_scan_connect

                from .models import Wifi

                ifconfig = check_output(['ifconfig', wifi_device.name]).decode('utf-8')
                if 'inet' not in ifconfig:
                    Wifi.objects.all().update(available=False)
                    wifi_scan_connect.scan_only(wifi_device.name)
                    available_wifis = Wifi.objects.filter(available=True)
                    Wifi.objects.filter([Q(mac_address__exact=available_wifi.mac_address) for available_wifi in available_wifis])
                    known_wifis = Wifi.objects.filter(available=True,known=True)
                    has_inet = False
                    if available_wifis.count() > 0:
                        for known_wifi in known_wifis:
                            wifi_scan_connect.connect(known_wifi.mac_address,wifi_device.device_name)
                            ifconfig = check_output(['ifconfig']).decode('utf-8')
                            if "inet " in ifconfig:
                                has_inet = True
                                break
                        if not has_inet:
                            wifi_scan_connect.turn_off(wifi_device.id)
                            add_hotspot.main(wifi_device.id)
                    else:
                        wifi_scan_connect.turn_off(wifi_device.id)
                        add_hotspot.main(wifi_device.id)
                break
