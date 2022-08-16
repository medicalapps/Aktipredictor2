from django.contrib import admin
from datacollector.models import *

# Register your models here.


@admin.register(Companies)
class CompaniesAdmin(admin.ModelAdmin):
    pass


@admin.register(CompanyStockDay)
class CompanyStockDayAdmin(admin.ModelAdmin):
    pass


@admin.register(CollectorSettings)
class CollectorSettingsAdmin(admin.ModelAdmin):
    pass
