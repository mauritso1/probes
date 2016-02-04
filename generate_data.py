import matplotlib as mpl
mpl.use('Agg')
import sys
import random
from web.models import *
from collections import defaultdict
from netaddr import EUI
from test_rssi import time_to_coords
from database_queries import exclude_manufacturers


def mac_coords_dict(qs, day_list):
    qs = exclude_manufacturers(qs, ['cisco'])
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
            except IndexError:
                pass
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


def main():
    day_list = eval(sys.argv[1])
    days_dict = mac_coords_dict(DeviceSignalStrength.objects.all(), day_list)
    neural_dict_day = {}

    for day in days_dict:
        neural_dict = defaultdict(list)
        for mac in days_dict[day]:
            for num in range(1, 73):
                if num in days_dict[day][mac]:
                    neural_dict[mac].append(1)
                else:
                    neural_dict[mac].append(0)
        neural_dict_day[day] = neural_dict
    role_list = []

    for neural_dict in neural_dict_day:
        for identity in neural_dict_day[neural_dict]:
            try:
                if any(char.isdigit() for char in identity):
                    role_list.append((0, neural_dict_day[neural_dict][identity]))
                else:
                    if not 'host' in identity:
                        role_list.append((1, neural_dict_day[neural_dict][identity]))
            except IndexError:
                pass

    print "role_list: ", len(role_list)
    teacher_list = [a for a in role_list if a[0] == 1]
    student_list = [a for a in role_list if a[0] == 0]
    print len(teacher_list)
    print len(student_list)

    f = open(sys.argv[2], 'wb')
    pickle.dump(role_list, f)


if __name__ == '__main__':
    try:
        if sys.argv[1]:
           print "parsing data for days %s" % str(sys.argv[1]) 
        if sys.argv[2]:
           print "saving parsed data as %s" 5 str(sys.argv[2])
    except:
        print "Usage: python generate_data.py [<day_list>] <filename>"
        print "For example: python generate_data.py [1,2,3,4] 4days.txt"

    main()
