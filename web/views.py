from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django_tables2   import RequestConfig
from web.tables import test
from web.models import Probe, Location
from web.forms import ProbeSearchForm
from eztables.views import DatatablesView
from table.views import FeedDataView
import json
import time
import datetime
import random
from netaddr import EUI

# Create your views here.
cisco_macs = [u'F0-25-72-CA-E4-70', u'F0-25-72-71-78-C0', u'F0-25-72-71-78-C1', u'F0-25-72-CA-F3-B1', u'08-17-35-31-0A-31', u'08-17-35-31-4E-70', u'08-17-35-31-4E-71', u'08-17-35-31-15-E1', u'08-17-35-31-15-E0', u'08-17-35-31-1C-80', u'08-17-35-31-1C-81', u'08-17-35-31-27-91', u'08-17-35-31-38-D1', u'08-17-35-31-38-D0', u'F0-25-72-CA-FE-30', u'F0-25-72-CA-F2-A0', u'F0-25-72-DB-FE-31', u'08-17-35-31-50-20', u'F0-25-72-71-7B-A1', u'F0-25-72-CB-2F-A0', u'F0-25-72-CA-F2-A1', u'08-17-35-31-2F-10', u'F0-25-72-CA-FF-91', u'F0-25-72-CA-FF-90', u'F0-25-72-71-7B-10', u'F0-25-72-CB-2E-C0', u'08-17-35-31-36-30', u'F0-25-72-CA-FD-51', u'08-17-35-31-2D-D0', u'08-17-35-31-2D-D1', u'F0-25-72-CB-2E-C1', u'08-17-35-31-1B-90', u'F0-25-72-CB-2F-A1', u'F0-25-72-CA-F3-71', u'00-02-6F-FA-A2-50', u'00-02-6F-FA-A2-4C', u'00-02-6F-FA-A2-48']

def filter_cisco(qs, mac_addresses=cisco_macs):
    for mac in mac_addresses:
        qs = qs.exclude(source_address=EUI(mac))
    return qs


class ProbeDataView(FeedDataView):
    token = test.token

    def get_queryset(self):
        qs = super(ProbeDataView, self).get_queryset()
        #qs = qs.filter(signal_strength__lt=form.cleaned_data['signal_strength_from'])
        #qs = qs.filter(signal_strength__gt=form.cleaned_data['signal_strength_to'])
        return qs


def probe_data(request):
    if request.method=='POST':
        received_json_data=json.loads(request.body)
        print received_json_data
        return HttpResponse(status=200)
    return HttpResponse(status=400)


def table(request):
#    qs = Probe.objects.all()
#    if request.method == 'POST':
#        form = ProbeSearchForm(request.POST)
#        if form.is_valid():
#            qs = qs.filter(signal_strength__lt=form.cleaned_data['signal_strength_from'])
#            qs = qs.filter(signal_strength__gt=form.cleaned_data['signal_strength_to'])
#            for a in form.cleaned_data:
#                if form.cleaned_data[a] != None and form.cleaned_data[a]!= "" and "signal" not in a and form.cleaned_data[a] != "0":
#                    qs = qs.filter(**{a:form.cleaned_data[a]})
#    else:
#    print qs.count()
    probes = test()
    return render(request, "table2.html", {'probes': probes})


def f7(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if not (x in seen or seen_add(x))]


def get_data(request):
    if request.method == 'GET':
        point_list = []
        
        xdata, ydata = linechart_devices_per_time(calculate_per=600)
        for x, y in zip(xdata, ydata):
            dict =  {'x': x, 'y': y}
            point_list.append(dict.copy())

        js_data = json.dumps(point_list)
    return HttpResponse(js_data)


def scatterchart_device_location():
    ydata = []
    xdata = []
    dict = {}
    qs = Location.objects.all()
    for location in qs[0:5000]:
        if location.x != 0 and location.y != 0:
            dict[location.x] = location.y

    for x, y in dict.items():
        xdata.append(x)
        ydata.append(y)

    return (xdata, ydata)


