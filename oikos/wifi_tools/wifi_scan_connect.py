from oikos.models import Wifi

def get_wifi(wifi_device):
    from subprocess import check_output
    from wifi import Cell

    Wifi.objects.filter(known=False).delete()
    Wifi.objects.all().update(available=False)
    check_output(['sudo', 'wifi', 'scan'])
    return sorted(list(Cell.all(wifi_device)), key=lambda x: x.signal, reverse=True)

def connect(wifi_mac_address,interface_name):
    from os import stat, getcwd
    from subprocess import Popen, PIPE, check_output
    from time import sleep

    from django.db.models import Q

    from oikos.models import WifiDevice

    print('about to connect')
    to_connect = Wifi.objects.get(mac_address=wifi_mac_address)
    with open(getcwd() + '/oikos/wifi_tools/wpa_supplicant_default_start.conf', 'r') as f:
            default_wpa = f.read()
    if to_connect.encryption_type:
        wpa_supplicant_default = check_output(['sudo', 'wpa_passphrase', '{}'.format(to_connect.ssid), '{}'.format(to_connect.password)]).decode('utf-8')
    else:
        with open(getcwd() + '/oikos/wifi_tools/wpa_supplicant_default.conf', 'r') as f:
            wpa_supplicant_default = f.read()
            wpa_supplicant_default = wpa_supplicant_default.replace('testing',to_connect.ssid)
    wpa_supplicant_default = default_wpa + wpa_supplicant_default
    print(wpa_supplicant_default)
    with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as wpa_supplicant:
        wpa_supplicant.write(wpa_supplicant_default)
    Popen(['sudo', 'ifconfig', interface_name, 'down'], stdout=PIPE, stderr=PIPE)
    Popen(['sudo', 'systemctl', 'daemon-reload'], stdout=PIPE, stderr=PIPE)
    Popen(['sudo', 'systemctl', 'restart', 'dhcpcd'], stdout=PIPE, stderr=PIPE)
    Popen(['sudo', 'systemctl', 'stop', 'wpa_supplicant.service'], stdout=PIPE, stderr=PIPE)
    Popen(['sudo', 'killall', 'wpa_supplicant'], stdout=PIPE, stderr=PIPE)
    Popen(['sudo', 'systemctl', 'restart', 'networking'], stdout=PIPE, stderr=PIPE)
    Popen(['sudo', '/etc/init.d/networking', 'restart'], stdout=PIPE, stderr=PIPE)
    Popen(['sudo', 'ifconfig', interface_name, 'up'], stdout=PIPE, stderr=PIPE)
    connection_status, errors = Popen(['sudo', 'wpa_cli', '-i', interface_name, 'reconfigure'], stdout=PIPE, stderr=PIPE).communicate()
    print(connection_status)
    to_connect = Wifi.objects.get(mac_address=wifi_mac_address)
    to_connect.connected = True
    to_connect.available = True
    to_connect.known = True
    to_connect.save()

def scan_only(wifi_device):
    m = get_wifi(wifi_device)
    if not m:
        from subprocess import Popen, PIPE
        Popen(['sudo', 'iwlist', 'wlan0', 'scanning', '|', 'grep' 'ESSID'], stdout=PIPE, stderr=PIPE)
    for cell in m:
        a = Wifi.objects.filter(mac_address=cell.address)
        for i in a:
            print(i.ssid)
            print(i.mac_address)
        scanned_wifi, created = Wifi.objects.get_or_create(mac_address=cell.address)
        scanned_wifi.strength = cell.signal
        scanned_wifi.ssid = cell.ssid
        print('cell encryption type')
        print(cell.encryption_type)
        scanned_wifi.encryption_type = cell.encryption_type
        scanned_wifi.available = True
        scanned_wifi.save()

def delete_wifi(wifi_device):
    from subprocess import Popen, PIPE, check_output
    from time import sleep

    with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as f:
        pass

    print('nice shoe')
    Popen(['sudo', 'wpa_cli', '-i', wifi_device, 'reconfigure'], stdout=PIPE, stderr=PIPE)
    Popen(['sudo', 'killall', 'wpa_supplicant'], stdout=PIPE, stderr=PIPE)
    Popen(['sudo', 'systemctl', 'stop', 'wpa_supplicant.service'], stdout=PIPE, stderr=PIPE)
    Popen(['sudo', 'systemctl', 'disable', 'wpa_supplicant'], stdout=PIPE, stderr=PIPE)
    Popen(['sudo', 'systemctl', 'daemon-reload'], stdout=PIPE, stderr=PIPE)
    dhcpcd_journal = check_output(['sudo', 'journalctl', '-u', 'dhcpcd', '-b']).decode('utf-8')
    dhcpcd_count = dhcpcd_journal.count('wlan0: waiting for carrier')
    print('nice shoe1')
    Popen(['sudo', 'systemctl', 'restart', 'dhcpcd'], stdout=PIPE, stderr=PIPE)
    Popen(['sudo', 'systemctl', 'restart', 'networking'], stdout=PIPE, stderr=PIPE)
    print('nice shoe1.5')
    dhcpcd_journal = check_output(['sudo', 'journalctl', '-u', 'dhcpcd', '-b']).decode('utf-8')
    print('nice shoe1.6')
    print('nice shoe1.7')
    dhcpcd_restart_count = dhcpcd_journal.count('wlan0: waiting for carrier')
    print('nice shoe2')
    print(dhcpcd_restart_count)
    print(dhcpcd_count)
    ifconfig = check_output(['ifconfig']).decode('utf-8')
    if wifi_device in ifconfig:
        while dhcpcd_restart_count == dhcpcd_count:
            sleep(1)
            dhcpcd_journal = check_output(['sudo', 'journalctl', '-u', 'dhcpcd', '-b']).decode('utf-8')
            dhcpcd_restart_count = dhcpcd_journal.count('wlan0: waiting for carrier')
    print(dhcpcd_restart_count)
    print('nice shoe3')
    Popen(['sudo', 'ifconfig', wifi_device, 'down'], stdout=PIPE, stderr=PIPE)
    ifconfig = check_output(['ifconfig']).decode('utf-8')
    print(ifconfig)
    print('noel')
    while wifi_device in ifconfig:
        print('while')
        print(wifi_device)
        sleep(0.10)
        ifconfig = check_output(['ifconfig']).decode('utf-8')
    return True

def main(wifi_device):
    m = get_wifi(wifi_device)
    with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as f:
        pass
    for cell in m:
        print('cell')
        print(cell.ssid)
        try:
            this_wifi = Wifi.objects.get(mac_address=cell.address,known=True)
            print('this_wifi')
            print(this_wifi.ssid)
            connect(this_wifi.mac_address,wifi_device)
        except Wifi.DoesNotExist:
            this_wifi, create = Wifi.objects.get_or_create(mac_address=cell.address)
            this_wifi.strength=cell.signal
            this_wifi.encryption_type=cell.encryption_type
            this_wifi.ssid = cell.ssid
            this_wifi.available = True
            this_wifi.save()
