# -*- coding: utf8 -*-
# This is a sosreport plugin to collect configuration details and system information about NVMe devices

from sos.plugins import Plugin, RedHatPlugin, DebianPlugin
import os

class NvmePlugin(Plugin):
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
    	    spec.extend([
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
        	"%s/device/serial" % path])
    	    i += 1
        return spec

    def setup(self):
        spec = self.get_spec()
	self.add_copy_spec(spec)

	
class RedHatNvmePlugin(NvmePlugin, RedHatPlugin):

    def setup(self):
        super(RedHatNvmePlugin, self).setup()
	# check if nvme-cli package is installed
	ret = os.system("rpm -qa | grep nvme-cli")
	if ret == 0:  
	    for dev in self.devices:  
	    	self.add_cmd_output([
	        	"nvme list",
	 		"nvme fw-log /dev/%s" % dev,
			"nvme list-ctrl /dev/%s" % dev,
			"nvme list-ns /dev/%s" % dev], root_symlink="nvme");


class DebianNvmePlugin(NvmePlugin, DebianPlugin):

    def setup(self):
        super(DebianPlugin, self).setup()	
	# check if nvme-cli package is installed
	ret = os.system("dpkg -s nvme-cli")
	if ret == 0:
	    self.add_cmd_output([
	       	"nvme list",
	 	"nvme fw-log /dev/%s" % dev,
		"nvme list-ctrl /dev/%s" % dev,
		"nvme list-ns /dev/%s" % dev], root_symlink="nvme");

