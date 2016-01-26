import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "probes.settings")

from django_mysqlpool import auto_close_db
from django.db.utils import IntegrityError
from web.models import *


@auto_close_db
def save_probes(probe_list):
    try:
        DeviceSignalStrength.objects.bulk_create(probe_list)
    except (IntegrityError), e:
        print e
        save_probes_singles(probe_list)
    return True


def save_probes_singles(probe_list):
    try:
        probe_list[-1].save()
    except (IntegrityError), e:
        print "last", e
        return
    for probe in probe_list:
        try:
            probe.save()
        except (IntegrityError), e:
            print e
    return True


time_mac_dict = {}
for time in Probe.objects.values_list('time', flat=True).distinct():
    time_qs = Probe.objects.filter(time=time).iterator()
    time_mac_dict[time] = time_qs

print "got time_mac_dict"

dss_list = []
time_mac_dict_iter_items = time_mac_dict.iteritems()

for time_key, time_qs in time_mac_dict_iter_items:
    time_dict = {}
    for entry in time_qs:
        if entry.source_address not in time_dict:
            time_dict[entry.source_address] = {}
        time_dict[entry.source_address][entry.router_id] = entry.signal_strength
    time_dict_iter_items = time_dict.iteritems()
    for mac, rssi_dict in time_dict_iter_items:
        if len(rssi_dict) == 3:
            dss = DeviceSignalStrength(
                time = time_key,
                mac_address = mac,
                signal_strength_hg655d=rssi_dict['HG655D'],
                signal_strength_710nr=rssi_dict['710Nr'],
                signal_strength_710nm=rssi_dict['710Nm'],
                )
            dss_list.append(dss)
            if len(dss_list) > 2000:
                print save_probes(dss_list)
                dss_list = []

print save_probes(dss_list)
