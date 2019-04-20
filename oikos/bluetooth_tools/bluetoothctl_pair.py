# ReachView code is placed under the GPL license.
# Written by Egor Fedorov (egor.fedorov@emlid.com)
# Copyright (c) 2015, Emlid Limited
# All rights reserved.

# If you are interested in using ReachView code as a part of a
# closed source project, please contact Emlid Limited (info@emlid.com).

# This file is part of ReachView.

# ReachView is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# ReachView is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with ReachView.  If not, see <http://www.gnu.org/licenses/>.

import time
import pexpect
import subprocess
from subprocess import Popen, PIPE
import sys
import re

from decouple import config

class BluetoothctlError(Exception):
    """This exception is raised, when bluetoothctl fails to start."""
    pass


class Bluetoothctl:
    """A wrapper for bluetoothctl utility."""

    def __init__(self):
        sub_proc = Popen('rfkill unblock bluetooth'.split(), stdout=PIPE, stderr=PIPE, shell=True)
        out, errors = sub_proc.communicate()
        self.child = pexpect.spawn("sudo bluetoothctl", echo = False)

    def get_output(self, command):
        """Run a command in bluetoothctl prompt, return output as a list of lines."""
        self.child.send(command + "\n")
        try:
            start_failed = self.child.expect(["#", pexpect.EOF])

        except pexpect.exceptions.TIMEOUT:
            raise BluetoothctlError("Bluetoothctl failed after running " + command)

        print((self.child.before).decode().split("\r\n"))
        return (self.child.before).decode().split("\r\n")

    def start_scan(self):
        """Start bluetooth scanning process."""
        try:
            out = self.get_output("scan on")
            print("out")
            print(out)
        except BluetoothctlError as e:
            print(e)
            return None

    def make_discoverable(self):
        """Make device discoverable."""
        try:
            out = self.get_output("discoverable on")
        except BluetoothctlError as e:
            print(e)
            return None

    def parse_device_info(self, info_string, controller):
        """Parse a string corresponding to a device."""
        device = {}
        block_list = ["[\x1b[0;", "removed"]
        string_valid = not any(keyword in info_string for keyword in block_list)

        if string_valid:
            if controller:
                try:
                    device_position = info_string.index("Controller")
                except ValueError:
                    pass
                else:
                    if device_position > -1:
                        attribute_list = info_string[device_position:].split(" ", 2)
                        device = {
                            "mac_address": attribute_list[1],
                            "name": attribute_list[2]
                        }
            else:
                try:
                    device_position = info_string.index("Device")
                except ValueError:
                    pass
                else:
                    if device_position > -1:
                        attribute_list = info_string[device_position:].split(" ", 2)
                        device = {
                            "mac_address": attribute_list[1],
                            "name": attribute_list[2]
                        }

        return device

    def parse_controller_info(self, info_string):
        search = None
        search_dic = None
        for line in info_string:
            if 'Controller' in line and (not search):
                search = re.search(r'Controller\s*(.*?)\s*\[default\]', line).group(1)
                search_dic = {'name': search[1], 'mac_address': search[0]}
            elif all(item in line for item in ['Powered', 'yes']):
                search_dic['powered'] = True
            elif ('Powered') in line and 'yes' not in line:
                search_dic['powered'] = False
            elif all(item in line for item in ['Discoverable', 'yes']):
                search_dic['discoverable'] = True
            elif 'Discoverable' in line and ('yes' not in line):
                search_dic['discoverable'] = False
            elif all(item in line for item in ['Pairable', 'yes']):
                search_dic['pairable'] = True
            elif 'Pairable' in line and ('yes' not in line):
                search_dic['pairable'] = False

        return search_dic

    def get_available_devices(self):
        """Return a list of tuples of paired and discoverable devices."""
        try:
            out = self.get_output("devices")
            print("out devices")
            print(out)
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            available_devices = []
            for line in out:
                device = self.parse_device_info(line, controller=False)
                if device:
                    available_devices.append(device)

            return available_devices

    def get_paired_devices(self):
        """Return a list of tuples of paired devices."""
        try:
            out = self.get_output("paired-devices")
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            paired_devices = []
            for line in out:
                device = self.parse_device_info(line, controller=False)
                if device:
                    paired_devices.append(device)

            return paired_devices

    def get_discoverable_devices(self):
        """Filter paired devices out of available."""
        available = self.get_available_devices()
        paired = self.get_paired_devices()

        return [d for d in available if d not in paired]

    def get_device_info(self, mac_address):
        """Get device info by mac address."""
        try:
            out = self.get_output("info " + mac_address)
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            return out

    def get_connectable_devices(self):
        """Get a  list of connectable devices.
        Must install 'sudo apt-get install bluez blueztools' to use this"""
        try:
            res = []
            sub_proc = Popen(["hcitool", "scan"], stdout=PIPE, stderr=PIPE, shell=True)  # Requires 'apt-get install bluez'
            out, errors = sub_proc.communicate()
            out = out.split("\n")
            device_name_re = re.compile("^\t([0-9,:,A-F]{17})\t(.*)$")
            for line in out:
                device_name = device_name_re.match(line)
                if device_name != None:
                    res.append({
                            "mac_address": device_name.group(1),
                            "name": device_name.group(2)
                        })
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            return res

    def is_connected(self):
        """Returns True if there is a current connection to any device, otherwise returns False"""
        try:
            res = False
            sub_proc = subprocess.check_output(["hcitool", "con"], stdout=PIPE, stderr=PIPE, shell=True)  # Requires 'apt-get install bluez'
            out = sub_proc.communicate()
            out = out.split("\n")
            mac_addr_re = re.compile("^.*([0-9,:,A-F]{17}).*$")
            for line in out:
                mac_addr = mac_addr_re.match(line)
                if mac_addr != None:
                    res = True
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            return res

    def pair(self, mac_address):
        """Try to pair with a device by mac address."""
        try:
            out = self.get_output("pair " + mac_address)
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            res = self.child.expect(["Failed to pair", "Pairing successful", pexpect.EOF])
            success = True if res == 1 else False
            return success

    def remove(self, mac_address):
        """Remove paired device by mac address, return success of the operation."""
        try:
            out = self.get_output("remove " + mac_address)
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            res = self.child.expect(["not available", "Device has been removed", pexpect.EOF])
            success = True if res == 1 else False
            return success

    def connect(self, mac_address):
        """Try to connect to a device by mac address."""
        try:
            out = self.get_output("connect " + mac_address)
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            res = self.child.expect(["Failed to connect", "Connection successful", pexpect.EOF])
            success = True if res == 1 else False
            return success

    def disconnect(self, mac_address):
        """Try to disconnect to a device by mac address."""
        try:
            out = self.get_output("disconnect " + mac_address)
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            res = self.child.expect(["Failed to disconnect", "Successful disconnected", pexpect.EOF])
            success = True if res == 1 else False
            return success

    def trust(self, mac_address):
        """Trust the device with the given MAC address"""
        try:
            out = self.get_output("trust " + mac_address)
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            res = self.child.expect(["not available", "trust succeeded", pexpect.EOF])
            success = True if res == 1 else False
            return success

    def start_agent(self):
        """Start agent"""
        try:
            out = self.get_output("agent on")
        except BluetoothctlError as e:
            print(e)
            return None

    def default_agent(self):
        """Start default agent"""
        try:
            out = self.get_output("default-agent")
        except BluetoothctlError as e:
            print(e)
            return None

    def list(self):
        """Return a list of tuples of paired and discoverable devices."""
        try:
            out = self.get_output("list")
            print("out list")
            print(out)
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            available_devices = []
            for line in out:
                device = self.parse_device_info(line, controller=True)
                if device:
                    available_devices.append(device)

            return available_devices

    def show(self):
        try:
            out = self.get_output("show")
            print("out show")
            print(out)
        except BluetoothctlError as e:
            print(e)
            return None
        return self.parse_controller_info(out)
