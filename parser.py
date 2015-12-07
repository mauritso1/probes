import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "probes.settings")
from collections import defaultdict
import sys
import time
import datetime
import Queue
import threading
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from multiprocessing import Process
from web.models import Probe
from django_mysqlpool import auto_close_db


print "argv[1] HG655D, 710Nr, 710Nm"
router_id = sys.argv[1]
current_time = '00:00:00'
probe_list = []
third_dict = {}
line_dict = {
    0 : 'date',
    1 : 'time',
    6 : 'freq',
    9 : 'rssi',
    14 : 'bssid',
    15 : 'da',
    16 : 'sa',
    }


@auto_close_db
def save_probes(probe_list):
    try:
    #    Probe.objects.bulk_create(probe_list)
        for probe in probe_list:
            probe.save()
        return True
    except (IntegrityError), e:
        print e
        return False


for line in sys.stdin:
    lines = line.split()
    probe_dict = {}
    try:
        if lines[16]:
            for key, value in line_dict.items():
                probe_dict[value] = lines[key]

            if len(probe_dict['sa']) == 20 and len(probe_dict['bssid']) == 23 and probe_dict['rssi'] and 'SA:' in probe_dict['sa'] and probe_dict['freq'] != '1.0':
                try:
                    probe_time = probe_dict['time'][0:8]
                    probe_rssi = probe_dict['rssi'][0:3]
                    if probe_time == current_time:
                        if probe_dict['sa'] not in third_dict:
                            third_dict[probe_dict['sa']] = {'rssi_list': [], 'bssid' : probe_dict['bssid'], 'freq': probe_dict['freq']}
                        try:
                            third_dict[probe_dict['sa']]['rssi_list'].append(int(probe_rssi))
                        except:
                            print "woah"
                            print third_dict
                    else:
                        if len(third_dict) != 0:
                            for key, value in third_dict.iteritems():
                                timestamp = datetime.datetime.strptime(probe_dict['date'] + ' ' + current_time, "%Y-%m-%d %H:%M:%S")
#                                print probe_dict['bssid'][-17:], probe_dict['sa'][-17:], timestamp, sum(value)/len(value), probe_dict['freq'], router_id
                                if len(value['rssi_list']) != 0:
                                    probe = Probe(
                                        time = timestamp,
                                        BSSID = value['bssid'][-17:],
                                        source_address = key[-17:],
                                        signal_strength = sum(value['rssi_list'])/len(value['rssi_list']),
                                        frequency = value['freq'],
                                        router_id = router_id
                                    )
                                    probe_list.append(probe)
                                else: print "WOAH"
                        if len(probe_list) >= 1000:
                            success = save_probes(probe_list)
                            print success
                            probe_list = []
                        
                        current_time = probe_time
                        third_dict = {}
                        third_dict[probe_dict['sa']] = {'rssi_list': [], 'bssid' : probe_dict['bssid'], 'freq': probe_dict['freq']}
                        third_dict[probe_dict['sa']]['rssi_list'].append(int(probe_rssi))
                     
                except IndexError, e:
                    print e
    except IndexError:
        pass


success = save_probes(probe_list)
print "Last few probes: ", success



#    print 'time: ', a['time'][0:8], 'rssi: ', a['rssi'][0:3]

#for a in probes_list:
#    if a['sa'] == 'SA:04:f7:e4:4d:ff:7c':
#        #time = time.mktime(datetime.datetime.strptime(a['date'] + ' ' + a['time'], "%Y-%m-%d %H:%M:%S.%f").timetuple())
#        timestamp = datetime.datetime.strptime(a['date'] + ' ' + a['time'], "%Y-%m-%d %H:%M:%S.%f")
#        timestamp = unix_time_millis(timestamp)
#        print a['rssi'][0:3]

