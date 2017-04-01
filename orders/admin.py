from django.contrib import admin
from .models import Order,OrderItem,PaymentMethod

class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ('order_number','receipt_code',)
    list_display = ('order_number', 'customer','taxes', 'total',
                    'payment_method','payment_status', 'allocate_order','delivery_date')
    list_filter = ('order_number', 'created_on',)
    search_fields = ('order_number', 'customer__username', 'customer__first_name',)
    date_hierarchy = 'created_on'

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product','price','quantity','sub_total', 'taxes',)
    list_filter = ('created_on',)
    search_fields = ('product',)
    date_hierarchy = 'created_on'

class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name','code', 'is_active',)
    list_filter = ('is_active',)
    search_fields = ('name',)
    date_hierarchy = 'created_on'


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(PaymentMethod,PaymentMethodAdmin)
