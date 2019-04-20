from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class LocalServices(models.Model):
    name = models.TextField(u'worker')
    service_id = models.CharField(max_length=100,null=True)
    worker_number = models.PositiveIntegerField(null=True)

class WifiDevice(models.Model):
    name = models.CharField(max_length=100,null=True,unique=True)
    active = models.BooleanField(default=False)

class Wifi(models.Model):
    name = models.CharField(max_length=100,null=True)
    ssid = models.CharField(max_length=100,null=True)
    mac_address = models.CharField(max_length=100,null=True,unique=True)
    password = models.CharField(max_length=100,null=True)
    encryption_type = models.CharField(max_length=100,null=True)
    available = models.BooleanField(default=False)
    connected = models.BooleanField(default=False)
    strength = models.CharField(max_length=4,null=True)
    known = models.BooleanField(default=False)
    device_name = models.CharField(max_length=100,null=True)
    wifi_device = models.ForeignKey(WifiDevice, on_delete=models.CASCADE,null=True)

class BluetoothDevice(models.Model):
    name = models.CharField(max_length=100,null=True)
    mac_address = models.CharField(max_length=100,null=True,unique=True)
    powered = models.BooleanField(default=False)
    discoverable = models.BooleanField(default=False)
    pairable = models.BooleanField(default=False)

class Bluetooth(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    username = models.TextField(null=True)
    name = models.CharField(max_length=100,null=True)
    mac_address = models.CharField(max_length=100,null=True,unique=True)
    password = models.CharField(max_length=100,null=True)
    email = models.CharField(max_length=100,null=True)
    available = models.BooleanField(default=True)
    paired = models.BooleanField(default=False)
    strength = models.CharField(max_length=4,null=True)
    date_updated = models.DateTimeField(default=timezone.now)
    primal = models.BooleanField(default=False)
    bluetooth_device = models.ForeignKey(BluetoothDevice, on_delete=models.CASCADE,null=True)

class Hotspot(models.Model):
    name = models.CharField(max_length=100,null=True)
    password = models.CharField(max_length=100,null=True)
    wifi_device = models.OneToOneField(WifiDevice,on_delete=models.CASCADE,primary_key=True,unique=True)
    rand_ip = models.PositiveIntegerField(null=True)
    active = models.BooleanField(default=False)
    on_boot = models.BooleanField(default=False)
    primary = models.BooleanField(default=False)

class PowerOff(models.Model):
    shutdown = models.BooleanField(default=False)
