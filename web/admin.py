from django.contrib import admin
from web.models import Probe, Location, DeviceInfo
# Register your models here.

class ProbeAdmin(admin.ModelAdmin):
    pass


class LocationAdmin(admin.ModelAdmin):
    pass


class DeviceInfoAdmin(admin.ModelAdmin):
    pass


admin.site.register(Probe, ProbeAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(DeviceInfo, DeviceInfoAdmin)
