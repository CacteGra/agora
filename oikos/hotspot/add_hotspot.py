from requests import get
from subprocess import Popen, PIPE, check_output

from oikos.models import WifiDevice, Hotspot

def file_ending(path):
    with open(path, 'r') as f:
        return f.readlines()

def delete_hotspot(id):
    wifi_device = WifiDevice.objects.get(id=id)
    try:
        the_hotspot = Hotspot.objects.get(wifi_device=wifi_device)
    except Hotspot.DoesNotExist:
        print('returning true')
        return True
    with open(getcwd() + '/oikos/hotspot/hostapd.conf', 'r') as f:
        hostapd = f.readlines()
    delete = False
    with open(getcwd() + '/oikos/hotspot/hostapd.conf', 'w') as f:
        for line in hostapd:
            if wifi_device.name in line:
                delete = True
                pass
            elif "rsn_pairwise=CCMP" in line:
                delete = False
            elif delete == True:
                pass
            else:
                f.write(line)
    the_hotspot.active = False
    the_hotspot.save()
    with open('/etc/dhcpcd.conf', 'r') as f:
        dhcpcd = f.readlines()
    Popen(['sudo', 'ifconfig', the_hotspot.wifi_device.name, 'down'], stdout=PIPE, stderr=PIPE)
    print('brought wlan0 down')
    with open(getcwd() + '/oikos/hotspot/dhcpcd.conf', 'w') as f:
        wifi_list = []
        for line in dhcpcd:
            if the_hotspot.wifi_device.name in line:
                print('wifi_device in line')
                line_list = line.split(" ")
                for line_item in line_list:
                    try:
                        wifi_device = WifiDevice.objects.get(name=line_item)
                        a_hotspot = Hotspot.objects.get(wifi_device=wifi_device)
                    except Hotspot.DoesNotExist:
                        continue
                    except WifiDevice.DoesNotExist:
                        continue
                    if a_hotspot.active:
                        wifi_list.append(line_item)
                if wifi_list:
                    line = "denyinterfaces " + (" ").join(wifi_list)
                    f.write(line)
                    Popen(['sudo', 'systemctl', 'restart', 'hostapd'], stdout=PIPE, stderr=PIPE)
                else:
                    Popen(['sudo', 'systemctl', 'stop', 'hostapd'], stdout=PIPE, stderr=PIPE)
            else:
                print(line)
                f.write(line)
    new_conf = getcwd() + '/oikos/hotspot/dhcpcd.conf'
    default_conf = '/etc/dhcpcd.conf'
    Popen(['sudo', 'cp', '-f', new_conf, default_conf], stdout=PIPE, stderr=PIPE)
    Popen(['sudo', 'systemctl', 'daemon-reload'], stdout=PIPE, stderr=PIPE)
    Popen(['sudo', 'systemctl', 'restart dhcpcd'], stdout=PIPE, stderr=PIPE)

def main(id, change):

    wifi_device = WifiDevice.objects.get(id=id)
    if change:
        the_hotspot = Hotspot.objects.get(wifi_device=wifi_device)
        with open(getcwd() + '/oikos/hotspot/hostapd.conf', 'r') as f:
            hostapd = f.readlines()
            for line in hostapd:
                if "interface=" in line:
                    f.write("interface={}".format(the_hotspot.wifi_device.name))
                elif "wpa_passphrase=" in line:
                    f.write("wpa_passphrase={}".format(the_hotspot.password))
                elif "ssid=" in line:
                    f.write("ssid={}".format(the_hotspot.name))
                else:
                    f.write(line)
        if the_hotspot.on_boot:
            Popen(['sudo', 'systemctl', 'restart', 'hostapd'], stdout=PIPE, stderr=PIPE)
        else:
            Popen(['hostapd', '-B', getcwd() + '/oikos/hotspot/hostapd.conf'], stdout=PIPE, stderr=PIPE)
        Popen(['sudo', 'ifconfig', the_hotspot.wifi_device.name, 'down'], stdout=PIPE, stderr=PIPE)
        Popen(['sudo', 'ifconfig', the_hotspot.wifi_device.name, 'up'], stdout=PIPE, stderr=PIPE)
        return True
    try:
        print('in the try')
        the_hotspot = Hotspot.objects.get(wifi_device=wifi_device,active=True)
        with open(getcwd() + '/oikos/hotspot/hostapd.conf', 'r') as f:
            hostapd = f.read()
        if wifi_device.name in hostapd and the_hotspot.active and wifi_device.name in check_output(['sudo', 'ifconfig', '-a']).decode('utf-8'):
            right_lines = False
            with open(getcwd() + '/oikos/hotspot/hostapd.conf', 'r') as f:
                hostapd = f.readlines()
            with open(getcwd() + '/oikos/hotspot/hostapd.conf', 'w') as f:
                for line in hostapd:
                    if '**{}**'.format(wifi_device.name) in line:
                        if right_lines:
                            right_lines = False
                        else:
                            right_lines = True
                        pass
                    elif right_lines:
                        pass
                    else:
                        f.write(line)
    except Hotspot.DoesNotExist:
        print('in the expect')
        the_hotspot, created = Hotspot.objects.get_or_create(name='olympus',password='keraunos',wifi_device=wifi_device)
