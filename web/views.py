from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django_tables2   import RequestConfig
from web.tables import test
from web.models import Probe
from web.forms import ProbeSearchForm
from eztables.views import DatatablesView
from table.views import FeedDataView
import json
import time
import datetime
import random


# Create your views here.


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


def probe_graph(request):
    """
    lineChart page
    """
    
    qs = Probe.objects.filter(source_address="04:F7:E4:4D:FF:7C").order_by('time')
    print len(qs)
    xdata =  [int(time.mktime(a.time.timetuple()) * 1000) for a in qs]
    ydata = [a.signal_strength for a in qs]
    print len(xdata)
    print len(f7(xdata))

    tooltip_date = "%H:%M:%S"

    chartdata = {
        'x': xdata,
        'y1': ydata,
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
