from django import forms
from .models import WifiDevice, Wifi, Hotspot, PowerOff, Bluetooth

class WifiDeviceForm(forms.ModelForm):
    class Meta:
        model = Wifi
        fields = ['name','id']
        name = forms.CharField(label='name',required=True)

class WifiForm(forms.ModelForm):
    class Meta:
        model = Wifi
        fields = ['ssid','password','mac_address','device_name']
        ssid = forms.CharField(label='ssid',required=True)
        password = forms.CharField(widget=forms.PasswordInput)
        mac_address = forms.CharField(label='mac_address',required=True)
        device_name = forms.CharField(label='device_name',required=True)

class WifiForgetForm(forms.ModelForm):
    class Meta:
        model = Wifi
        fields = ['mac_address']
        forms.CharField(label='mac_address',required=True)

class HotspotForm(forms.ModelForm):
    class Meta:
        model = Hotspot
        fields = ['name','password','on_boot']
        name = forms.CharField(label='name',required=True)
        password = forms.CharField(widget=forms.PasswordInput,required=True)
        on_boot = forms.BooleanField(label='on_boot',required=True,widget=forms.CheckboxInput())

class PowerOffForm(forms.ModelForm):
    class Meta:
        model = PowerOff
        fields = ['shutdown']

class BluetoothPrimalForm(forms.ModelForm):
    class Meta:
        model = Bluetooth
        fields = ['username','mac_address','password','email']
        password = forms.CharField(widget=forms.PasswordInput)

class BluetoothForm(forms.ModelForm):
    class Meta:
        model = Bluetooth
        fields = ['username','mac_address']
