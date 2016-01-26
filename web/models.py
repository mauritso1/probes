from django.db import models
from macaddress.fields import MACAddressField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from trilateration import trilaterate
from numpy import array


class Probe(models.Model):
    time = models.DateTimeField(verbose_name='Timestamp')
    BSSID = MACAddressField(verbose_name='BSSID', integer=False)
    destination_address = MACAddressField(null=True, blank=True, verbose_name='Destination address', integer=False)
    source_address = MACAddressField(verbose_name='Source address', integer=False)
    signal_strength = models.IntegerField(verbose_name='Signal strength', validators=[MinValueValidator(-100), MaxValueValidator(0)])
    frequency =  models.IntegerField(verbose_name='Frequency', validators=[MinValueValidator(2412), MaxValueValidator(2472)])
    router_id = models.CharField(verbose_name='Router name', max_length=15, choices=(
        ('HG655D', 'Huawei HG655D'), 
        ('710Nr', 'TL-WR710N Ramon'), 
        ('710Nm', 'TL-WR710N Maurits'), 
        ('experiaboxv8', 'Experiabox V8'), 
        ('other', 'Other')))


    def __unicode__(self):
        return '%s | SA: %s | Signal strength: %s | %s' % (self.time, self.source_address, self.signal_strength, self.router_id)


    class Meta:
        unique_together = ["time", "source_address", "router_id"]




class Location(models.Model):
    time = models.DateTimeField(verbose_name='Timestamp')
    source_address = MACAddressField(verbose_name='Source address', integer=False)
    x = models.IntegerField(verbose_name='x-coordinate')
    y = models.IntegerField(verbose_name='y-coordinate')
    
    def __unicode__(self):
        return 'Time: %s | SA: %s | x: %s | y: %s' % (self.time, self.source_address, self.x, self.y)


class DeviceSignalStrength(models.Model):
    time = models.DateTimeField(verbose_name='Timestamp')
    mac_address = MACAddressField(verbose_name='Mac address', integer=False)
    signal_strength_hg655d = models.IntegerField(verbose_name='Signal strength', validators=[MinValueValidator(-100), MaxValueValidator(0)]) 
    signal_strength_710nr = models.IntegerField(verbose_name='Signal strength', validators=[MinValueValidator(-100), MaxValueValidator(0)])
    signal_strength_710nm = models.IntegerField(verbose_name='Signal strength', validators=[MinValueValidator(-100), MaxValueValidator(0)])

    def __unicode__(self):
        return 'Time: %s | Mac address: %s | Signal strength (HG655D, 710Nr, 710Nm): (%s, %s, %s) ' % (self.time, self.mac_address, self.signal_strength_hg655d, self.signal_strength_710nr, self.signal_strength_710nm)

    class Meta:
        unique_together = ["time", "mac_address"]



class DeviceInfo(models.Model):
    identity = models.CharField(verbose_name='Identity', max_length=100)
    mac_address = MACAddressField(verbose_name='Mac address', integer=False)


    def __unicode__(self):
        return 'Identity: %s | Mac address: %s' % (self.identity, self.mac_address)


    class Meta:
        unique_together = ["identity", "mac_address"]


def rToD(rssi):
    one_metre_rssi = 1
    path_loss_constant = 2
    distance = 10^((rssi + one_metre_rssi)/-20)
    return distance


#@receiver(post_save, sender=Probe)
def calculate_location(sender, instance, **kwargs):
    point_distance = trilaterate.point_data.copy() 
    distance =  trilaterate.rssiToDistance(-77)
    point_distance['710Nm'] = distance
    qs = Probe.objects.filter(source_address=instance.source_address, time=instance.time)
    if qs.count() > 1:
        print '710Nm', -77, distance
        for probe in qs:
            distance = int(trilaterate.rssiToDistance(probe.signal_strength))
            point_distance[probe.router_id] = distance
            print probe.router_id, probe.signal_strength, distance 
        
        point_estimate = trilaterate.basicTrilateration.trilaterateLM(trilaterate.point_data, point_distance.values(), trilaterate.identifiers)
        location = Location(
            time = instance.time,
            source_address = instance.source_address,
            x = point_estimate.params['x'].value,
            y = point_estimate.params['y'].value,
            )
        print location.x, location.y
        location.save()



