import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import os
import sys
import math
import time
import django
import netaddr
from math import sqrt, log10
from numpy import array
from netaddr import EUI
from web.models import *
from web.trilateration import basicTrilateration
from django.db.models import Count
import matplotlib.patches as mpatches

from collections import defaultdict
from netaddr import EUI                         
from netaddr.core import NotRegisteredError

from test_rssi import time_to_coords, filter_cisco


def mac_coords_dict(qs):
    qs = filter_cisco(qs, mac_address_key='mac_address')
    days = {}

    for day in day_list:
        day_dict_list = defaultdict(list)
        day_dict = {}
        day_qs = qs.filter(time__day=day)
        mac_addresses = day_qs.values_list('mac_address', flat=True).distinct()
        mac_identity = {}
        for mac in mac_addresses:
            try:
                identity = DeviceInfo.objects.filter(mac_address=EUI(mac))[0].identity.split('@')[0]
                if not 'host' in identity:
                    mac_identity[EUI(mac)] = identity
            except IndexError, e:
                pass #print identity, e
        for obj in day_qs:
            coords = time_to_coords(obj.time)
            try:
                day_dict_list[mac_identity[obj.mac_address]].append(coords)
            except KeyError:
                pass
        for mac in day_dict_list:
            day_dict[mac] = sorted(set(day_dict_list[mac]))

        days[day] = day_dict
    return days



day_list = eval(sys.argv[1])

days_dict = mac_coords_dict(DeviceSignalStrength.objects.all())
print "days_dict"


neural_dict_day = {}
for day in days_dict:
    neural_dict = defaultdict(list)
    for mac in days_dict[day]:
        for num in range(1,73):
            if num in days_dict[day][mac]:
                neural_dict[mac].append(1)
            else:
                neural_dict[mac].append(0)
    neural_dict_day[day] = neural_dict


print "neural_dict_day"


role_list = []
for neural_dict in neural_dict_day:
    for identity in neural_dict_day[neural_dict]:
        try:
            if any(char.isdigit() for char in identity):                    
                role_list.append((0,neural_dict_day[neural_dict][identity]))
            else:
                if not 'host' in identity:
                    role_list.append((1,neural_dict_day[neural_dict][identity]))
        except IndexError, e:
            pass #print identity, e


print "role_list: ", len(role_list)

from collections import Counter
import random

teacher_list = [a for a in role_list if a[0] == 1]
student_list = [a for a in role_list if a[0] == 0]

print len(teacher_list)
print len(student_list)

student_list = random.sample(student_list, len(teacher_list))

print len(student_list)

