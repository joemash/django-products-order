from django.contrib import admin
from .models import Tax

class TaxAdmin(admin.ModelAdmin):
    list_display = ('name', 'method', 'rate',)
    list_filter = ('method', 'created_on',)
    search_fields = ('name',)
    date_hierarchy = 'created_on'

admin.site.register(Tax, TaxAdmin)
