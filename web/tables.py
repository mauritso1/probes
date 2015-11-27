#import django_tables2 as tables
from models import Probe
from table import Table
from table.columns import Column, DatetimeColumn
from django.core.urlresolvers import reverse_lazy

#class ProbeTable(tables.Table):
#    class Meta:
#        model = Probe
#        attrs = {"class": "table table-striped table-hover"}


class test(Table):
    time = DatetimeColumn(field='time', header='Timestamp')
    BSSID = Column(field='BSSID', header='BSSID')
    source_address = Column(field='source_address', header='Source address')
    signal_strength = Column(field='signal_strength', header='Signal strength')
#    frequency = Column(field='frequency', header='Frequency')
    class Meta:
        model = Probe
        ajax = True
        ajax_source = reverse_lazy('table_data')
