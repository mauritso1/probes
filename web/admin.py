from django.contrib import admin
from web.models import Probe, Location, DeviceInfo, DeviceSignalStrength

# Register your models here.

class ProbeAdmin(admin.ModelAdmin):
    pass


class LocationAdmin(admin.ModelAdmin):
    pass


class DeviceInfoAdmin(admin.ModelAdmin):
    pass

class DeviceSignalStrengthAdmin(admin.ModelAdmin):
    pass


admin.site.register(Probe, ProbeAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(DeviceInfo, DeviceInfoAdmin)
admin.site.register(DeviceSignalStrength, DeviceSignalStrengthAdmin)

