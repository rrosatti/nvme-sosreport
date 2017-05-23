# -*- coding: utf8 -*-
# This is a sosreport plugin to collect configuration details and system information about NVMe devices

from sos.plugins import Plugin, RedHatPlugin

class NvmePlugin(Plugin, RedHatPlugin):
    """Collect config and system information about NVMe devices"""

    plugin_name = "nvme"
    packages = ('nvme-cli',)
    
    def setup(self):
        self.add_copy_spec([
	    "/sys/block/nvme1n1/device/firmware_rev",
	    "/sys/block/nvme1n1/device/model"
	])

	self.add_cmd_output("nvme list", root_symlink="nvme");
	
	

