# Create your views here.

def home(request):
    from datetime import datetime
    zero_now = datetime.now()
    first_now = datetime.now()
    from os import getcwd, popen
    from subprocess import Popen, PIPE, check_output
    from re import search

    from .bluetooth_tools import bluetooth_scan

    from django.shortcuts import render
    from django.http import HttpResponseRedirect

    from .models import Wifi, WifiDevice, Hotspot, Bluetooth, BluetoothDevice

    from .forms import WifiDeviceForm, WifiForm, WifiForgetForm, HotspotForm, PowerOffForm, BluetoothPrimalForm, BluetoothForm
    widi_devices = WifiDevice.objects.all()
    for widi_device in widi_devices:
        print(widi_device.name)
    then_now = datetime.now() - first_now
    first_now = datetime.now()
    if BluetoothDevice.objects.filter(powered=True).count() > 0:
        print("{} {}minutes ".format(then_now.days, then_now.seconds // 3600))
        bluetooth_active, err = Popen(['systemctl', 'is-active', 'bluetooth'],stdout=PIPE, stderr=PIPE).communicate()
        if bluetooth_active.decode('utf-8').replace('\n', '') == 'active':
            if Bluetooth.objects.filter(primal=True).count() == 0:
                controller = bluetooth_scan.controller_show()
                bluetooth_device = BluetoothDevice.objects.get(id=controller)
                bluetooth_scan.main(bluetooth_device_id=controller)
                print('scan bluetooth')
                bluetooth_primals = Bluetooth.objects.filter(primal=True,bluetooth_device=bluetooth_device)
                bluetooth_devices = Bluetooth.objects.filter(available=True,bluetooth_device=bluetooth_device)
            else:
                bluetooth_devices = Bluetooth.objects.filter(available=True,bluetooth_device=bluetooth_device)
                bluetooth_primals = None
            if bluetooth_primals.count() == 0:
                bluetooth_primals = Bluetooth.objects.filter(name='G5',bluetooth_device=bluetooth_device)
        else:
            if Bluetooth.objects.filter(primal=True).count() == 0:
                bluetooth_scan.turn_on()
                controller = bluetooth_scan.controller_show()
                bluetooth_device = BluetoothDevice.objects.get(id=controller)
                bluetooth_scan.main(bluetooth_device_id=controller)
                print('scan bluetooth')
                bluetooth_devices = Bluetooth.objects.filter(available=True,bluetooth_device=bluetooth_device)
                bluetooth_primals = Bluetooth.objects.filter(primal=True,bluetooth_device=bluetooth_device)
    else:
        bluetooth_primals = None
        bluetooth_devices = None
    then_now = datetime.now() - first_now
    first_now = datetime.now()
    print("{} {}minutes ".format(then_now.days, then_now.seconds // 3600))
    available_interfaces = popen("ip -br addr show | awk '{print $1}'").read()
    print('back')
    ifconfig = check_output(['ifconfig']).decode('utf-8')
    print(ifconfig)
    Wifi.objects.filter(connected=False).update(available=False)
    for available_interface in available_interfaces.split('\n'):
        wifi_device = None
        if ('wlan' in available_interface) and (available_interface in ifconfig):
            print(available_interface)
            wifi_device, created = WifiDevice.objects.get_or_create(name=available_interface)
            wifi_device.active = True
            wifi_device.save()
            ifconfig = check_output(['ifconfig', available_interface]).decode('utf-8')
            print('hello')
            print(ifconfig)
            if "inet " in ifconfig:
                print("is inet wlan0")
                iwconfig = check_output(['iwconfig', available_interface]).decode('utf-8')
                word = search('ESSID:"(.+?)"', iwconfig)
                if word and ('Master' not in iwconfig):
                    print("is word wlan0")
                    ssid = word.group(1)
                    active_wifi = Wifi.objects.get(ssid=ssid)
                    active_wifi.connected = True
                    active_wifi.save()
                else:
                    print("is word wlan0")
                    Wifi.objects.all().update(connected=False)
            else:
                print('removing interface')
                wifi_device, created = WifiDevice.objects.get_or_create(name=available_interface)
                Wifi.objects.all().update(connected=False)
        elif ('wlan' in available_interface) and (available_interface not in ifconfig):
            print('wlan but not in ifconfig')
            print(available_interface)
            wifi_device, created = WifiDevice.objects.get_or_create(name=available_interface)
            wifi_device.active = False
            wifi_device.save()
            Wifi.objects.all().update(connected=False)
    then_now = datetime.now() - first_now
    first_now = datetime.now()
    print("{} {}minutes ".format(then_now.days, then_now.seconds // 3600))
    print('going')
    wifi_set = WifiDevice.objects.all()
    for wifi_s in wifi_set:
        if ('inet' in check_output(['ifconfig', wifi_s.name]).decode('utf-8')) and ('Master' in check_output(['iwconfig', wifi_s.name]).decode('utf-8')):
            with open(getcwd() + "/oikos/hotspot/hostapd.conf", 'r') as f:
                hostapd_conf = f.read()
            if wifi_s.name in hostapd_conf:
                print('wifi_s in host')
                print(Hotspot.objects.filter(active=True))
                hotspot = Hotspot.objects.filter(active=True)
            else:
                Hotspot.objects.filter(wifi_device=wifi_s).update(active=False)
                hotspot = None
        else:
            Hotspot.objects.filter(wifi_device=wifi_s).update(active=False)
            hotspot = None
    print('gone')
    print('corrosive')
    print(hotspot)
    then_now = datetime.now() - first_now
    first_now = datetime.now()
    print("{} {}minutes ".format(then_now.days, then_now.seconds // 3600))
    bluetooths = BluetoothDevice.objects.all()
    print('bluetooths')
    print(bluetooths)

    available_wifis = Wifi.objects.filter(available=True).order_by('-strength')
    for available_wifi in available_wifis:
        print(available_wifi.ssid)
    then_now = datetime.now() - first_now
    first_now = datetime.now()
    print("{} {}minutes ".format(then_now.days, then_now.seconds // 3600))
    wifi_device_form = WifiDeviceForm(request.POST)
    wifi_form = WifiForm(request.POST)
    wifi_forget_form = WifiForgetForm(request.POST)
    hotspot_form = HotspotForm(request.POST)
    power_form = PowerOffForm(request.POST)
    bluetooth_primals_form = BluetoothPrimalForm(request.POST)
    bluetooth_form = BluetoothForm(request.POST)
    print(wifi_form)
    then_now = datetime.now() - first_now
    print("{} {}minutes ".format(then_now.days, then_now.seconds // 3600))
    then_zero = datetime.now() - zero_now
    print("{} {}minutes ".format(then_zero.days, then_zero.seconds // 3600))
    return render(request, 'oikos/home.html', {'wifi_set': wifi_set, 'available_wifis': available_wifis, 'bluetooths': bluetooths, 'bluetooth_primals': bluetooth_primals, 'bluetooth_primals_form': bluetooth_primals_form, 'bluetooth_devices': bluetooth_devices, 'wifi_device_form': wifi_device_form, 'hotspot': hotspot, 'hotspot_form': hotspot_form, 'wifi_form': wifi_form, 'wifi_forget_form': wifi_forget_form, 'power_form': power_form})

def wifi_turn(request, wifi_device_id):
    from subprocess import Popen, PIPE, check_output
    from time import sleep

    from .wifi_tools import wifi_scan_connect
    from .hotspot import add_hotspot

    from django.http import HttpResponseRedirect

    from .models import WifiDevice, Wifi, Hotspot
    from .forms import WifiDeviceForm

    wifi_device_form = WifiDeviceForm(request.POST)
    print("keyword_delete views")
    if request.method == 'POST':
        if wifi_device_form.is_valid():
            try:
                wifi_device = WifiDevice.objects.get(id=wifi_device_id)
            except WifiDevice.DoesNotExist:
                return HttpResponseRedirect('/')
            print(wifi_device)
            print(wifi_device.id)
            wifi_device.save()
            ifconfig = check_output(['ifconfig']).decode('utf-8')
            print(ifconfig)
            if wifi_device.name in ifconfig:
                print('bringing it down')
                iwconfig = check_output(['iwconfig', wifi_device.name]).decode('utf-8')
                if 'Master' in iwconfig:
                    add_hotspot.delete_hotspot(wifi_device.id)
                wifi_scan_connect.turn_off(wifi_device.name)
                print(wifi_device.name)
            else:
                Wifi.objects.filter(wifi_device__name=wifi_device.name).update(available=False,connected=False)
                sub_proc = check_output(['sudo', 'ifconfig', wifi_device.name, 'down']).decode('utf-8')
                add_hotspot.delete_hotspot(wifi_device.id)
                Hotspot.objects.filter(wifi_device__name=wifi_device.name).update(active=False)
                Popen(['sudo', 'ifconfig', wifi_device.name, 'up'], stdout=PIPE, stderr=PIPE)
                ifconfig = check_output(['ifconfig']).decode('utf-8')
                while wifi_device.name not in ifconfig:
                    sleep(0.10)
                    print(wifi_device.name)
                    print(ifconfig)
                    ifconfig = check_output(['ifconfig']).decode('utf-8')
                wifi_scan_connect.main(wifi_device.name)

    return HttpResponseRedirect('/')

def wifi_scan(request):
    from .wifi_tools import wifi_scan_connect

    from django.shortcuts import get_object_or_404
    from django.template.loader import render_to_string
    from django.http import HttpResponse

    from .models import Wifi, WifiDevice
    from .forms import WifiForm, WifiForgetForm

    wifi_form = WifiForm(request.POST)

    pk = int(request.POST['id'])
    wifi_object = get_object_or_404(WifiDevice, pk=pk)

    if request.method == 'POST':
        wifi_scan_connect.scan_only(wifi_object.name)

    available_wifis = Wifi.objects.filter(available=True)
    for available_wifi in available_wifis:
        print(available_wifi.ssid)

    wifi_forget_form = WifiForgetForm(request.POST)
    html = render_to_string('oikos/wifi-scan.html', {'available_wifis': available_wifis, 'wifi_single': wifi_object, 'wifi_form': wifi_form, 'wifi_forget_form': wifi_forget_form}, request=request)
    return HttpResponse(html)

def wifi_connect(request):
    from subprocess import Popen, PIPE

    from .wifi_tools import wifi_scan_connect
    from .hotspot import add_hotspot

    from django.http import HttpResponseRedirect

    from .models import Wifi, WifiDevice

    from .forms import WifiForm

    wifi_form = WifiForm(request.POST)
    print('hello')
    print(wifi_form)
    if request.method == 'POST':
        if wifi_form.is_valid():
            wifi_form_wait = wifi_form.save(commit=False)
            update_wifi = Wifi.objects.get(mac_address=wifi_form_wait.mac_address)
            update_wifi.ssid = wifi_form_wait.ssid
            if update_wifi.encryption_type != 'None':
                update_wifi.password = wifi_form_wait.password
            else:
                update_wifi.password = ''
            print('gonna connect')
            update_wifi.wifi_device = WifiDevice.objects.get(name=wifi_form_wait.device_name)
            update_wifi.save()
            Popen(['sudo', 'ifconfig', update_wifi.wifi_device.name, 'down'], stdout=PIPE, stderr=PIPE)
            add_hotspot.delete_hotspot(update_wifi.wifi_device.id)
            wifi_scan_connect.connect(update_wifi.mac_address,wifi_form_wait.device_name)

    return HttpResponseRedirect('/')

def wifi_forget(request):
    from subprocess import Popen, PIPE

    from .wifi_tools import wifi_scan_connect

    from django.http import HttpResponseRedirect

    from .models import Wifi

    from .forms import WifiForgetForm

    wifi_forget_form = WifiForgetForm(request.POST)
    if request.method == 'POST':
        if wifi_forget_form.is_valid():
            wifi_forget_form_wait = wifi_forget_form.save(commit=False)
            wifi = Wifi.objects.filter(mac_address=wifi_forget_form_wait.mac_address)
            wifi.update(known=False,connected=False,password=None)
            wifi_scan_connect.turn_off(wifi.wifi_device.name)
            Popen(['sudo', 'ifconfig', wifi_device, 'up'], stdout=PIPE, stderr=PIPE)

    return HttpResponseRedirect('/')

def bluetooth_turn(request, bluetooth_device_id):
    from subprocess import Popen, PIPE

    from .bluetooth_tools import bluetooth_scan

    from django.http import HttpResponseRedirect
    from django.shortcuts import get_object_or_404

    from .models import Bluetooth, BluetoothDevice

    bluetooth = get_object_or_404(BluetoothDevice, pk=bluetooth_device_id)
    print('got 404')
    print(bluetooth)
    if request.method == 'POST':
        is_active, err = Popen(['systemctl', 'is-active', 'bluetooth'],stdout=PIPE, stderr=PIPE).communicate()
        if is_active.decode('utf-8').replace('\n', '') == 'active':
            print('turning off')
            bluetooth_scan.turn_off(bluetooth_device_id)
        else:
            print('turning on')
            bluetooth_scan.turn_on()
            controller = bluetooth_scan.controller_show()
            bluetooth_device = BluetoothDevice.objects.get(id=controller)
            bluetooth_scan.main()
    return HttpResponseRedirect('/')


def bluetooth_scan(request):
    from .bluetooth_tools import bluetooth_scan

    from django.shortcuts import get_object_or_404
    from django.http import HttpResponse
    from django.template.loader import render_to_string

    from .models import Bluetooth, BluetoothDevice
    from .forms import BluetoothForm

    if request.method == 'POST':
        pk = int(request.POST['id'])
        bluetooth_object = get_object_or_404(BluetoothDevice, pk=pk)
        bluetooth_scan.main(bluetooth_device_id=pk)
        bluetooth_form = BluetoothForm(request.POST)
        bluetooth_devices = Bluetooth.objects.filter(available=True,bluetooth_device=bluetooth_object)
        for bluetooth_device in bluetooth_devices:
            print(bluetooth_device)
        html = render_to_string('oikos/bluetooth-scan.html', {'bluetooth_devices': bluetooth_devices, 'bluetooth_form': bluetooth_form}, request=request)
        return HttpResponse(html)


def bluetooth_pair(request):
    from .bluetooth_tools import bluetooth_scan

    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404

    from .models import Bluetooth

    if request.method == 'POST':
        id = int(request.POST['id'])
        bluetooth_object = get_object_or_404(Bluetooth, pk=id)
        bluetooth_scan.pair(id)
        bluetooth_object = Bluetooth.objects.get(id=id)
        if bluetooth_object.paired:
            data = {'is_paired': True}
        else:
            data = {'is_paired': False}
        return JsonResponse(data)

def hotspot_turn(request, wifi_device_id):
    from os import getcwd

    from django.http import HttpResponseRedirect

    from .models import WifiDevice, Hotspot

    from .hotspot import add_hotspot
    from .wifi_tools import wifi_scan_connect

    print('hotspot')
    if request.method == 'POST':
        try:
            wifi_device = WifiDevice.objects.get(id=wifi_device_id)
        except WifiDevice.DoesNotExist:
            return HttpResponseRedirect('/')
        if Hotspot.objects.filter(active=True,wifi_device=wifi_device).count() > 0:
            print('deleting')
            add_hotspot.delete_hotspot(wifi_device.id)
        else:
            if Hotspot.objects.filter(wifi_device=wifi_device,primary=True).count() > 0:
                wifi_scan_connect.turn_off(wifi_device.name)
                add_hotspot.main(wifi_device.id)
            else:
                Hotspot.objects.filter(wifi_device=wifi_device).update(active=False)
                wifi_scan_connect.turn_off(wifi_device.name)
                add_hotspot.main(wifi_device.id)

    return HttpResponseRedirect('/')

def hotspot_submit(request):
    from random import randint

    from django.http import HttpResponseRedirect

    from .models import Hotspot
    from .forms import HotspotForm

    from .hotspot import add_hotspot

    hotspot_form = HotspotForm(request.POST)
    if request.method == 'POST':
        if hotspot_form.is_valid():
            hotspot_form_wait = hotspot_form.save(commit=False)
            the_hotspot = Hotspot.objects.get(hotspot_form.name)
            the_hotspot.name = hotspot_form.name
            the_hotspot.password = hotspot_form.password
            the_hotspot.on_boot = hotspot_form.on_boot
            the_hotspot.save()
            add_hotspot.change(the_hotspot.wifi_device.id)

    return HttpResponseRedirect('/')

def bluetooth_primal_set(request):
    from django.http import HttpResponseRedirect
    from django.contrib.auth.models import User

    from .forms import BluetoothPrimalForm

    if request.method == 'POST':
        bluetooth_primal_form = BluetoothPrimalForm(request.POST)
        if bluetooth_primal_form.is_valid():
            check_worker.main(bluetooth_primal_form.username)
            try:
                User.objects.get(bluetooth_primal_form.username)
            except:
                that_user = User.objects.create_user(bluetooth_primal_form.username)
            bluetooth_primal_form.user = that_user
            bluetooth_primal_form.authenticated = True
            bluetooth_primal_form.save()

    return HttpResponseRedirect('/')

def power_off(request):
    from subprocess import Popen, PIPE

    from django.http import HttpResponseRedirect

    if request.method == 'POST':
        Popen(['sudo', 'halt'], stdout=PIPE, stderr=PIPE)

    return HttpResponseRedirect('/')
