# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from sos.plugins import Plugin, RedHatPlugin, DebianPlugin, UbuntuPlugin
import os
import subprocess


class Nvme(Plugin, RedHatPlugin, DebianPlugin, UbuntuPlugin):
    """Collect config and system information about NVMe devices"""

    plugin_name = "nvme"
    packages = ('nvme-cli',)
    devices = []

    def copy_spec(self):
        """
        Loop through all NVMe devices in /sys/block/<nvme-device>/
        and get the files inside queue/, device/, integrity/ and mq/
        """

        i = 0
        self.devices = [dev for dev in os.listdir('/sys/block/') if dev.startswith('nvme')]
        for dev in self.devices:
            queue_files = subprocess.check_output(
                    "ls -1 /sys/block/%s/queue/*" % dev,
                    shell=True).rstrip()

            # in python 3.3+ prefix b' is not ignored
            # bytes.decode() get rid of it
            queue_files = bytes.decode(queue_files)
            queue_files = queue_files.splitlines()
            self.add_copy_spec(queue_files)

            device_files = subprocess.check_output(
                    "find /sys/block/%s/device/ -maxdepth 1 -type f" % dev,
                    shell=True).rstrip()
            device_files = bytes.decode(device_files)
            device_files = device_files.splitlines()
            self.add_copy_spec(queue_files)

            general_files = subprocess.check_output(
                    "find /sys/block/%s/ -maxdepth 1 -type f" % dev,
                    shell=True).rstrip()
            general_files = bytes.decode(general_files)
            general_files = general_files.splitlines()
            self.add_copy_spec(general_files)

            integrity_files = subprocess.check_output(
                    "ls -1 /sys/block/%s/integrity/*" % dev,
                    shell=True).rstrip()
            integrity_files = bytes.decode(integrity_files)
            integrity_files = integrity_files.splitlines()
            self.add_copy_spec(integrity_files)

            mq_files = subprocess.check_output(
                    "find /sys/block/%s/mq/ -type f" % dev,
                    shell=True).rstrip()
            mq_files = bytes.decode(mq_files)
            mq_files = mq_files.splitlines()
            self.add_copy_spec(mq_files)

    def setup(self):
        self.copy_spec()

        for dev in self.devices:
            # get block size
            self.add_cmd_output(
                    "sh -c \"lsblk | grep %s | awk '{ print $4 }'\"" % dev,
                    suggest_filename="block-size.%s" % dev)

            # check if the firmware mode is OPAL
            """opal = subprocess.check_output(
                    "cat /proc/cpuinfo | grep firmware | grep OPAL | wc -l",
                    shell=True)
            opal = int(opal)
            if opal == 1:
                grep_op = "mass-storage"
            else:
                grep_op = "pci"""

            op = self.get_cmd_output_now(
                    "cat /proc/cpuinfo | grep firmware | grep OPAL | wc -l")
            
            if op:
                opal = open(op, 'r').read().splitlines()
                if opal == 1:
                    grep_op = "mass-storage"
                else:
                    grep_op = "pci"
            else:
                print "test"

            # get info about slot location and pci location
            """slot = subprocess.check_output(
                    "lscfg -vl %s | grep nvme | grep %s | awk '{ print $4 }'"
                    % (dev[0:-2], grep_op), shell=True).strip()
            pci = subprocess.check_output(
                    "lscfg -vl %s | grep nvme | grep %s | awk '{ print $1 }'"
                    % (dev[0:-2], grep_op), shell=True).strip()"""

            self.add_cmd_output([
                                "nvme list",
                                "nvme list-ns /dev/%s" % dev,
                                "nvme fw-log /dev/%s" % dev,
                                "nvme list-ctrl /dev/%s" % dev,
                                "nvme id-ctrl -H /dev/%s" % dev,
                                "nvme id-ns -H /dev/%s" % dev,
                                "nvme smart-log /dev/%s" % dev,
                                "nvme error-log /dev/%s" % dev,
                                "nvme show-regs /dev/%s" % dev])
            """
            self.add_cmd_output("nvme list-ns /dev/%s" % dev)
            self.add_cmd_output("nvme fw-log /dev/%s" % dev)
            self.add_cmd_output("nvme list-ctrl /dev/%s" % dev)
            self.add_cmd_output("nvme id-ctrl -H /dev/%s" % dev)
            self.add_cmd_output("nvme id-ns -H /dev/%s" % dev)
            self.add_cmd_output("nvme smart-log /dev/%s" % dev)
            self.add_cmd_output("nvme error-log /dev/%s" % dev)
            self.add_cmd_output("nvme show-regs /dev/%s" % dev)"""
