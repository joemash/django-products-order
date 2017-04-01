from django.db import models
from django.db.models import Count
from django.db.models.signals import post_save,pre_save
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from accounts.models import Customer
from taxes.models import Tax



class ProductManager(models.Manager):
    def create_batch(self,product_items):
        for mydict in product_items:
            Product.objects.create(  name = mydict['product_name'],
                                     short_description = mydict['description'],
                                     price = mydict['price'],
                                     #tax_rate=tax_rate,
                                     #tax_method=tax_method,
                                     )

class CustomerPriceManager(models.Manager):
    def create_batch(self,customer_items,customer):
        for mydict in customer_items:
            #create() method expects to get product_type instance not string
            product_instance = Product.objects.get(name=mydict['product'])
            #select all rows from db that have a duplicate product
            #product_val=CustomerPrice.objects.values('product').annotate(Count('id')).order_by().filter(id__count__gt=1)
            CustomerPrice.objects.create( name = customer,
                                          product = product_instance,
                                          price = mydict['price'],
                                          #tax_rate=tax_rate,
                                          #tax_method=tax_method,
                                     )




            #if self.filter(product__name__iexact=product_instance).count() > 0:
                #raise IntegrityError('UNIQUE constraint failed')
            #else:




class Product(models.Model):
    '''Represents a product '''

    name = models.CharField(max_length=100,unique=True)
    slug = models.SlugField(max_length=100,unique=True)
    short_description = models.CharField(max_length=500,blank=True,null=True,
         help_text='Short Description of product')
    description = models.TextField(blank=True,null=True,help_text='Full Description of the product')
    price = models.DecimalField(max_digits=9,decimal_places=2,help_text='Per unit price')
    quantity = models.IntegerField(help_text='Stock quantity',null=True, blank=True)
    tax = models.ForeignKey(
        Tax, null=True, blank=True,  help_text='Tax applied on this product, if tax exempt select none')
    #picture = models.ImageField(null=True, blank=True,upload_to='/uploads/')
    is_active = models.BooleanField(default=True,help_text='Product is available for listing and sale')
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    objects = ProductManager()

    def __str__(self):
        return  self.name

    def save(self,*args,**kwargs):
        #generate the slug only once when you create a new object:
        if not self.slug:
            self.slug = slugify(self.name)
        super(Product,self).save(*args,**kwargs)

    def get_product_image(self):
		img = self.productimage_set.first()
		if img:
			return img.image
		return img

'''
class ProductImage(models.Model):
	product = models.ForeignKey(Product)
	image = models.ImageField(upload_to='uploads/products')

	def __str__(self):
		return self.product.name

	def thumbnail(self):
		return """<a href="/static/%s"><img border="0" alt="" src="/static/%s" height="40" /></a>""" % ((self.image.name, self.image.name))
	thumbnail.allow_tags = True
'''
class CustomerPrice(models.Model):
    name = models.ForeignKey(Customer)
    product = models.ForeignKey(Product)
    price = models.DecimalField(max_digits=9,decimal_places=2)
    quantity = models.IntegerField(help_text='Purchased quantity',default=1)
    short_description = models.CharField(max_length=500,blank=True,null=True,
        help_text='Short Description of product')
    is_active = models.BooleanField(default=True,help_text='Product is available for listing and sale')
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    objects = CustomerPriceManager()

    @classmethod
    def get_active(cls):
        return list(cls.objects.filter(is_active=True))

class About(models.Model):
    text = models.TextField()

class Recipe(models.Model):
    text = models.TextField()
