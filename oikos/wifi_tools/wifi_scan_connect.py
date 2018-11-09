from oikos.models import Wifi

def get_wifi(wifi_device):
    from wifi import Cell

    Wifi.objects.filter(known=False).delete()
    Wifi.objects.all().update(available=False)
    return sorted(list(Cell.all(wifi_device)), key=lambda x: x.signal)

def connect(wifi_mac_address,interface_name):
    from os import popen, stat, getcwd
    from subprocess import Popen, PIPE
    from time import sleep

    from django.db.models import Q

    from oikos.models import WifiDevice

    print('about to connect')
    to_connect = Wifi.objects.get(mac_address=wifi_mac_address)
    with open(getcwd() + '/oikos/wifi_tools/wpa_supplicant_default_start.conf', 'r') as f:
            default_wpa = f.read()
    if to_connect.encryption_type:
        wpa_supplicant_default = popen('sudo wpa_passphrase "{}" "{}"'.format(to_connect.ssid,to_connect.password)).read()
    else:
        with open(getcwd() + '/oikos/wifi_tools/wpa_supplicant_default.conf', 'r') as f:
            wpa_supplicant_default = f.read()
            wpa_supplicant_default = wpa_supplicant_default.replace('testing',to_connect.ssid)
    wpa_supplicant_default = default_wpa + wpa_supplicant_default
    print(wpa_supplicant_default)
    with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as wpa_supplicant:
        wpa_supplicant.write(wpa_supplicant_default)
    popen('sudo ifconfig {} down'.format(interface_name))
    popen('sudo systemctl daemon-reload')
    popen('sudo systemctl restart dhcpcd')
    popen('sudo systemctl stop wpa_supplicant.service')
    popen('sudo systemctl disable wpa_supplicant')
    popen('sudo killall wpa_supplicant')
    popen('sudo systemctl restart networking')
    popen('sudo /etc/init.d/networking restart')
    popen('sudo ifconfig {} up'.format(interface_name))
    connection_status = popen('sudo wpa_cli -i {} reconfigure'.format(interface_name)).read()
    print(connection_status)
    wifi_device = WifiDevice.objects.get(name=interface_name)
    Wifi.objects.filter(wifi_device=wifi_device).update(connected=False)
    sub_proc = Popen(['sudo', 'ifconfig',interface_name], stdout=PIPE, stderr=PIPE)
    ifconfig, errors = sub_proc.communicate()
    ifconfig = ifconfig.decode('utf-8')
    while "inet " not in ifconfig:
        sleep(1)
        sub_proc = Popen(['sudo', 'ifconfig', interface_name], stdout=PIPE, stderr=PIPE)
        ifconfig, errors = sub_proc.communicate()
        ifconfig = ifconfig.decode('utf-8')
    to_connect = Wifi.objects.get(mac_address=wifi_mac_address)
    to_connect.connected = True
    to_connect.available = True
    to_connect.known = True
    to_connect.save()

def scan_only(wifi_device):
    m = get_wifi(wifi_device)
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
    from os import popen
    from subprocess import Popen, PIPE
    from time import sleep

    with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as f:
        pass

    print('nice shoe')
    Popen(['sudo', 'systemctl', 'stop', 'wpa_supplicant.service'], stdout=PIPE, stderr=PIPE).communicate()
    Popen(['sudo', 'systemctl', 'disable', 'wpa_supplicant'], stdout=PIPE, stderr=PIPE).communicate()
    Popen(['sudo', 'systemctl', 'daemon-reload'], stdout=PIPE, stderr=PIPE).communicate()
    sub_proc = Popen(['sudo', 'journalctl', '-u', 'dhcpcd', '-b'], stdout=PIPE, stderr=PIPE)
    dhcpcd_journal, errors = sub_proc.communicate()
    dhcpcd_count = (dhcpcd_journal.decode('utf-8')).count('wlan0: waiting for carrier')
    print('nice shoe1')
    sub_proc = Popen(['sudo', 'systemctl', 'restart', 'dhcpcd'], stdout=PIPE, stderr=PIPE).communicate()
    sub_proc = Popen(['sudo', 'systemctl', 'restart', 'networking'], stdout=PIPE, stderr=PIPE).communicate()
    print('nice shoe1.5')
    sub_proc = Popen(['sudo', 'journalctl', '-u', 'dhcpcd', '-b'], stdout=PIPE, stderr=PIPE)
    print('nice shoe1.6')
    dhcpcd_journal, errors = sub_proc.communicate()
    print('nice shoe1.7')
    dhcpcd_restart_count = (dhcpcd_journal.decode('utf-8')).count('wlan0: waiting for carrier')
    print('nice shoe2')
    print(dhcpcd_restart_count)
    print(dhcpcd_count)
    sub_proc = Popen(['sudo', 'ifconfig'], stdout=PIPE, stderr=PIPE)
    ifconfig, errors = sub_proc.communicate()
    ifconfig = ifconfig.decode('utf-8')
    if wifi_device in ifconfig:
        while dhcpcd_restart_count == dhcpcd_count:
            sleep(1)
            sub_proc = Popen(['sudo', 'sudo', 'journalctl', '-u', 'dhcpcd', '-b'], stdout=PIPE, stderr=PIPE)
            dhcpcd_journal, errors = sub_proc.communicate()
            dhcpcd_restart_count = (dhcpcd_journal.decode('utf-8')).count('wlan0: waiting for carrier')
    print(dhcpcd_restart_count)
    print('nice shoe3')
    sub_proc = Popen(['sudo', 'ifconfig', wifi_device, 'down'], stdout=PIPE, stderr=PIPE)
    sub_proc = Popen(['sudo', 'ifconfig'], stdout=PIPE, stderr=PIPE)
    ifconfig, errors = sub_proc.communicate()
    ifconfig = ifconfig.decode('utf-8')
    print(ifconfig)
    print('noel')
    while wifi_device in ifconfig:
        print('while')
        print(wifi_device)
        sleep(0.10)
        sub_proc = Popen(['sudo', 'ifconfig'], stdout=PIPE, stderr=PIPE)
        ifconfig, errors = sub_proc.communicate()
        ifconfig = ifconfig.decode('utf-8')
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

