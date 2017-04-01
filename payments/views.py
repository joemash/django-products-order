import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from orders.models import Order
from accounts.models import Customer
from utils import LoginRequiredMixin


class PaymentAllocationView(LoginRequiredMixin):
    template_name = 'payment_allocation.html'

    def get(self,request,*args,**kwargs):
        customers = Customer.objects.all()
        myorders = Order.objects.get_all_orders()
        if request.is_ajax():
            json_data = json.dumps(myorders) #dump list as JSON
            return HttpResponse(json_data,content_type='application/json')
        return super(PaymentAllocationView,self).get(request,customers=customers)

    def post(self,request,*args,**kwargs):
        if request.is_ajax():
            order_number = request.POST.get('order_no')
            payment_chkbox = request.POST.get('payment_chk')
            if payment_chkbox == 'true':
                payment_status = True
                Order.objects.filter(order_number= order_number).update(payment_status='Paid',total=0.0)
            else:
                payment_status = False
                Order.objects.filter(order_number= order_number).update(payment_status='Pending')

            Order.objects.filter(order_number= order_number).update(allocate_order=payment_status)
        return super(PaymentAllocationView,self).get(request)
