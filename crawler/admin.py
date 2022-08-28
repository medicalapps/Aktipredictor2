from django.contrib import admin
from crawler.models import *

# Register your models here.

@admin.register(Companies)
class CompaniesAdmin(admin.ModelAdmin):
    pass


@admin.register(CompanyStockDay)
class CompanyStockDayAdmin(admin.ModelAdmin):
    pass


@admin.register(WorldKPI)
class WorldKPIAdmin(admin.ModelAdmin):
    pass

@admin.register(CollectorSettings)
class CollectorSettingsAdmin(admin.ModelAdmin):
    pass
