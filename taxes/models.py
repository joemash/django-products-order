from django.db import models


class Tax(models.Model):

    """
    Represents a Tax Category
    """
    TAX_PERCENTAGE = 'PE'
    TAX_FIXED = 'FI'
    TAX_METHODS = ((TAX_PERCENTAGE, 'Percentage'),
                   (TAX_FIXED, 'Fixed'))

    name = models.CharField(max_length=100, unique=True)
    method = models.CharField(
        max_length=2, choices=TAX_METHODS,
        help_text='Tax deduction method: fixed tax per product or percentage (in fraction) of price per product')
    rate = models.FloatField(default=0.0)
    updated_by = models.CharField(max_length=100)
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100)

    class Meta:
        db_table = 'financial_tax'
        verbose_name_plural = 'Taxes'

    def __str__(self):
        return '%s [%s]: %s' % (self.name, self.method, self.rate)

    def calculate(self, price, quantity):
        """
        Calculate tax on price & quantity based on tax method
        """
        return self._calculate(price, quantity, self.method, self.rate, self.name)

    @classmethod
    def get_taxes(cls):
        """
        Return all taxes defined in system
        """
        return list(cls.objects.all())

    @classmethod
    def _calculate(cls, price, quantity, method, rate, name=None):
        """
        Calculate tax on price & quantity based on tax method
        """
        if method == cls.TAX_FIXED:
            return float(rate) * float(quantity)
        elif method == cls.TAX_PERCENTAGE:
            return float(rate) * float(quantity) * float(price)

        if name:
            raise Exception('Unknown tax method "%s" defined for tax rate: "%s"' % (method, name))

        raise Exception('Unknown tax method "%s"' % method)