#        hostapd_origin = file_ending(getcwd() + '/oikos/hotspot/hostapd.conf')
#        if '\n' not in hostapd_origin[-1]:
#            with open(getcwd() + '/oikos/hotspot/hostapd.conf', 'a') as f:
#                f.write('\n')
        with open(getcwd() + '/oikos/hotspot/hostapd_sample.conf', 'r') as f_hotspot:
            hostapd_sample = f_hotspot.read()
        hostapd_sample = hostapd_sample.replace('####', wifi_device.name)
        hostapd_sample = hostapd_sample.replace('%%%%', the_hotspot.name)
        hostapd_sample = hostapd_sample.replace('++++', the_hotspot.password)
        with open('/etc/default/hostapd', 'r') as f:
            hostapd = f.readlines()
        if (getcwd() + '/oikos/hotspot/hostapd.conf') not in hostapd:
            with open(getcwd() + '/oikos/hotspot/hostapd', 'w') as f:
                for line in hostapd:
                    if 'DAEMON_CONF=' in line:
                        f.write('DAEMON_CONF="{}/oikos/hotspot/hostapd.conf"'.format(getcwd()) + "\n")
                    else:
                        f.write(line)
            new_conf = getcwd() + '/oikos/hotspot/hostapd.conf'
            default_conf = '/etc/default/hostapd'
            Popen(['sudo', 'cp', '-f', new_conf, default_conf], stdout=PIPE, stderr=PIPE)
        with open(getcwd() + '/oikos/hotspot/hostapd.conf', 'w') as hostapd_conf:
            print('writing')
            print(hostapd_sample)
            hostapd_conf.write(hostapd_sample)
        new_conf = getcwd() + '/oikos/hotspot/hostapd.conf'
        default_conf = '/etc/default/hostapd'
        Popen(['sudo', 'cp', '-f', new_conf, default_conf], stdout=PIPE, stderr=PIPE)
        Popen(['sudo', 'ifconfig', wifi_device.name, 'down'], stdout=PIPE, stderr=PIPE)
        with open('/etc/dhcpcd.conf', 'r') as f:
            dhcpcd = f.readlines()
        print(dhcpcd)
        if not wifi_device.name in dhcpcd:
            if 'denyinterfaces' in dhcpcd:
                with open(getcwd() + '/oikos/hotspot/dhcpcd.conf', 'w') as f:
                    for line in dhcpcd:
                        if 'denyinterfaces' in dhcpcd:
                            f.write(line + ' ' + wifi_device.name)
                            print('writing deny line')
                        else:
                            f.write(line)
                new_conf = getcwd() + '/oikos/hotspot/dhcpcd.conf'
                default_conf = '/etc/dhcpcd.conf'
                Popen(['sudo', 'cp', '-f', new_conf, default_conf], stdout=PIPE, stderr=PIPE)
            else:
                if '\n' in dhcpcd[-1]:
                    dhcpcd.append('denyinterfaces ' + wifi_device.name)
                else:
                    dhcpcd.append('\n' + 'denyinterfaces ' + wifi_device.name)
                with open(getcwd() + '/oikos/hotspot/dhcpcd.conf', 'w') as f:
                    for line in dhcpcd:
                        f.write(line)
                new_conf = getcwd() + '/oikos/hotspot/dhcpcd.conf'
                default_conf = '/etc/dhcpcd.conf'
                Popen(['sudo', 'cp', '-f', new_conf, default_conf], stdout=PIPE, stderr=PIPE)
        Popen(['sudo', 'systemctl', 'daemon-reload'], stdout=PIPE, stderr=PIPE)
        Popen(['sudo', 'systemctl', 'restart', 'hostapd'], stdout=PIPE, stderr=PIPE)
        Popen(['sudo', 'systemctl', 'restart', 'dhcpcd'], stdout=PIPE, stderr=PIPE)
        Popen(['sudo', 'ifconfig', wifi_device.name, 'up'], stdout=PIPE, stderr=PIPE)
        hostapd_boot = Popen(['sudo', 'hostapd', '-B', getcwd() + '/oikos/hotspot/hostapd.conf'], stdout=PIPE, stderr=PIPE)
        the_hotspot.active = True
        the_hotspot.save()
