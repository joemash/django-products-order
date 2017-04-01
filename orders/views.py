import json,string,random,datetime,cStringIO as StringIO
from django.shortcuts import render,redirect
from django.core import serializers
from django.core.urlresolvers import reverse
from django.template.loader import get_template, render_to_string
from django.template import RequestContext,Context
from django.http import HttpResponseRedirect,HttpResponse,JsonResponse
from django.views.generic import View,TemplateView
from utils import LoginRequiredMixin
from accounts.models import Customer
from products.models import CustomerPrice
from orders.models import Order,OrderItem,PaymentMethod
from xhtml2pdf import pisa
from cgi import escape




def order_number_generator(size=6,chars=string.digits):
    return ''.join(random.choice(chars) for x in range(size))



class OrderCreateView(LoginRequiredMixin):
    model = CustomerPrice
    template_name = 'order_entry.html'


    def get(self,request,*args,**kwargs):
        products =  CustomerPrice.objects.filter(name__email=request.user)
        customer = Customer.objects.get(email=request.user)
        payment_methods = PaymentMethod.objects.all()
        today_date = datetime.date.today()
        if request.is_ajax():
            product_id = request.GET.get("product_id")
            price = CustomerPrice.objects.filter(id=product_id)
            json_data = json.dumps(serializers.serialize('json',price))
            return HttpResponse(json_data,content_type='application/json')
        return super(OrderCreateView,self).get(request,products=products,
                      customer=customer,payment_methods=payment_methods,today_date=today_date)


    def post(self,request,*args,**kwargs):
        myitems = []
        import locale
        locale.setlocale(locale.LC_ALL, '')

        if request.is_ajax():
            line_items= request.POST.get("payload")
            total = request.POST.get("total")
            tot = locale.atof(total)
            payment_method = request.POST.get("payment_method")
            delivery_date = request.POST.get("delivery_date")

            contact_person = request.POST.get("contact_person")
            customer_phone = request.POST.get("customer_phone")


            order_number = order_number_generator(size=4,chars=string.digits)
            #convert the json string to a python object
            json1_data = json.loads(line_items)
            customer = request.user

            Order.objects.place(payment_method,'Pending',order_number,tot,json1_data,'Processing',customer,delivery_date)

            #update customer contact details
            Customer.objects.filter(email=customer).update(first_name=contact_person,phone_number=customer_phone)

            #Send order to client
            Order.objects.send_order_confirmation(order_number,tot,json1_data,customer)


            data = {
               'url':'http://127.0.0.1:8000/myorders/',
               'order_number':order_number,
            }
            return JsonResponse(data)
        return super(OrderCreateView,self).get(request)

class SingleOrder(LoginRequiredMixin):
    template_name = 'simple_invoice.html'

    def get_context_data(self,**kwargs):
        context = super(SingleOrder,self).get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        context['single_order'] = Order.objects.get(id=order_id)
        single_order1 = Order.objects.get(id=order_id)
        context['order_items'] = OrderItem.objects.filter(order=single_order1)
        return context

def single_order(request,order_id):
    single_order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=single_order)
    context = {'single_order':single_order,'order_items':order_items}
    return render(request,'simple_invoice.html',context)

#Method to allow CSS to be rendered by Pisa
def fetch_resources(uri, rel):
    path = os.path.join(settings.MEDIA_ROOT,uri.replace(settings.MEDIA_URL, ""))
    return path


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    context =context_dict
    html  = template.render(context)
    result = StringIO.StringIO()

    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))



def generate_PDF(request,order_id):
    single_order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=single_order)
    context = {'single_order':single_order,'order_items':order_items,'pagesize':'A3',}
    return render_to_pdf(
            'simple_pdf.html',
	         context
        )


class ReportsView(LoginRequiredMixin):
    model  = Order
    template_name = 'reports.html'

    def get(self,request,*args,**kwargs):
        orders = Order.objects.filter(customer=request.user)
        if request.is_ajax():
            json_data = serializers.serialize('json',orders)
            return HttpResponse(json_data,content_type='application/json')
        return super(ReportsView,self).get(request)

class AdminReportsView(LoginRequiredMixin):
    template_name = 'all_order_reports.html'

    def get(self,request,*args,**kwargs):
        customers = Customer.objects.all()
        myorders = Order.objects.get_all_orders()

        if request.is_ajax():
            #json_data = serializers.serialize('json',myorders)
            #print json_data
            #json_data = json.dumps(map(unicode, myorders))
            #print(type(myorders))
            #return JsonResponse(myorders,safe=False)
            json_data = json.dumps(myorders) #dump list as JSON
            return HttpResponse(json_data,content_type='application/json')
        return super(AdminReportsView,self).get(request,customers=customers)
