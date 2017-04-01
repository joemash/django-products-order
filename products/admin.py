from django.contrib import admin

from .models import Product,CustomerPrice,About,Recipe


class ProductAdmin(admin.ModelAdmin):
	list_display = ('name','description')
	prepopulated_fields = {'slug':('name',)}
'''
class ProductImageAdmin(admin.ModelAdmin):
	list_display = ('product','thumbnail')
'''

class CustomerPriceAdmin(admin.ModelAdmin):
	list_display = ('name','product','price')


class AboutAdmin(admin.ModelAdmin):
	class Media:
		 js=('/static/js/tiny_mce/tiny_mce.js','/static/js/tiny_mce/textarea.js',)

class RecipeAdmin(admin.ModelAdmin):
	class Media:
		 js=('/static/js/tiny_mce/tiny_mce.js','/static/js/tiny_mce/textarea.js',)


admin.site.register(Product,ProductAdmin)
admin.site.register(CustomerPrice,CustomerPriceAdmin)
#admin.site.register(ProductImage,ProductImageAdmin)
admin.site.register(About,AboutAdmin)
admin.site.register(Recipe,RecipeAdmin)
