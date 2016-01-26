import matplotlib as mpl
mpl.use('PDF')
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
import pickle
from random import shuffle
from pybrain.datasets            import ClassificationDataSet
from pybrain.utilities           import percentError
from pybrain.tools.shortcuts     import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure.modules   import SoftmaxLayer
from pybrain.tools.validation import CrossValidator
from pylab import ion, ioff, figure, draw, contourf, clf, show, hold, plot
from scipy import diag, arange, meshgrid, where
from numpy.random import multivariate_normal
from collections import Counter
import random
import datetime
import numpy as np
SPINE_COLOR = 'black'
import pandas as pd
import matplotlib

from collections import defaultdict
from netaddr import EUI
from netaddr.core import NotRegisteredError

os.environ["DJANGO_SETTINGS_MODULE"] = "probes.settings"
django.setup()


one_metre_rssi = -45
length = 24.1
width = 18.6
path='/srv/media/temp.pdf'


def pythagoras(a,b):
    return sqrt(a**2 + b**2)


def rssi_to_distance(rssi, one_metre_rssi=one_metre_rssi):
    result = 10**((rssi - one_metre_rssi)/-21.0)
    return result


def distance_to_rssi(d, one_metre_rssi=one_metre_rssi):
    return -30 * log10(d) + one_metre_rssi


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
    'HG655D' : -45,
    '710Nr' : -45,
    '710Nm' : -45,
}
max_rssi = {
    'HG655D': distance_to_rssi(pythagoras(14, width), one_metre_rssi=one_metre_rssi['HG655D']),
    '710Nr': distance_to_rssi(pythagoras(length, 11.5), one_metre_rssi=one_metre_rssi['710Nr']),
    '710Nm': distance_to_rssi(pythagoras(17, width), one_metre_rssi=one_metre_rssi['710Nm'])
    }


def trilaterate(distance_dict):
    distance_data = [int(distance_dict[router_id]) for router_id in identifiers]
    point_estimate = basicTrilateration.trilaterate(point_data, distance_data, identifiers)
    return (point_estimate[0], point_estimate[1])


def contains_point(point, a=(0,0), b=(length, width)):
    if (a[0] < point[0] <= b[0] and
         a[1] < point[1] <= b[1]):
         return True
    return False


def generate_locations(qs, one_metre_rssi=one_metre_rssi):
    max_rssi = {
        'HG655D': distance_to_rssi(pythagoras(14, width), one_metre_rssi=one_metre_rssi['HG655D']),
        '710Nr': distance_to_rssi(pythagoras(length, 11.5), one_metre_rssi=one_metre_rssi['710Nr']),
        '710Nm': distance_to_rssi(pythagoras(17, width), one_metre_rssi=one_metre_rssi['710Nm'])
    }

    rssi_list = [
        {
            'HG655D': rssi_to_distance(rss.signal_strength_hg655d, one_metre_rssi=one_metre_rssi['HG655D']),
            '710Nm': rssi_to_distance(rss.signal_strength_710nm, one_metre_rssi=one_metre_rssi['710Nm']),
            '710Nr': rssi_to_distance(rss.signal_strength_710nr, one_metre_rssi=one_metre_rssi['710Nr']),
            }
        for rss in qs #if rss.signal_strength_hg655d  +1 > max_rssi['HG655D'] and rss.signal_strength_710nm  >= max_rssi['710Nm'] and rss.signal_strength_710nr + 1 > max_rssi['710Nr']
        ]

    rssi_list = [dict(t) for t in set([tuple(d.items()) for d in rssi_list])]
    trilaterate_list = [trilaterate(rssi) for rssi in rssi_list]
    xy_list = trilaterate_list
    return xy_list
    #xy_list = [(t.params['x'].value, t.params['y'].value) for t in trilaterate_list]
    #return [x for x, y in xy_list], [y for x, y in xy_list]



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



def generate_rssi_graph():
    fig = plt.figure()
    latexify(columns=1)
    ax = fig.add_subplot(111)
    fig.subplots_adjust(top=0.85)
    ax.set_title('Count vs. signal strength')

    ax.set_xlabel('Signal strength')
    ax.set_ylabel('Count')
    ax = format_axes(ax)

    hg655d_list = list(DeviceSignalStrength.objects.values('signal_strength_hg655d').annotate(the_count=Count('signal_strength_hg655d')))
    nm_list = list(DeviceSignalStrength.objects.values('signal_strength_710nm').annotate(the_count=Count('signal_strength_710nm')))
    nr_list = list(DeviceSignalStrength.objects.values('signal_strength_710nr').annotate(the_count=Count('signal_strength_710nr')))

    hg655d_list.sort(key=lambda tup: tup['signal_strength_hg655d'])
    nm_list.sort(key=lambda tup: tup['signal_strength_710nm'])
    nr_list.sort(key=lambda tup: tup['signal_strength_710nr'])

    xy_list= zip(*[(a['signal_strength_hg655d'], a['the_count']) for a in hg655d_list if a['the_count'] > 1000])
    xy_lists = sorted(xy_list, key=lambda tup: tup[1])
    plt.plot(xy_lists[0], xy_lists[1], 'blue')

    xy_list= zip(*[(a['signal_strength_710nm'], a['the_count']) for a in nm_list if a['the_count'] > 1000])
    xy_lists = sorted(xy_list, key=lambda tup: tup[1])
    plt.plot(xy_lists[0], xy_lists[1], 'green')

    xy_list= zip(*[(a['signal_strength_710nr'], a['the_count']) for a in nr_list if a['the_count'] > 1000])
    xy_lists = sorted(xy_list, key=lambda tup: tup[1])
    plt.plot(xy_lists[0], xy_lists[1], 'red')

    blue_patch = mpatches.Patch(color='blue', label='Router: C / HG655D')
    red_patch = mpatches.Patch(color='red', label='Router: B / 710Nr')
    green_patch = mpatches.Patch(color='green', label='Router: A / 710Nm')

    plt.legend(handles=[green_patch, red_patch, blue_patch])

    plt.show()
    plt.draw()
    plt.savefig(path, dpi=1000)
    return



