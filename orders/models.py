import string, random, datetime,locale
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
from django.db import models
from django.db.models.signals import pre_save
from django.utils.crypto import get_random_string
from django.template import Context
from accounts.models import Customer
from products.models import Product,CustomerPrice
from taxes.models import Tax




class PaymentMethod(models.Model):

    """
    Represents payment methods for order
    """
    # Payment methods

    ONLINE = 'ON'
    PURCHASE_ORDER = 'PO'
    ALL = (
           (ONLINE, 'Online'),
           (PURCHASE_ORDER, 'Purchase Order'))
    ALL_METHODS = dict(ALL)

    code = models.CharField(primary_key=True, max_length=2, choices=ALL)
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    updated_by = models.CharField(max_length=100)
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100)

    class Meta:
        db_table = 'sales_payment_method'
        verbose_name_plural = 'Payment Methods'

    def __str__(self):
        return '%s: %s' % (self.code, self.name)


class OrderManager(models.Manager):
    locale.setlocale(locale.LC_ALL, '')

    def place(self,payment_method,payment_status,
              order_number,total,lineitems,order_status,customer,delivery_date):

        #billing_address = Address.objects.get(customer=customer)
        payment_method = PaymentMethod.objects.get(code=payment_method)
        receipt_code = get_random_string(20)  # allows secure access to order receipt
        order = self.create(customer=customer,
                            total = total,
                            payment_method=payment_method,
                            payment_status=payment_status,
                            order_status = order_status,
                            order_number=order_number,
                            delivery_date=delivery_date,#datetime.datetime.strptime(delivery_date,'%m/%d/%y').strftime('%Y-%m-%d'),
                            updated_by=customer,
                            created_by=customer
                            )

        for mydict in lineitems:
            product_id = CustomerPrice.objects.get(id=mydict['product_id'])
            OrderItem.objects.create(order = order,
                                     product = product_id.product,
                                     price = mydict['price'],
                                     quantity = mydict['quantity'],
                                     sub_total = mydict['line_total'],
                                     #sub_total = locale.atof(mydict['line_total']),
                                     #tax_rate=tax_rate,
                                     #tax_method=tax_method,
                                     updated_by=customer,
                                     created_by=customer)

        return order

    def send_order_confirmation(self,
              order_number,total,lineitems,customer):

    	"""Sends email to user confirming order and contents"""
    	items = []
    	for mydict in lineitems:
                product_id = CustomerPrice.objects.get(id=mydict['product_id'])
                items.append({'product':product_id.product,'price':mydict['price'],
                               'quantity':mydict['quantity'],'sub_total':mydict['line_total']})


    	context = {
			'user': customer.last_name,
			'order_items':items,
			'order_number':order_number,
			'total':total,
			#'order_status':order_status,
			'MEDIA_URL': settings.MEDIA_URL,
			'SITE_URL': settings.SITE_URL
    					}

    	subject = 'Thanks for your purchase at Gaea! Order ' + str(order_number)
    	from_email = 'Sales gaeafoods <info@gaeafoods.com>'

    	# If at order screen, user provided an email address

    	to = customer

    	text_content = render_to_string('orders/email/order_confirmation.txt', context)
    	html_content = render_to_string('orders/email/order_confirmation.html', context)
    	msg = EmailMultiAlternatives(subject, text_content)
    	msg.attach_alternative(html_content, "text/html")
    	msg.to = [to]
    	msg.from_email = from_email

    	# Send a copy to me after finished as well
    	msg_copy = EmailMultiAlternatives("#Order " + str(order_number) + '--' + str(customer.company), text_content)
    	msg_copy.attach_alternative(html_content, "text/html")
    	msg_copy.to = ['Daniel@gaeafoods.com']
    	msg_copy.from_email = from_email

    	msg.send()
    	msg_copy.send()

    def get_all_orders(self):
        myorders = Order.objects.all()
        orders = []
        for item in myorders:
            orders.append({'created_on':str(item.created_on),'customer':item.customer.company,
               'order_number':item.order_number,'allocate':item.allocate_order,'payment_status':item.payment_status,'total':str(item.total)})

        return orders



class Order(models.Model):
    """
    Represents customer's order
    """
    ORDER_PENDING = 'Pending'
    ORDER_PROCESSING = 'Processing'
    ORDER_COMPLETE = 'Complete'
    ORDER_CANCELLED = 'Cancelled'

    ORDER_STATUS = (
               (ORDER_PENDING,'Pending'),
               (ORDER_PROCESSING,'Processing'),
               (ORDER_COMPLETE ,'Complete'),
               (ORDER_CANCELLED,'Cancelled'),

                )

    # Payment statuses
    PAYMENT_PENDING = 'Pending'
    PAYMENT_AUTHORIZED = 'Authorized'
    PAYMENT_PAID = 'Paid'

    PAYMENT_STATUS = (
            (PAYMENT_PENDING, 'Pending'),
            (PAYMENT_AUTHORIZED, 'Authorized'),
            (PAYMENT_PAID, 'Paid'),
        )

    customer = models.ForeignKey(Customer,null=True,blank=True)
    order_number = models.CharField(max_length=50,null=True,blank=True,help_text='Purchase Order number')
    shipping_cost = models.DecimalField(max_digits=9, decimal_places=2,null=True,blank=True)
    taxes = models.DecimalField(max_digits=9, decimal_places=2,null=True,blank=True)
    total = models.DecimalField(max_digits=9, decimal_places=2)
    payment_method = models.ForeignKey(PaymentMethod,default='Pending')
    order_status = models.CharField(max_length=20,choices=ORDER_STATUS)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS)
    #billing_address = models.ForeignKey(Address, null=True,blank=True,related_name='billing_orders')
    allocate_order = models.BooleanField(blank=True,default=False)
    delivery_date = models.DateField(null=True,blank=True)
    receipt_code = models.CharField(max_length=100,null=True,blank=True, help_text="Random code generate for each order for secure access.")
    updated_by = models.CharField(max_length=100)
    updated_on = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100)
    created_on = models.DateField(auto_now_add=True)

    objects = OrderManager()

    @property
    def company(self):
        return self.customer.company

    def get_orderitems(self):
        return self.items.prefetch_related('products').all()


    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    """
    Represents a purchase product
    """
    order = models.ForeignKey(Order, related_name='items')
    product = models.ForeignKey(Product)
    price = models.DecimalField(max_digits=9, decimal_places=2, help_text='Unit price of the product')
    quantity = models.IntegerField()
    taxes = models.DecimalField(max_digits=9, decimal_places=2,null=True,blank=True,default=1)
    sub_total = models.DecimalField(max_digits=9, decimal_places=2)
    tax_rate = models.FloatField(default=0.0)
    tax_method = models.CharField(max_length=2, choices=Tax.TAX_METHODS, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=100,null=True,blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100,null=True,blank=True)

    class Meta:

        verbose_name_plural = 'Order Items'

    def get_absolute_url(self):
        return reverse('orders:single_order',kwargs={'order_id':self.id})
