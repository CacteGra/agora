from datetime import datetime, timedelta
from pytz import utc
from subprocess import Popen, PIPE, check_output

from .bluetoothctl.bluetoothctl import Bluetoothctl

from django.db.models import Q

from oikos.models import Bluetooth, BluetoothDevice

def controller_show(bl=None):
    if not bl:
        bl = Bluetoothctl()
    controller = bl.show()
    active_controller, created = BluetoothDevice.objects.get_or_create(mac_address=controller['mac_address'])
    #There's no way to check if bluetooth agent (interface) is down
    active_controller.powered = controller['powered']
    active_controller.discoverable = controller['discoverable']
    active_controller.pairable = controller['pairable']
    active_controller.save()
    return active_controller.id

def pair(bluetooth_id):
    bl = Bluetoothctl()
    bluetooth = Bluetooth.objects.get(id=bluetooth_id)
    if not bluetooth.paired:
        bl.pair(bluetooth.mac_address)
        bluetooth.paired = bl.trust(bluetooth.mac_address)
        bluetooth.save()
    else:
        bl.remove(bluetooth.mac_address)
        if bluetooth.mac_address in bl.get_paired_devices():
            bluetooth.paired = True
        else:
            bluetooth.paired = False
        bluetooth.save()

def scan(bl, bluetooth_device_id):
    bl.start_scan()
    bluetooths = bl.get_available_devices()
    paired = bl.get_paired_devices()
    bluetooth_device = BluetoothDevice.objects.get(id=bluetooth_device_id)
    for bluetooth in bluetooths:
        print(bluetooth)
        the_bluetooth, created = Bluetooth.objects.get_or_create(mac_address=bluetooth['mac_address'])
        if the_bluetooth.name != bluetooth['name']:
            the_bluetooth.name = bluetooth['name']
        the_bluetooth.last_updated = datetime.utcnow()
        the_bluetooth.available = True
        the_bluetooth.bluetooth_device = bluetooth_device
        if any(d['mac_address'] == the_bluetooth.mac_address for d in paired):
            the_bluetooth.paired = True
        the_bluetooth.save()

def get_local_devices(bl):
    local_devices = bl.list()
    Bluetooth.objects.all().update(available=False)
    for local_device in local_devices:
        print('local_device')
        print(local_device['name'])
        local_device_object, created = Bluetooth.objects.get_or_create(mac_address=local_device['mac_address'])
        print(local_device_object)
        local_device_object.name = local_device['name']
        local_device_object.available = True
        local_device_object.save()

def turn_off(bluetooth_device_id):
    print('turning off')
    Popen(['sudo', 'systemctl', 'disable', 'bluetooth'], stdout=PIPE, stderr=PIPE)
    Popen(['sudo', 'systemctl', 'stop', 'bluetooth'], stdout=PIPE, stderr=PIPE)
    sub_proc = Popen(['sudo', 'systemctl', 'stop', 'panr'], stdout=PIPE, stderr=PIPE)
    active_controller, created = BluetoothDevice.objects.get_or_create(id=bluetooth_device_id)
    #There's no way to check if bluetooth agent (interface) is down
    active_controller.powered = False
    active_controller.save()
    Bluetooth.objects.filter(paired=False).delete()
    Bluetooth.objects.all().update(paired=False)
    print('following suit')
    bluetooth_status = check_output(['sudo', 'systemctl', 'status', 'bluetooth']).decode('utf-8')
    print(bluetooth_status)

def turn_on():
    Popen(['sudo', 'systemctl', 'enable', 'bluetooth'], stdout=PIPE, stderr=PIPE)
    Popen(['sudo', 'systemctl', 'start', 'bluetooth'], stdout=PIPE, stderr=PIPE)
    sub_proc = Popen(['sudo', 'systemctl', 'start', 'panr'], stdout=PIPE, stderr=PIPE)
    bluetooth_status = check_output(['sudo', 'systemctl', 'status', 'bluetooth']).decode('utf-8')
    print(bluetooth_status)

def main(bluetooth_device_id=None):

    Bluetooth.objects.filter(Q(date_updated__lte=utc.localize(datetime.utcnow() - timedelta(seconds=30)))).delete()
    bl = Bluetoothctl()
    if not bluetooth_device_id:
        bluetooth_device_id = controller_show(bl=bl)
    print(bluetooth_device_id)
    get_local_devices(bl)
    scan(bl, bluetooth_device_id)
