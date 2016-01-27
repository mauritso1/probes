import matplotlib as mpl
mpl.use('PDF')
import matplotlib.pyplot as plt
import os
import django
from web.models import *
import matplotlib.patches as mpatches
import pickle
from random import shuffle
from pybrain.datasets            import ClassificationDataSet
from pybrain.utilities           import percentError
from pybrain.tools.shortcuts     import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure.modules   import SoftmaxLayer
import random
import datetime
import numpy as np
SPINE_COLOR = 'black'
from database_queries import exclude_manufacturers
from graphing import latexify, format_axes, generate_rssi_graph

from collections import defaultdict

os.environ["DJANGO_SETTINGS_MODULE"] = "probes.settings"
django.setup()


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


def mac_coords_dict(qs, day_list, mac_address_key='source_address'):
    qs = exclude_manufacturers(qs, ['cisco'])
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

def setup_neural_network_performance_graph():
    cd = {10:'b', 20:'g', 30:'r', 40:'c', 50:'m', 60:'y', 70:'k'}
    fig = plt.figure()
    latexify(columns=1)
    ax = fig.add_subplot(111)
    fig.subplots_adjust(top=0.85)
    ax.set_title('Error rate vs. iterations')
    ax.set_xlabel('Training iteration')
    ax.set_ylabel('Error percentage')
    format_axes(ax)
    blue_patch = mpatches.Patch(color='blue', label='Training result')
    green_patch = mpatches.Patch(color='green', label='Test data result')
    plt.legend(handles=[blue_patch, green_patch]) #[mpatches.Patch(color=cd[a], label = 'train res. %s neurons in hl' % a) for a in sorted(cd)])
    plt.xlim(0,epochs-1)
    plt.ylim(0,55)


def run_neural_network(xn, xt, yl, epochs, hidden_neurons):

    f = open('total_list_probe_mac_all.txt', 'rb')
    role_list = pickle.load(f)

    teacher_list = [a for a in role_list if a[0] == 1]
    student_list = [a for a in role_list if a[0] == 0]
    print 'len st: ', len(student_list), 'len te: ', len(teacher_list)

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


def generate_neural_network_data(iterations, epochs, hidden_neurons):
    results = {}

    for i in range(iterations):
        xn, xt, yl = [], [], []
        run_neural_network(xn, xt, yl, epochs, hidden_neurons)
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
    return (xn, xt, yl)


def generate_neural_network_graph(path, iterations, epochs, hidden_neurons):
    setup_neural_network_performance_graph()
    xn, xt, yl = generate_neural_network_data(5, 10, 10)
    plt.xticks(np.arange(min(yl), max(yl)+1, 1))
    plt.yticks(np.arange(0, 100+1, 10))
    plt.plot(yl, xt, 'g', xn, 'b')
    plt.show()
    plt.draw()
    plt.savefig(path, dpi=1000)


if __name__ == "__main__":
    iterations = 10
    epochs = 10
    hidden_neurons = 10
    path='/srv/media/it%d_ep%d_hn%d_probe_all_%s.pdf' % (
        iterations,
        epochs,
        hidden_neurons,
        datetime.datetime.now().strftime('%H_%M_%d_%m_%y')
    )
    generate_neural_network_graph(path, iterations, epochs, hidden_neurons)

if __name__ == "__main__":
    generate_rssi_graph()