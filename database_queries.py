import os
import datetime

import django
from netaddr import EUI
from netaddr.core import NotRegisteredError

from web.models import Probe, DeviceInfo

os.environ["DJANGO_SETTINGS_MODULE"] = "probes.settings"
django.setup()


def exclude_manufacturers(qs, manufacturers):
    mac_addresses = set(qs.values_list(get_mac_address_key(qs), flat=True))
    for mac in mac_addresses:
        try:
            if EUI(mac).oui.registration().org.lower() in [x.lower() for x in manufacturers]:
                exclude_mac(qs, mac)
        except NotRegisteredError:
            pass
    return qs


def get_mac_address_key(qs):
    if qs[0].__class__.__name__ == 'Probe':
        return "source_address"
    elif qs[0].__class__.__name__ == 'DeviceSignalStrength':
        return "mac_address"
    else:
        return 'Invalid input qs'


def exclude_mac(qs, mac):
    if qs[0].__class__.__name__ == 'Probe':
        qs = qs.exclude(source_address=EUI(mac))
    elif qs[0].__class__.__name__ == 'DeviceSignalStrength':
        qs = qs.exclude(mac_address=EUI(mac))
    else:
        return 'Invalid input qs'
    return qs


def mac_addresses_from_person(identity, qs=DeviceInfo.objects.all()):
    qs = qs.filter(identity=identity)
    return [obj.mac_address for obj in qs]


def probes_from_mac_address(mac_address, qs=Probe.objects.all()):
    qs = qs.filter(source_address=mac_address)
    return qs


def probes_from_person(identity, probe_qs=Probe.objects.all()):
    qs = Probe.objects.none()
    for mac_address in mac_addresses_from_person(identity):
        qs = qs | probe_qs.filter(source_address=mac_address)
    return qs


def filter_triplets(probe_qs):
    qs = Probe.objects.none()
    for mac_address in set(probe_qs.values_list('source_address', flat=True)):
        for time in probe_qs.filter(source_address=EUI(mac_address)).values_list('time', flat=True):
            if probe_qs.filter(time=time, source_address=EUI(mac_address)).count() >= 3:
                qs = qs | probe_qs.filter(time=time)
    return qs


def rssi_triplets_of_qs(mac_address,
                                 from_datetime=datetime.datetime.combine(datetime.date.today(), datetime.time.min),
                                 to_datetime=datetime.datetime.combine(datetime.date.today(), datetime.time.max)):
    qs = Probe.objects.filter(source_address=EUI(mac_address))
    date_range = (from_datetime, to_datetime)
    qs = qs.filter(time__range=date_range)
    qs = filter_triplets(qs)
    return qs


def search_identity(identity, qs=DeviceInfo.objects.all()):
    return list(set(deviceinfo.identity for deviceinfo in qs.filter(identity__icontains=identity)))


"""
def place(qs):
    x, y = [], []

    for time in set(qs.values_list('time', flat=True)):
        d = {probe.router_id: probe.signal_strength for probe in qs.filter(time=time) if probe.signal_strength + 8 >
        max_rssi[probe.router_id]}
        if len(d) >= 3:
            xy = trilaterate(d)
            x.append(xy.params['x'].value)
            y.append(xy.params['y'].value)

    return x, y


def locations_of_mac_address(mac_address, day=time.strftime('%Y-%m-%d')):
    qs = Probe.objects.filter(source_address=EUI(mac_address))

    date_range = (
        datetime.datetime.combine(day, datetime.datetime.min.time()),
        datetime.datetime.combine(day, datetime.datetime.max.time())
        )

    qs = qs.filter(
        time__range=date_range
        )

    x, y = [], []

    for time in set(qs.values_list('time', flat=True)):
        d = {probe.router_id: probe.signal_strength for probe in qs.filter(time=time) if probe.signal_strength + 8 >
        max_rssi[probe.router_id]}
        if len(d) >= 3:
            xy = trilaterate(d)
            x.append(xy.params['x'].value)
            y.append(xy.params['y'].value)

    return x, y
"""