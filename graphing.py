import matplotlib as mpl
mpl.use('pdf')
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
os.environ["DJANGO_SETTINGS_MODULE"] = "probes.settings"
django.setup()


one_metre_rssi = -45
length = 24.1
width = 18.6


def pythagoras(a,b):
    return sqrt(a**2 + b**2)


rssi_to_distance = lambda rssi: 10**((rssi - one_metre_rssi)/-25.0)
distance_to_rssi = lambda d: -10 * 2.5 * log10(d) + one_metre_rssi


point_data = {
    'HG655D': array([14, length, 0]),
    '710Nr': array([0, 11.5, 0]),
    '710Nm': array([17, 0, 0])
     }
identifiers = [
    'HG655D',
    '710Nr',
    '710Nm',
    ]
max_rssi = {
    'HG655D': distance_to_rssi(pythagoras(14, width)), 
    '710Nr': distance_to_rssi(pythagoras(length, 11.5)), 
    '710Nm': distance_to_rssi(pythagoras(17, width))
    }


def trilaterate(distance_dict):
    distance_data = [distance_dict[router_id] for router_id in identifiers]
    point_estimate = basicTrilateration.trilaterateLM(point_data, distance_data, identifiers)
    return point_estimate


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

from test_rssi import latexify, format_axes

def generate_graph(x, y, path='/srv/media/temp.pdf'):
    fig = plt.figure()
    latexify()
    ax = fig.add_subplot(111)
    fig.subplots_adjust(top=0.85)
    ax.set_title('Locaties apparaten in aula')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax = format_axes(ax)
    plt.ylim([0, width])
    plt.xlim([0,length])
    plt.scatter(x, y)
    plt.show()
    plt.draw()
    plt.savefig(path, dpi=1000)

def three_probes_per_second(probe_qs):
    qs = Probe.objects.none()
    for mac_address in set(probe_qs.values_list('source_address', flat=True)):
        for time in probe_qs.filter(source_address=EUI(mac_address)).values_list('time', flat=True):
            if probe_qs.filter(time=time, source_address=EUI(mac_address)).count() >= 3:
                qs = qs | probe_qs.filter(time=time)

    return qs


def search_identity(identity, qs=DeviceInfo.objects.all()):
    return list(set(deviceinfo.identity for deviceinfo in qs.filter(identity__icontains=identity)))


def locations_of_mac_address(mac_address, day=time.strftime('%Y-%m-%d')):
    qs = Probe.objects.filter(source_address=EUI(mac_address))

    date = datetime.datetime.strptime(day, '%Y-%m-%d')
    date_range = (
        datetime.datetime.combine(day, datetime.datetime.min.time()),
        datetime.datetime.combine(day, datetime.datetime.max.time())
        )

    qs = qs.filter(
        time__range=date_range
        )

    x = []
    y = []

    for time in set(qs.values_list('time', flat=True)):
        d = {probe.router_id: probe.signal_strength for probe in qs.filter(time=time) if probe.signal_strength + 8 > max_rssi[probe.router_id]}
        if len(d) >= 3:
            xy = trilaterate(d)
            x.append(xy.params['x'].value)
            y.append(xy.params['y'].value)

    return x, y


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

    x = []
    y = []

    for time in set(qs.values_list('time', flat=True)):
        d = {probe.router_id: rssi_to_distance(probe.signal_strength) for probe in qs.filter(time=time) if probe.signal_strength + 5> max_rssi[probe.router_id]}
        if len(d) >= 3:
            xy = trilaterate(d)
            print xy.params['x'].value, xy.params['y'].value
            x.append(xy.params['x'].value)
            y.append(xy.params['y'].value)
    generate_graph(x,y)


if __name__ == '__main__':
    main()
