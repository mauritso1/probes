import sys
import time
import datetime


epoch = datetime.datetime.utcfromtimestamp(0)

def unix_time_millis(dt):
    return (dt - epoch).total_seconds()

lines_list = []
probes_list = []

line_dict = {
    0 : 'date',
    1 : 'time',
    6 : 'freq',
    9 : 'rssi',
    14 : 'mac1',
    15 : 'mac2',
    16 : 'mac3',
    }


for line in sys.stdin:
    lines_list.append(line.split())


for line in lines_list:
    probe_dict = {}
    try:
        if line[16]:
            for key, value in line_dict.items():
                probe_dict[value] = line[key]
            probes_list.append(probe_dict)
    except IndexError:
        pass

for a in probes_list:
    if a['mac3'] == 'SA:04:f7:e4:4d:ff:7c':
        #time = time.mktime(datetime.datetime.strptime(a['date'] + ' ' + a['time'], "%Y-%m-%d %H:%M:%S.%f").timetuple())
        timestamp = datetime.datetime.strptime(a['date'] + ' ' + a['time'], "%Y-%m-%d %H:%M:%S.%f")
        timestamp = unix_time_millis(timestamp)
        print a['rssi'][0:3]

