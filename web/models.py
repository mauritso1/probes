from django.db import models
from macaddress.fields import MACAddressField
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


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
        return '%s | SA: %s | SS: %s | %sMhz | %s' % (self.time, self.source_address, self.signal_strength, self.frequency, self.router_id)


    class Meta:
        unique_together = ["time", "source_address"]

