import sys
import os
from spoofmac.util import random_mac_address

from spoofmac.interface import find_interface
from spoofmac.interface import set_interface_mac

def fakemac(target='eth0'):
    root = os.geteuid() == 0
    if root:
        port, device, _, mac = find_interface(target)
        target_mac = random_mac_address()
        set_interface_mac(device, target_mac, port)
        print('{0} mac changed {1} -> {2}'.format(target, mac, target_mac))
    else:
        print('no mac changed')