def unique_addresses_stats():
    qs = DeviceSignalStrength.objects.filter(time__month=12, time__day=9)
    count = qs.values('mac_address').annotate(count=Count('mac_address'))
    d = {}
    for num in [7, 8, 9,10]:
        d[num] = [a for a in Probe.objects.filter(time__month=12, time__day=num).values_list('source_address', flat=True)]


    mac_addresses_in_all = set(d[num])

    for a in d:
        print len(mac_addresses_in_all)
        mac_addresses_in_all = mac_addresses_in_all & set(d[a])

    return mac_addresses_in_all
    

#unique_addresses = unique_addresses_stats()
#addresses_identity = {}

#for a in unique_addresses: 
#    try:
#        obj = DeviceInfo.objects.filter(mac_address=EUI(a))[0]
#        identity = obj.identity
#        print obj
#    except:
#        try:
#            print 'no identity', EUI(a).oui.registration().org
#        except:
#            pass
#    else:
#        if not identity in addresses_identity:
#            addresses_identity[identity] = []
#        addresses_identity[identity].append(a)


#print addresses_identity

#for a in addresses_identity:
#    if not any(char.isdigit() for char in a):
#        print a
#print len(unique_addresses)
#print len(addresses_identity)


#generate_rssi_graph()

#print len(unique_addresses_stats())
#generate_rssi_graph()


def generate_rssi_device_graph(qs):
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

#qs = DeviceSignalStrength.objects.all() #filter(mac_address=EUI('60:FB:42:42:1A:10'))
#filter(time__gt=datetime.datetime(2015, 12, 14, 0, 0, 0)) #.filter(mac_address=EUI('60:FB:42:42:1A:10'))
#print qs.count()


#xy_list = generate_locations(qs)

#heatmap, xedges, yedges = np.histogram2d([x for x, y in xy_list], [y for x, y in xy_list], bins=10)
#extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]

#plt.clf()
#plt.imshow(heatmap, extent=extent)
#plt.ylim(-5,22) 
#plt.xlim(-5,29)
#plt.scatter([x for x, y in xy_list], [y for x, y in xy_list])
#plt.show()
#plt.draw()
#plt.savefig(path)


def time_to_coords(dt):
    return (dt.hour - 5) * 6 + (dt.minute/10) + 1


def filter_cisco(qs, mac_address_key='source_address'):
    mac_addresses = set(qs.values_list(mac_address_key, flat=True))
    is_probe = (qs[0].__class__.__name__ == 'Probe')
    for mac in mac_addresses:
        try:
            if 'cisco' in EUI(mac).oui.registration().org.lower():
                if is_probe:
                    qs = qs.exclude(source_address=EUI(mac))
                else:
                    qs = qs.exclude(mac_address=EUI(mac))
        except NotRegisteredError:
            pass
    print "filtered count: ", qs.count()
    return qs


def mac_coords_dict(qs, day_list, mac_address_key='source_address'):
    qs = filter_cisco(qs, mac_address_key=mac_address_key)
    days = {}

    for day in day_list:
        day_dict_list = defaultdict(list)
        day_dict = {}
        day_qs = qs.filter(time__day=day)
        mac_addresses = day_qs.values_list(mac_address_key, flat=True).distinct()
        
        mac_identity = {obj.mac_address:obj.identity for obj in DeviceInfo.objects.all() if not 'host' in obj.identity.lower()}        
        is_probe = qs[0].__class__.__name__ == 'Probe'
        print 'start', datetime.datetime.now()        
        for obj in day_qs:
            coords = time_to_coords(obj.time)
            if is_probe:
                day_dict_list[obj.source_address].append(coords)
            else:
                day_dict_list[obj.mac_address].append(coords)
        print 'stop', datetime.datetime.now()        
        for mac in day_dict_list:
            day_dict[mac] = sorted(set(day_dict_list[mac]))

        days[day] = day_dict
    for day in days:
        print day, len(days[day])

    return days, mac_identity


