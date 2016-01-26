import os
import sys
import math
import time
import django
import netaddr
from math import sqrt, log10
from numpy import array
from netaddr import EUI
from models import *
from trilateration import basicTrilateration
os.environ["DJANGO_SETTINGS_MODULE"] = "probes.settings"
django.setup()


one_metre_rssi = -35
length = 24.1
width = 18.6


from views import filter_cisco, cisco_macs


def filter_cisco(qs, mac_addresses=cisco_macs):
    for mac in mac_addresses:
        qs = qs.exclude(mac_address=EUI(mac))
    return qs



def pythagoras(a,b):
    return sqrt(a**2 + b**2)


#def rssi_to_distance(rssi, one_metre_rssi=one_metre_rssi): 
#    result = 10**((rssi - one_metre_rssi)/-20.0)
#    print 'one_metre_rssi: ', one_metre_rssi, 'rssi: ', rssi, 'distance: ', result
#    return result


def rssi_to_distance(rssi, one_metre_rssi=one_metre_rssi):
    result = 10**((rssi - one_metre_rssi)/-25.0)
    print 'one_metre_rssi: ', one_metre_rssi, 'rssi: ', rssi, 'distance: ', result
    return result


def distance_to_rssi(d, one_metre_rssi=one_metre_rssi):
    return -25 * log10(d) + one_metre_rssi


def distance_to_rssi(d, one_metre_rssi=one_metre_rssi):
    return -25 * log10(d) + one_metre_rssi


point_data = {
    'HG655D': array([14, width, 0]),
    '710Nr': array([0, 11.5, 0]),
    '710Nm': array([17, 0, 0])
     }
identifiers = [
    'HG655D',
    '710Nr',
    '710Nm',
    ]
one_metre_rssi = {
    'HG655D' : -70,
    '710Nr' : -70,
    '710Nm' : -70,
}
max_rssi = {
    'HG655D': distance_to_rssi(pythagoras(14, width), one_metre_rssi=one_metre_rssi['HG655D']), 
    '710Nr': distance_to_rssi(pythagoras(length, 11.5), one_metre_rssi=one_metre_rssi['710Nr']), 
    '710Nm': distance_to_rssi(pythagoras(17, width), one_metre_rssi=one_metre_rssi['710Nm'])
    }


def trilaterate(distance_dict):
    distance_data = [int(distance_dict[router_id]) for router_id in identifiers]
    point_estimate = basicTrilateration.trilaterate(point_data, distance_data, identifiers)
    #print distance_data, int(point_estimate.params['x'].value), int(point_estimate.params['y'].value)
    print distance_data, (point_estimate[0], point_estimate[1])
    return (point_estimate[0], point_estimate[1])


def mac_addresses_from_person(identity, qs=DeviceInfo.objects.all()):
    qs = qs.filter(identity=identity)
    return [object.mac_address for object in qs]


def probes_from_mac_address(mac_address, qs=Probe.objects.all()):
    qs = qs.filter(source_address=mac_address)
    return qs


def probes_from_person(identity, probe_qs=Probe.objects.all()):
    qs = Probe.objects.none()
    for mac_address in mac_addresses_from_person(identity):
        qs = qs | probe_qs.filter(source_address=mac_address)
    return qs


def generate_graph(x, y, path='/srv/media/temp.png'):
    graph = plt.scatter(x, y)
    plt.ylim([-width, 2*width])
    plt.xlim([-length, 2*length])
    plt.show()
    plt.draw()
    plt.savefig(path)


def three_probes_per_second(probe_qs):
    qs = Probe.objects.none()
    for mac_address in set(probe_qs.values_list('source_address', flat=True)):
        for time in probe_qs.filter(source_address=EUI(mac_address)).values_list('time', flat=True):
            if probe_qs.filter(time=time, source_address=EUI(mac_address)).count() >= 3:
                qs = qs | probe_qs.filter(time=time)

    return qs


def search_identity(identity, qs=DeviceInfo.objects.all()):
    return list(set(deviceinfo.identity for deviceinfo in qs.filter(identity__icontains=identity)))


import time
import datetime


def locations_of_identity(identity):
#    date = datetime.datetime.strptime(day, '%Y-%m-%d')
#    date_range = (
#        datetime.datetime.combine(date, datetime.datetime.min.time()),
#        datetime.datetime.combine(date, datetime.datetime.max.time())
#        )
    #qs = Probe.objects.all()
 #   qs = Probe.objects.filter(
  #      time__range=date_range
  #      )

    #qs = probes_from_person(identity, probe_qs=qs)
    #print xy.params['x'].value, xy.params['y'].value
    #xy_list.append((xy.params['x'].value, xy.params['y'].value))
    qs = DeviceSignalStrength.objects.all()[0:100000]
    #oqs = filter_cisco(qs)
    rssi_list = [
        {
            'HG655D': rssi_to_distance(rss.signal_strength_hg655d, one_metre_rssi=one_metre_rssi['HG655D']), 
            '710Nm': rssi_to_distance(rss.signal_strength_710nm, one_metre_rssi=one_metre_rssi['710Nm']), 
            '710Nr': rssi_to_distance(rss.signal_strength_710nr, one_metre_rssi=one_metre_rssi['710Nr']),
            } 
        for rss in qs #if rss.signal_strength_hg655d + 1 > max_rssi['HG655D'] and rss.signal_strength_710nm  >= max_rssi['710Nm'] and rss.signal_strength_710nr + 1 > max_rssi['710Nr'] 
        ]
    print max_rssi
    print len(rssi_list)
    rssi_list = [dict(t) for t in set([tuple(d.items()) for d in rssi_list])]

    trilaterate_list = [trilaterate(rssi) for rssi in rssi_list]

    #xy_list = [(t.params['x'].value, t.params['y'].value) for t in trilaterate_list]
    
    xy_list = trilaterate_list
    print len(rssi_list)
    return [x for x, y in xy_list], [y for x, y in xy_list]


def main():
    if DeviceInfo.objects.filter(identity=sys.argv[1]).count() == 0:
        print "No person with that name found in the db, but here are the results of a search operation:"
        for identity in search_identity(identity=sys.argv[1]):
            print identity

    qs = probes_from_person(sys.argv[1])
    qs = three_probes_per_second(qs)
    print qs.count()
    macs = mac_addresses_from_person(sys.argv[1])
    for mac in macs: 
        try:
            print mac,  ' | ', mac.oui.registration().org
        except netaddr.core.NotRegisteredError:
            print 'not registered'

    qs = qs.order_by('time')
    xy_list = []
    rssi_list = []
    for time in set(qs.values_list('time', flat=True)):
        d = {probe.router_id: probe.signal_strength for probe in qs.filter(time=time) if probe.signal_strength > max_rssi[probe.router_id]}
        if len(d) >= 3:
            rssi_list.append((rssi_to_distance(a.signal_strength, one_metre_rssi[a.router_id]) for a in d))
    
    print xy.params['x'].value, xy.params['y'].value
    xy_list.append((xy.params['x'].value, xy.params['y'].value))
    print len(rssi_list)
    rssi_list = list(set(rssi_list))
    print len(rssi_list)
    x = [x for x, y in xy_list]
    y = [y for x, y in xy_list]

    generate_graph(x,y)


if __name__ == '__main__':
    main()
