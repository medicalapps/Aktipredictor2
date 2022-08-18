from django.contrib import admin
from network.models import *

# Register your models here.


@admin.register(NetworkSettings)
class NetworkSettingsAdmin(admin.ModelAdmin):
    pass
