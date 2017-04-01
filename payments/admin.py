from django.contrib import admin
from .models import Transaction




class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'status','tracking_id','reference')
    list_filter = ('status',)
    search_fields = ('id', 'order',)
    date_hierarchy = 'created_on'

admin.site.register(Transaction, TransactionAdmin)
