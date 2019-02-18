from os import getcwd, stat
from subprocess import Popen, PIPE, check_output

from oikos.models import WifiDevice, Hotspot

def file_ending(path):
    with open(path, 'r') as f:
        return f.readlines()

def delete_hotspot(id):
    wifi_device = WifiDevice.objects.get(id=id)
    the_hotspot = Hotspot.objects.get(wifi_device=wifi_device)
    the_hotspot.active = False
    the_hotspot.save()
    all_hotspots = Hotspot.objects.filter(active=True)
    if all_hotspots.count() == 0:
        with open(getcwd() + '/oikos/hotspot/hostapd.conf', 'w'):
            pass
    else:
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
    all_on_boot_hotspots = Hotspot.objects.filter(on_boot=True)
    if all_on_boot_hotspots.count() == 0:
        with open('/etc/default/hostapd', 'r') as f:
            hostapd = f.readlines()
        with open(getcwd() + '/oikos/hotspot/hostapd', 'w') as f:
            for line in hostapd:
                if 'DAEMON_CONF=' in line:
                    f.write('DAEMON_CONF=""')
                else:
                    f.write(line)

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
    with open(getcwd() + '/oikos/hotspot/dhcpcd.conf', 'r') as f:
        new_conf = f.read()
    with open('/etc/dhcpcd.conf', 'w') as default_conf:
        default_conf.write(new_conf)
    Popen(['sudo', 'systemctl', 'daemon-reload'], stdout=PIPE, stderr=PIPE)
    Popen(['sudo', 'systemctl', 'restart dhcpcd'], stdout=PIPE, stderr=PIPE)

def change(id):
    wifi_device = WifiDevice.objects.get(id=id)
    all_hotspots = Hotspot.objects.filter(active=True)
    all_on_boot_hotspots = Hotspot.objects.filter(on_boot=True)
    if all_hotspots.count() == 0:
        with open(getcwd() + '/oikos/hotspot/hostapd.conf', 'w'):
            pass
    the_hotspot = Hotspot.objects.get(wifi_device=wifi_device)
    with open('/etc/default/hostapd', 'r') as f:
        hostapd = f.readlines()
    if the_hotspot.on_boot == True:
        with open(getcwd() + '/oikos/hotspot/hostapd', 'w') as f:
            for line in hostapd:
                if 'DAEMON_CONF=' in line:
                    f.write('DAEMON_CONF="{}/oikos/hotspot/hostapd.conf"'.format(getcwd()))
                else:
                    f.write(line)
    elif all_on_boot_hotspots.count() == 0:
        with open(getcwd() + '/oikos/hotspot/hostapd', 'w') as f:
            for line in hostapd:
                if 'DAEMON_CONF=' in line:
                    f.write('DAEMON_CONF=""')
                else:
                    f.write(line)
    with open(getcwd() + '/oikos/hotspot/hostapd.conf', 'r') as f:
        hostapd_conf = f.readlines()
    with open(getcwd() + '/oikos/hotspot/hostapd.conf', 'w') as f:
        for line in hostapd_conf:
            if "interface=" in line:
                f.write("interface={}".format(the_hotspot.wifi_device.name))
            elif "wpa_passphrase=" in line:
                f.write("wpa_passphrase={}".format(the_hotspot.password))
            elif "ssid=" in line:
                f.write("ssid={}".format(the_hotspot.name))
            else:
                f.write(line)
    Popen(['sudo', 'ifconfig', the_hotspot.wifi_device.name, 'up'], stdout=PIPE, stderr=PIPE)
    if the_hotspot.on_boot:
        Popen(['sudo', 'systemctl', 'restart', 'hostapd'], stdout=PIPE, stderr=PIPE)
    else:
        Popen(['sudo', 'hostapd', '-B', getcwd() + '/oikos/hotspot/hostapd.conf'], stdout=PIPE, stderr=PIPE)
    return True

