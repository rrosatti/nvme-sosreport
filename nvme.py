### This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from sos.plugins import Plugin, RedHatPlugin, DebianPlugin
import os, subprocess

class NvmePlugin(Plugin, RedHatPlugin, DebianPlugin):
    """Collect config and system information about NVMe devices"""

    plugin_name = "nvme"
    devices = [] 

    # get the files for every nvme device
    def get_spec(self):  
        i = 0
	spec = []
	while os.path.isdir('/sys/block/nvme%dn1' % i):
	    self.devices.append("nvme%dn1" % i)
	    
	    queue_files = subprocess.check_output("ls -1 /sys/block/nvme%dn1/queue/*" % i, shell=True).rstrip()
	    queue_files = queue_files.splitlines()
	    for q in queue_files:
		self.add_copy_spec(q)

	    device_files = subprocess.check_output("find /sys/block/nvme%dn1/device/ -maxdepth 1 -type f" % i, shell=True).rstrip()
	    device_files = device_files.splitlines()
	    for d in device_files:
		self.add_copy_spec(d)

	    general_files = subprocess.check_output("find /sys/block/nvme%dn1/ -maxdepth 1 -type f" % i, shell=True).rstrip()
	    general_files = general_files.splitlines()
	    for g in general_files:
		self.add_copy_spec(g)
	
	    integrity_files = subprocess.check_output("ls -1 /sys/block/nvme%dn1/integrity/*" % i, shell=True).rstrip()
	    integrity_files = integrity_files.splitlines()
	    for ing in integrity_files:
		self.add_copy_spec(ing)
	 
	    mq_files = subprocess.check_output("find /sys/block/nvme%dn1/mq/ -type f" % i, shell=True).rstrip()
	    mq_files = mq_files.splitlines()
	    for m in mq_files:
		self.add_copy_spec(m)	

	    i += 1

        return spec

    def setup(self):
        spec = self.get_spec()
	#self.add_copy_spec(spec)

	# check if nvme-cli package is installed
	if self.is_installed("nvme-cli"):
	    self.add_cmd_output("nvme list")
            for dev in self.devices:
                self.add_cmd_output("nvme list-ns /dev/%s" % dev, suggest_filename="list-ns.%s" % dev)
                self.add_cmd_output("nvme fw-log /dev/%s" % dev, suggest_filename="fw-log.%s" % dev)
                self.add_cmd_output("nvme list-ctrl /dev/%s" % dev, suggest_filename="list-ctrl.%s" % dev)
                self.add_cmd_output("nvme id-ctrl -H /dev/%s" % dev, suggest_filename="id-ctrl.%s" % dev)
                self.add_cmd_output("nvme id-ns -H /dev/%s" % dev, suggest_filename="id-ns.%s" % dev)
                self.add_cmd_output("nvme smart-log /dev/%s" % dev, suggest_filename="smart-log.%s" % dev)
                self.add_cmd_output("nvme error-log /dev/%s" % dev, suggest_filename="error-log.%s" % dev)
                self.add_cmd_output("sh -c \"lsblk | grep %s | awk '{ print $4 }'\"" % dev, suggest_filename="block-size.%s" % dev)

                opal = subprocess.check_output("cat /proc/cpuinfo | grep firmware | grep OPAL | wc -l", shell=True)
                opal = int(opal)
                if opal == 1:
                    grep_op = "mass-storage"
                else:
                    grep_op = "pci"

                # get info about slot location and pci location
                slot = subprocess.check_output("lscfg -vl %s | grep nvme | grep %s | awk '{ print $4 }'"
			% (dev[0:-2], grep_op), shell=True).strip()
                pci = subprocess.check_output("lscfg -vl %s | grep nvme | grep %s | awk '{ print $1 }'" 
			% (dev[0:-2], grep_op), shell=True).strip()

                self.add_cmd_output("sh -c \"lscfg -vl %s | grep nvme | grep %s | awk '{ print $4 }'\"" 
			% (dev[0:-2], grep_op), suggest_filename="slot_loc.%s" % dev)
                self.add_cmd_output("sh -c \"lscfg -vl %s | grep nvme | grep %s | awk '{ print $1 }'\"" 
			% (dev[0:-2], grep_op), suggest_filename="pci_loc.%s" % dev)
                self.add_cmd_output("sh -c \"lspci -vs %s | grep 'Non-Volatile memory controller' | cut -c 46-\"" 
			% pci, suggest_filename="pci_vdid.%s" % dev)
                self.add_cmd_output("sh -c \"lspci -vs %s | grep Subsystem | cut -c 13-\"" 
			% pci, suggest_filename="pci_ssid.%s" % dev)
		self.add_cmd_output("sh -c \"lspci -vvs %s | grep '\[PN\]' | awk '{ print $4 }'\"" 
			% pci, suggest_filename="part-number.%s" % dev)
		self.add_cmd_output("sh -c \"lspci -vvs %s | grep '\[EC\]' | awk '{ print $4 }'\"" 
			% pci, suggest_filename="engineering-changes.%s" % dev)		
	else:
	    self.add_string_as_file(("The nvme-cli tool is not installed. If you want more configuration details and" 
	        " system information about NVMe devices, you should install it.\n"), "nvme-cli_not_installed")	