def linechart_devices_per_time(calculate_per=600, start_date='04-12-15', end_date='04-12-15'):
    start_date = datetime.datetime.strptime(start_date, '%d-%m-%y')
    end_date = datetime.datetime.strptime(end_date, '%d-%m-%y')
    date_range = (
    datetime.datetime.combine(start_date, datetime.datetime.min.time()),
    datetime.datetime.combine(end_date, datetime.datetime.max.time())
    )   

    qs = Probe.objects.all()
    qs = qs.filter(
        time__range=date_range
        )
    qs = filter_cisco(qs)
    
    start_time = qs[0].time
    end_time = qs.order_by('time').reverse()[0].time

    xdata, ydata = [], []

    for second in range(0, int((end_time - start_time).total_seconds()), calculate_per):
          ydata.append(int(qs.filter(time__gt=start_time + datetime.timedelta(seconds=second), time__lt=start_time + datetime.timedelta(seconds=second + calculate_per)).count()))
          xdata.append(int(time.mktime((start_time + datetime.timedelta(seconds=second + (calculate_per/2))).timetuple())) * 1000)
    return (xdata, ydata)    


def probe_graph(request):
    xdata, ydata = linechart_devices_per_time()

    chartdata = {
        'x': xdata,
        'y': ydata,
        'name' : "",

        }
    charttype = "scatterChart"
    chartcontainer = 'linechart_container'
    data = {
        'charttype': charttype,
        'chartdata': chartdata,
        'chartcontainer': chartcontainer,
        'extra': {
            'x_is_date': False,
            'x_axis_format': "",
            'y_axis_format': "",
            'tag_script_js': True,
            'jquery_on_ready': False,
            }
    }
    a = render(request, 'line_chart.html', data)
    return render(request, 'line_chart.html', data)


def probe_graph(request):
    start_time = Probe.objects.all()[0].time
    end_time = Probe.objects.all().order_by('time').reverse()[0].time
    print start_time, end_time
    ydata = []
    xdata = []
    calculate_per = 600 # /\ in seconds
    
    for second in range(0, int((end_time - start_time).total_seconds()), calculate_per):
          ydata.append(int(Probe.objects.filter(time__gt=start_time + datetime.timedelta(seconds=second), time__lt=start_time + datetime.timedelta(seconds=second + calculate_per)).count()))
          xdata.append(int(time.mktime((start_time + datetime.timedelta(seconds=second + (calculate_per/2))).timetuple())) * 1000)

    chartdata = {
        'x': xdata,
        'y': ydata,
        'name' : '# devices/s in %d s' % calculate_per,

        }
    charttype = "lineChart"
    chartcontainer = 'linechart_container'
    data = {
        'charttype': charttype,
        'chartdata': chartdata,
        'chartcontainer': chartcontainer,
        'extra': {
            'x_is_date': True,
            'x_axis_format': "%H:%M:%S",
            'y_axis_format': "",
            'tag_script_js': True,
            'jquery_on_ready': False,
            }
    }
    a = render(request, 'line_chart.html', data)
    return render(request, 'line_chart.html', data)




# =============
def probe_graph_bak(request):
    """
    lineChart page
    """

    qs = Probe.objects.filter(signal_strength=-67).order_by('time')
    print len(qs)
    xdata =  [int(time.mktime(a.time.timetuple()) * 1000) for a in qs]
    ydata = [a.signal_strength for a in qs]
    print len(xdata)
    print len(f7(xdata))

    tooltip_date = "%H:%M:%S"

    chartdata = {
        'x': xdata,
        'y': ydata,
        'name1' : 'test123',
        'name2' : 'test789',
        }
    charttype = "lineChart"
    chartcontainer = 'linechart_container'
    data = {
        'charttype': charttype,
        'chartdata': chartdata,
        'chartcontainer': chartcontainer,
        'extra': {
            'x_is_date': True,
            'x_axis_format': '%H:%M:%S',
            'tag_script_js': True,
            'jquery_on_ready': False,
            }
    }
    return render(request, 'line_chart.html', data)
