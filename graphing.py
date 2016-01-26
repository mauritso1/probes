import matplotlib as mpl
mpl.use('pdf')
import matplotlib.pyplot as plt
import os
import sys
import django
import netaddr
from database_queries import search_identity, probes_from_person, mac_addresses_from_person, filter_triplets
from test_rssi import latexify, format_axes
from web.models import *
from web.trilateration import trilaterate
from netaddr.core import NotRegisteredError
os.environ["DJANGO_SETTINGS_MODULE"] = "probes.settings"
django.setup()


def generate_graph(x, y, path='/srv/media/temp.pdf'):
    fig = plt.figure()
    latexify()
    ax = fig.add_subplot(111)
    fig.subplots_adjust(top=0.85)
    ax.set_title('Locaties apparaten in aula')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    format_axes(ax)
    plt.ylim([0, trilaterate.width])
    plt.xlim([0, trilaterate.length])
    plt.scatter(x, y)
    plt.show()
    plt.draw()
    plt.savefig(path, dpi=1000)
    return


def main():
    if DeviceInfo.objects.filter(identity=sys.argv[1]).count() is 0:
        print "No person with that name found in the db, but here are the results of a search operation:"
        for identity in search_identity(identity=sys.argv[1]):
            print identity

    qs = probes_from_person(sys.argv[1])
    qs = filter_triplets(qs)
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
        d = {probe.router_id: trilaterate.rssi_to_distance(probe.signal_strength) for probe in qs.filter(time=time)
             if probe.signal_strength + 5 > trilaterate.max_rssi[probe.router_id]}
        if len(d) >= 3:
            xy = trilaterate.trilaterate(d)
            print xy.params['x'].value, xy.params['y'].value
            x.append(xy.params['x'].value)
            y.append(xy.params['y'].value)
    generate_graph(x, y)


if __name__ == '__main__':
    main()
