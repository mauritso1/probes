import django_tables2 as tables
from models import Probe


class ProbeTable(tables.Table):
    class Meta:
        model = Probe
        attrs = {"class": "paleblue"}