def id_coords_dict_to_nn_input(id_coords_dict, nn_input, mac_identity):
    neural_dict = defaultdict(list)
    
    for identity in id_coords_dict:

        for num in range(1,73):
            if num in id_coords_dict[identity]:
                neural_dict[identity].append(1)
            else:
                neural_dict[identity].append(0)
        try:
            if any(char.isdigit() for char in mac_identity[identity]):
                nn_input.append((0, neural_dict[identity]))
            else:
                nn_input.append((1, neural_dict[identity]))
        except KeyError:
            pass


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


#day_list = eval(sys.argv[1])
#qs = Probe.objects.all()
#qs = DeviceSignalStrength.objects.all()
#print "count: ", qs.count()
#is_probe = qs[0].__class__.__name__ == 'Probe'  
#if is_probe: 
#    days_dict, mac_identity = mac_coords_dict(qs, day_list, mac_address_key='source_address')
#else:
#    days_dict, mac_identity = mac_coords_dict(qs, day_list, mac_address_key='mac_address')
#role_list = []
#for day in days_dict:
#    id_coords_dict_to_nn_input(days_dict[day], role_list, mac_identity)


def main(xn,xt,yl,epochs,hidden_neurons):

    f = open('total_list_probe_mac_all.txt', 'rb')
    role_list = pickle.load(f)

    teacher_list = [a for a in role_list if a[0] == 1]
    student_list = [a for a in role_list if a[0] == 0]
    print 'len st: ', len(student_list), 'len te: ', len(teacher_list)
#    print 'is probe?: ', is_probe

    student_list = random.sample(student_list, len(teacher_list))
    total_list = student_list + teacher_list
    shuffle(total_list)

    alldata = ClassificationDataSet(72, 1, nb_classes=2)

    for (o, i) in total_list:
        alldata.addSample(i, o)

    tstdata, trndata = alldata.splitWithProportion(0.25)

    trndata._convertToOneOfMany( )
    tstdata._convertToOneOfMany( )

    print "Number of training patterns: ", len(trndata)
    print "Input and output dimensions: ", trndata.indim, trndata.outdim
    print "First sample (input, target, class):"
    print trndata['input'][0], trndata['target'][0], trndata['class'][0]

    fnn = buildNetwork(trndata.indim, hidden_neurons, trndata.outdim, outclass=SoftmaxLayer)
    trainer = BackpropTrainer( fnn, trndata, momentum=0.1, verbose=True, weightdecay=0.01)

    for i in range(epochs):
        trnresult = percentError( trainer.testOnClassData(),
                     trndata['class'] )
        tstresult = percentError( trainer.testOnClassData(
               dataset=tstdata ), tstdata['class'] )

        trainer.trainEpochs(1)

        xn.append(trnresult)
        xt.append(tstresult)
        yl.append(i)

        print "epoch: %4d" % trainer.totalepochs, \
              "  train error: %5.2f%%" % trnresult, \
              "  test error: %5.2f%%" % tstresult
    
#    f = open('total_list_probe_mac_1Mormore.txt', 'wb')
#    pickle.dump(role_list, f)
if __name__ == "__main__":
    generate_rssi_graph()


if __name__ == "a__main__":
    cd = {10:'b', 20:'g', 30:'r', 40:'c', 50:'m', 60:'y', 70:'k'}
    fig = plt.figure()    
    for a in range(10, 20, 10):
        iterations = 100
        epochs = 21
        hidden_neurons = a
        print 'hidden: ', hidden_neurons
        path='/srv/media/it%d_ep%d_hn%d_probe_all_%s.pdf' % (iterations, epochs, hidden_neurons, datetime.datetime.now().strftime('%H_%M_%d_%m_%y'))    
        results = {}
        for i in range(iterations):
            xn, xt, yl = [], [], []
            main(xn,xt,yl,epochs,hidden_neurons)
            results[i] = (yl, xn, xt)

        xnd = defaultdict(list)
        xtd = defaultdict(list)

        for i in results:
            for n, r in enumerate(results[i][1]):
                xnd[n].append(r)
            for n, r in enumerate(results[i][2]):
                xtd[n].append(r)
    
        xt = [float(sum(xtd[n]))/float(len(xtd[n])) for n in xtd]
        xn = [float(sum(xnd[n]))/float(len(xnd[n])) for n in xnd]

        latexify(columns=1)
        plt.plot(yl, xt, 'g', xn, 'b')
        ax = fig.add_subplot(111)
        fig.subplots_adjust(top=0.85)
        ax.set_title('Error rate vs. iterations')

        ax.set_xlabel('Training iteration')
        ax.set_ylabel('Error percentage')
        ax = format_axes(ax)
        plt.xticks(np.arange(min(yl), max(yl)+1, 1))
        plt.yticks(np.arange(0, 100+1, 10))
        blue_patch = mpatches.Patch(color='blue', label='Training result')
        green_patch = mpatches.Patch(color='green', label='Test data result')

        plt.legend(handles=[blue_patch, green_patch]) #[mpatches.Patch(color=cd[a], label = 'train res. %s neurons in hl' % a) for a in sorted(cd)])
        plt.xlim(0,epochs-1)
        plt.ylim(0,55)
#        plt.tight_layout()
        plt.show()
        plt.draw()
    plt.savefig(path, dpi=1000)
    print path