def main(id):

    wifi_device = WifiDevice.objects.get(id=id)
    all_hotspot = Hotspot.objects.filter(active=True)
    if all_hotspot.count() == 0:
        with open(getcwd() + '/oikos/hotspot/hostapd.conf', 'w'):
            pass
    try:
        print('in the try')
        the_hotspot = Hotspot.objects.get(wifi_device=wifi_device)
        with open(getcwd() + '/oikos/hotspot/hostapd.conf', 'r') as f:
            hostapd = f.readlines()
        if wifi_device.name in hostapd and the_hotspot.active and wifi_device.name in check_output(['sudo', 'ifconfig', '-a']).decode('utf-8'):
            right_lines = False
            with open(getcwd() + '/oikos/hotspot/hostapd.conf', 'r') as f:
                hostapd = f.readlines()
            with open(getcwd() + '/oikos/hotspot/hostapd.conf', 'w') as f:
                for line in hostapd:
                    if 'inteface={}'.format(wifi_device.name) in line:
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
    if the_hotspot.on_boot == True:
        with open(getcwd() + '/oikos/hotspot/hostapd', 'w') as f:
            for line in hostapd:
                if 'DAEMON_CONF=' in line:
                    f.write('DAEMON_CONF="{}/oikos/hotspot/hostapd.conf"'.format(getcwd()))
                else:
                    f.write(line)
    else:
        with open(getcwd() + '/oikos/hotspot/hostapd', 'w') as f:
            for line in hostapd:
                if 'DAEMON_CONF=' in line:
                    f.write('DAEMON_CONF="{}/oikos/hotspot/hostapd.conf"'.format(getcwd()))
                else:
                    f.write(line)
    with open(getcwd() + '/oikos/hotspot/hostapd', 'r') as f:
        hostapd = f.read()
    with open('/etc/default/hostapd', 'w') as default_conf:
        default_conf.write(hostapd)
    if (stat(getcwd() + "/oikos/hotspot/hostapd.conf").st_size > 0):
        with open(getcwd() + '/oikos/hotspot/hostapd.conf', 'r') as f:
            hostapd_origin = f.read()
    else:
        hostapd_origin = ''
    with open(getcwd() + '/oikos/hotspot/hostapd_sample.conf', 'r') as f_hotspot:
        hostapd_sample = f_hotspot.read()
    hostapd_sample = hostapd_sample.replace('####', wifi_device.name)
    hostapd_sample = hostapd_sample.replace('%%%%', the_hotspot.name)
    hostapd_sample = hostapd_sample.replace('++++', the_hotspot.password)
    with open(getcwd() + '/oikos/hotspot/hostapd.conf', 'w') as f:
        f.write(hostapd_sample + '\n' + hostapd_origin)
    Popen(['sudo', 'ifconfig', wifi_device.name, 'down'], stdout=PIPE, stderr=PIPE)
    with open('/etc/dhcpcd.conf', 'r') as f:
        dhcpcd = f.readlines()
    print(dhcpcd)
    if not any(wifi_device.name in line for line in dhcpcd):
        if 'denyinterfaces' in dhcpcd:
            with open(getcwd() + '/oikos/hotspot/dhcpcd.conf', 'w') as f:
                for line in dhcpcd:
                    if 'denyinterfaces' in dhcpcd:
                        f.write(line + ' ' + wifi_device.name)
                        print('writing deny line')
                    else:
                        f.write(line)
            with open(getcwd() + '/oikos/hotspot/dhcpcd.conf', 'r') as f:
                new_conf = f.readlines()
            with open('/etc/dhcpcd.conf', 'w') as default_dhcpcd:
                default_dhcpcd.write(new_conf)
        else:
            if '\n' in dhcpcd[-1]:
                dhcpcd.append('denyinterfaces ' + wifi_device.name)
            else:
                dhcpcd.append('\n' + 'denyinterfaces ' + wifi_device.name)
            with open(getcwd() + '/oikos/hotspot/dhcpcd.conf', 'w') as f:
                for line in dhcpcd:
                    f.write(line)
            with open(getcwd() + '/oikos/hotspot/dhcpcd.conf', 'r') as f:
                new_conf = f.read()
            with open('/etc/dhcpcd.conf', 'w') as default_dhcpcd:
                default_dhcpcd.write(new_conf)
    Popen(['sudo', 'systemctl', 'daemon-reload'], stdout=PIPE, stderr=PIPE)
    Popen(['sudo', 'systemctl', 'restart', 'hostapd'], stdout=PIPE, stderr=PIPE)
    Popen(['sudo', 'systemctl', 'restart', 'dhcpcd'], stdout=PIPE, stderr=PIPE)
    Popen(['sudo', 'ifconfig', wifi_device.name, 'up'], stdout=PIPE, stderr=PIPE)
    Popen(['sudo', 'hostapd', '-B', getcwd() + '/oikos/hotspot/hostapd.conf'], stdout=PIPE, stderr=PIPE)
    the_hotspot.active = True
    the_hotspot.save()
