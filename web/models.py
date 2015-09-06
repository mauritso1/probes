from django.db import models
from macaddress.fields import MACAddressField
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Probe(models.Model):
    mac_address = MACAddressField(null=True, blank=True, verbose_name='Mac address')
    signal_strength = models.IntegerField(verbose_name='Signal strength', validators=[MinValueValidator(-100), MaxValueValidator(0)])
    channel = models.IntegerField(verbose_name='Channel', validators=[MinValueValidator(1), MaxValueValidator(12)])
    time = models.DateTimeField(verbose_name='Timestamp')
