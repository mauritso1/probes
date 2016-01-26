import sys

from django.db.utils import IntegrityError, DataError
from netaddr import EUI

from web.models import DeviceInfo
from django_mysqlpool import auto_close_db


mac_username_dict = {}
device_info_list = []


@auto_close_db
def save_device_info(device_info):
    try:
        device_info.save()
        return True
    except IntegrityError, e:
        #print e
        return False 
    except DataError, e:
        print e
        print device_info.identity
        print device_info.mac_address

for line in sys.stdin:
    lines = line.split()
    
    if len(lines) == 5 and 'Identity' in line:
        mac_username_dict[previous_line_mac[-17:]] = lines[4]
    
    for a in lines:
        if 'SA' in a:
            previous_line_mac = a


for mac, identity in mac_username_dict.items():
    device_info = DeviceInfo(
        identity = identity,
        mac_address = mac,
        )
    a = save_device_info(device_info)
    if a:
        try:
            oui = EUI(mac).oui
            print mac, ' | ', oui.registration().org.ljust(31), ' | ', identity.ljust(30), ' | ',  a
        except:
            pass
