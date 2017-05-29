# -*- coding: utf8 -*-
# This is a sosreport plugin to collect configuration details and system information about NVMe devices

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
    	    path = "/sys/block/nvme%dn1" % i
	    temp = [
                "%s/size" % path,
                "%s/dev" % path,
                "%s/wwid" % path,
                "%s/queue/hw_sector_size" % path,
                "%s/queue/logical_block_size" % path,
                "%s/queue/max_hw_sectors_kb" % path,
                "%s/queue/max_segments" % path,
                "%s/queue/max_segment_size" % path,
                "%s/queue/nr_requests" % path,
                "%s/queue/physical_block_size" % path,
                "%s/device/firmware_rev" % path,
                "%s/device/model" % path,
                "%s/device/serial" % path]
	    spec = spec + temp
    	    i += 1
        return spec

    def setup(self):
        spec = self.get_spec()
	self.add_copy_spec(spec)

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
                slot = subprocess.check_output("lscfg -vl %s | grep nvme | grep %s | awk '{ print $4 }'" % (dev[0:-2], grep_op), shell=True).strip()
                pci = subprocess.check_output("lscfg -vl %s | grep nvme | grep %s | awk '{ print $1 }'" % (dev[0:-2], grep_op), shell=True).strip()

                self.add_cmd_output("sh -c \"lscfg -vl %s | grep nvme | grep %s | awk '{ print $4 }'\"" % (dev[0:-2], grep_op), suggest_filename="slot_loc.%s" % dev)
                self.add_cmd_output("sh -c \"lscfg -vl %s | grep nvme | grep %s | awk '{ print $1 }'\"" % (dev[0:-2], grep_op), suggest_filename="pci_loc.%s" % dev)
                self.add_cmd_output("sh -c \"lspci -vs %s | grep 'Non-Volatile memory controller' | cut -c 46-\"" % pci.strip(), suggest_filename="pci_vdid.%s" % dev)
                self.add_cmd_output("sh -c \"lspci -vs %s | grep Subsystem | cut -c 13-\"" % pci.strip(), suggest_filename="pci_ssid.%s" % dev)
	
