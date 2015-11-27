from django.contrib import admin
from web.models import Probe

# Register your models here.

class ProbeAdmin(admin.ModelAdmin):
    pass

admin.site.register(Probe, ProbeAdmin)
