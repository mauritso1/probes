import matplotlib as mpl
mpl.use('pdf')
import matplotlib.pyplot as plt
import os
import sys
import django
import netaddr
from database_queries import search_identity, probes_from_person, mac_addresses_from_person, filter_triplets
from web.models import *
from netaddr.core import NotRegisteredError
from web.trilateration.trilaterate import rssi_to_distance, distance_to_rssi, one_metre_rssi, trilaterate
os.environ["DJANGO_SETTINGS_MODULE"] = "probes.settings"
django.setup()


def latexify(fig_width=None, fig_height=None, columns=1):
    """Set up matplotlib's RC params for LaTeX plotting.
    Call this before plotting a figure.

    Parameters
    ----------
    fig_width : float, optional, inches
    fig_height : float,  optional, inches
    columns : {1, 2}
    """

    # code adapted from http://www.scipy.org/Cookbook/Matplotlib/LaTeX_Examples

    # Width and max height in inches for IEEE journals taken from
    # computer.org/cms/Computer.org/Journal%20templates/transactions_art_guide.pdf

    assert(columns in [1,2])

    if fig_width is None:
        fig_width = 3.39 if columns==1 else 6.9 # width in inches

    if fig_height is None:
        golden_mean = (sqrt(5)-1.0)/2.0    # Aesthetic ratio
        fig_height = fig_width*golden_mean # height in inches

    MAX_HEIGHT_INCHES = 8.0
    if fig_height > MAX_HEIGHT_INCHES:
        print("WARNING: fig_height too large:" + fig_height +
              "so will reduce to" + MAX_HEIGHT_INCHES + "inches.")
        fig_height = MAX_HEIGHT_INCHES

    params = {'backend': 'ps',
              'text.latex.preamble': ['\usepackage{gensymb}'],
              'axes.labelsize': 8, # fontsize for x and y labels (was 10)
              'axes.titlesize': 8,
              'text.fontsize': 8, # was 10
              'legend.fontsize': 8, # was 10
              'xtick.labelsize': 8,
              'ytick.labelsize': 8,
              'text.usetex': True,
              'figure.figsize': [fig_width,fig_height],
              'font.family': 'serif'
    }

    matplotlib.rcParams.update(params)


def format_axes(ax):
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)

    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color(SPINE_COLOR)
        ax.spines[spine].set_linewidth(0.5)

    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    for axis in [ax.xaxis, ax.yaxis]:
        axis.set_tick_params(direction='out', color=SPINE_COLOR)
    return ax


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


def generate_rssi_device_graph(qs, path):
    dates = [ss.time for ss in qs]
    sss = [(ss.signal_strength_hg655d, ss.signal_strength_710nr, ss.signal_strength_710nm) for ss in qs]

    blue_patch = mpatches.Patch(color='blue', label='HG655D')
    green_patch = mpatches.Patch(color='green', label='710Nr')
    red_patch = mpatches.Patch(color='red', label='710Nm')
    plt.legend(handles=[blue_patch, red_patch, green_patch])

    plt.plot_date(dates, sss)
    plt.show()
    plt.draw()
    plt.savefig(path)


def generate_rssi_graph(path, qs=DeviceSignalStrength.objects.all()):
    fig = plt.figure()
    latexify(columns=1)
    ax = fig.add_subplot(111)
    fig.subplots_adjust(top=0.85)
    ax.set_title('Count vs. signal strength')
    ax.set_xlabel('Signal strength')
    ax.set_ylabel('Count')
    format_axes(ax)

    keys = {'signal_strength_hg655d': 'blue', 'signal_strength_710nm': 'green', 'signal_strength_710nr': 'red'}
    for key in keys:
        l = list(qs.objects.values(key).annotate(the_count=Count(keys)))
        l.sort(key=lambda tup: tup[key])
        xy_list = zip(*[(signal_strength['signal_strength_hg655d'], signal_strength['the_count'])
                        for signal_strength in l if signal_strength['the_count'] > 1000])
        xy_lists = sorted(xy_list, key=lambda tup: tup[1])
        plt.plot(xy_lists[0], xy_lists[1], keys[key])

    blue_patch = mpatches.Patch(color='blue', label='Router: C / HG655D')
    red_patch = mpatches.Patch(color='red', label='Router: B / 710Nr')
    green_patch = mpatches.Patch(color='green', label='Router: A / 710Nm')
    plt.legend(handles=[green_patch, red_patch, blue_patch])

    plt.show()
    plt.draw()
    plt.savefig(path, dpi=1000)
    return


def generate_locations(qs, one_metre_rssi=one_metre_rssi):
    max_rssi = {
        'HG655D': distance_to_rssi(pythagoras(14, width)),
        '710Nr': distance_to_rssi(pythagoras(length, 11.5)),
        '710Nm': distance_to_rssi(pythagoras(17, width))
    }
    rssi_list = [
            {
                'HG655D': rssi_to_distance(rss.signal_strength_hg655d),
                '710Nm': rssi_to_distance(rss.signal_strength_710nm),
                '710Nr': rssi_to_distance(rss.signal_strength_710nr),
            }
        for rss in qs if rss.signal_strength_hg655d  +1 > max_rssi['HG655D'] and rss.signal_strength_710nm  >= max_rssi['710Nm'] and rss.signal_strength_710nr + 1 > max_rssi['710Nr']
        ]
    rssi_list = [dict(t) for t in set([tuple(d.items()) for d in rssi_list])]
    trilaterate_list = [trilaterate(rssi) for rssi in rssi_list]
    xy_list = trilaterate_list
    return xy_list


def contains_point(point, a=(0,0), b=(length, width)):
    if (a[0] < point[0] <= b[0] and
         a[1] < point[1] <= b[1]):
         return True
    return False


def location_statistics(one_metre_rssi=one_metre_rssi):
    x_list, y_list = generate_locations(one_metre_rssi)
    xy_list = zip(x_list, y_list)
    xy_in_rectangle = 0
    for xy in xy_list:
        if contains_point(xy):
            xy_in_rectangle += 1
    total_points = len(xy_list)
    result = (one_metre_rssi, total_points, xy_in_rectangle, float(xy_in_rectangle) / float(total_points) * 100)
    return result


def try_one_metre_rssi():
    results = []
    for i in range(-76, -31, 5):
        for n in range(-76, -31, 5):
            for c in range(-76, -31, 5):
                one_metre_rssi = {
                   'HG655D' : i,
                   '710Nr' : n,
                   '710Nm' : c,
                   }
                results.append(generate_locations(one_metre_rssi))
                print time.strftime("%H:%M:%S"), results[-1]
    return results


def unique_addresses_stats():
    qs = DeviceSignalStrength.objects.filter(time__month=12, time__day=9)
    count = qs.values('mac_address').annotate(count=Count('mac_address'))
    d = {}
    for num in [7, 8, 9,10]:
        d[num] = [a for a in Probe.objects.filter(time__month=12, time__day=num).values_list('source_address', flat=True)]


    mac_addresses_in_all = set(d[num])

    for a in d:
        mac_addresses_in_all = mac_addresses_in_all & set(d[a])

    return mac_addresses_in_all


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
