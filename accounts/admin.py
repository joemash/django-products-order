from django.contrib import admin

from django.contrib import admin
from django.contrib.auth.models import Group
from accounts.models import Customer
from django.contrib.auth.admin import UserAdmin
from accounts.forms import UserChangeForm,UserCreationForm

class CustomerAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    list_display = ('email','first_name','last_name','is_verified')
    list_filter = ('first_name',)

    fieldsets = (
        ('Credentials',{'fields':('email','password')}),
        ('Personal Information',{'fields':('first_name','last_name')}),
        ('Permissions',{'fields':('is_active','is_admin','is_staff','is_verified')}),

    )

    ordering = ('email',)
    search_fields=('email',)


class AddressAdmin(admin.ModelAdmin):
    list_display = ('contact_person', 'company', 'address1', 'city',)
    list_filter = ('city','created_on',)
    search_fields = ('address1', 'address2',)
    date_hierarchy = 'created_on'

admin.site.register(Customer,CustomerAdmin)
#admin.site.register(Address, AddressAdmin)
admin.site.unregister(Group)
