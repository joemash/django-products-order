from django.db import models
from django.core.exceptions import ValidationError
from orders.models import Order


class Transaction(models.Model):
    """
    Model to hold pesapal callback info and Payment Transactions
    """
    PESAPAL_STATUS_CHOICES = (
       ('PENDING', 'Pending'),
       ('COMPLETED', 'Completed'),
       ('FAILED', 'Failed'),
       ('INVALID', 'Invalid'),
    )

    order = models.ForeignKey(Order)
    tracking_id = models.CharField(max_length=50, verbose_name='Pesapal Transaction Tracking ID')
    reference = models.CharField(max_length=50, verbose_name='Pesapal Merchant Reference')
    status = models.CharField(max_length=9, choices=PESAPAL_STATUS_CHOICES, default='PENDING')
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)


    def __unicode__(self):
        return unicode(self.id)
