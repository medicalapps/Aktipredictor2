from django.contrib import admin

# Register your models here.
from net.models import *

# Register your models here.

@admin.register(Network)
class NetworkAdmin(admin.ModelAdmin):
    pass

