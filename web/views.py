from django.shortcuts import render
from django.http import HttpResponse
from django_tables2   import RequestConfig
from web.tables import ProbeTable
from web.models import Probe
import json
# Create your views here.

def probe_data(request):
    if request.method=='POST':
        received_json_data=json.loads(request.body)
        print received_json_data
        return HttpResponse(status=200)
    return HttpResponse(status=400)


def probe_table(request):
    probe_table = ProbeTable(Probe.objects.all())
    RequestConfig(request).configure(probe_table)
    return render(request, "table.html", {"table": probe_table})