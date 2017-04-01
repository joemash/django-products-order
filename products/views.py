import json,string,random,datetime,locale
from django.core import serializers
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.utils.decorators import method_decorator
from django.db.models import Sum,Count
from django.db import IntegrityError
from django.http import HttpResponseRedirect,HttpResponse,JsonResponse
from django.shortcuts import render
from django.views.generic import (View,TemplateView,ListView,
                CreateView,UpdateView)
from utils import LoginRequiredMixin
from orders.models import Order
from products.models import Product,CustomerPrice,About,Recipe
from accounts.models import Customer
from products.forms import ContactUsForm


def home(request):
    return render(request,'frontpage.html',{})


def contact(request):
    form = ContactUsForm(request.POST or None)
    if form.is_valid():
        form_email = form.cleaned_data.get("email")
        form_message = form.cleaned_data.get("message")
        form_phone = form.cleaned_data.get("phone")
        form_full_name = form.cleaned_data.get("full_name")
        subject = 'Site contact form'
        from_email = 'marketing@pytechsolutions.com'
        to_email = [from_email]
        contact_message = "%s: %s via %s %s "%(
                form_full_name,
                form_message,
                form_email,form_phone)

        send_mail(subject,
                contact_message,
                from_email,
                to_email)
        messages.success(request,'Thanks your message has been received will get back to you')
        return HttpResponseRedirect('/contact/')

    context = {
        "form": form,

    }

    return render(request, "contact.html", context)



def about(request):
    about = About.objects.all()
    return render(request,'about.html',{'about':about})

def recipe(request):
    recipe = Recipe.objects.all()
    return render(request,'recipe.html',{'recipe':recipe})

def vision(request):
    return render(request,'vision.html',{})

def mission(request):
    return render(request,'mission.html',{})

def values(request):
    return render(request,'values.html',{})


def allproducts(request):
    products = Product.objects.all()
    paginator = Paginator(products, 6)# Show 6 courses per page
    page = request.GET.get('page')
    try:
        allproducts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        allproducts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        allproducts = paginator.page(paginator.num_pages)

    return render(request,'products.html',{'allproducts':allproducts})


class DashboardView(LoginRequiredMixin):
    model = Order
    template_name = 'chart.html'
    def get(self,request,*args,**kwargs):
        if request.is_ajax():
            all_orders = Order.objects.all()
            json_data = json.dumps(serializers.serialize('json',all_orders))
            return HttpResponse(json_data,content_type='application/json')
        return super(DashboardView,self).get(request)


    def get_total_orders(self):
        orders = Order.objects.annotate(Count('total'))

        return orders

    def get_context_data(self,**kwargs):
   # Call the base implementation first to get a context
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['totals'] = self.get_total_orders()
        if self.request.user.is_staff:
            context['order_count'] = Order.objects.all().count()
        else:
            context['order_count'] = Order.objects.filter(customer=self.request.user).count()

        return context


class UserOrders(ListView):
    model = Order
    template_name = 'dashboard.html'
    paginate_by = 5
    context_object_name = 'user_orders'

    def get_queryset(self,**kwargs):

        if self.request.user.is_staff:
            return Order.objects.all()
        else:
            return Order.objects.filter(customer=self.request.user).order_by('-id')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UserOrders, self).dispatch(request, *args, **kwargs)


class ProductsView(ListView):
    model = Product
    template_name = 'allproducts.html'
    paginate_by = 5
    context_object_name = 'products'

    def get_queryset(self,**kwargs):

        if self.request.user.is_staff:
            return Product.objects.all()
        else:
            return None

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ProductsView, self).dispatch(request, *args, **kwargs)


class AddProductView(CreateView):
    model = Product
    template_name = 'add_product.html'
    fields = ['name','short_description','price']
    success_url = reverse_lazy('allproducts')


class EditProductView(UpdateView):
    model = Product
    template_name =  'add_product.html'
    fields = ['name','short_description','price']
    success_url = reverse_lazy('allproducts')


class CustomerPrices(ListView):
    model = CustomerPrice
    template_name = 'customerprice.html'
    paginate_by = 5
    context_object_name = 'customerprices'

    def get_queryset(self,**kwargs):

        if self.request.user.is_staff:
            return CustomerPrice.objects.all()
        else:
            return None

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CustomerPrices, self).dispatch(request, *args, **kwargs)


class AddCustomerPrice(CreateView):
    model = CustomerPrice
    template_name = 'add_customer_price.html'
    fields = ['name','product','price']
    success_url = reverse_lazy('customerprices')#'/customerprices/' #reverse


class EditCustomerPrice(UpdateView):
    model = CustomerPrice
    template_name =  'add_customer_price.html'
    fields = ['name','product','price']
    success_url = reverse_lazy('customerprices')


##Batch Processing
class ProductBatchCreateView(LoginRequiredMixin):
    model = Product
    template_name = 'add_product_batch.html'

    def post(self,request,*args,**kwargs):
	    if request.is_ajax():
	        product_items_json = request.POST.get("productItems")
	        #convert the json string to a python object
	        product_items = json.loads(product_items_json)
	        try:
	            #save/create product
	            Product.objects.create_batch(product_items)

	            data = {
	               'url':'http://josephat.webfactional.com/allproducts/',

	            }
	        except IntegrityError as e:

	            if 'column slug is not unique' in e.message:
	                data={
	                  'error':'You cannot add an already existing product',
	                  }
	            else:
	                data={
	                  'error':str(e),
	                  }
	        return JsonResponse(data)
	    return super(ProductBatchCreateView,self).get(request)


class CustomerPriceBatchView(LoginRequiredMixin):
    model = CustomerPrice
    template_name = 'add_customer_price_batch.html'

    def get_context_data(self,**kwargs):
        context = super(CustomerPriceBatchView,self).get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        context['customers'] = Customer.objects.all()
        return context

    def post(self,request,*args,**kwargs):
        if request.is_ajax():
            customer = request.POST.get('customer')
            customer_items_json = request.POST.get("customerItems")

            #convert the json string to a python object
            customer_items = json.loads(customer_items_json)

            #create_battch() method expects to get customer_type instance not string
            customer_instance = Customer.objects.get(email=customer)
            try:
                #save/create product
                CustomerPrice.objects.create_batch(customer_items,customer_instance)

                data = {
                   'url':'http://josephat.webfactional.com/customerprices/',

                }
            except IntegrityError as e:

                if 'column product_id is not unique' in e.message:
                    data={
                      'error':'You cannot add an already existing product',
                      }
                else:
                    data={
                      'error':str(e),
                      }

            return JsonResponse(data)
        return super(CustomerPriceBatchView,self).get(request)
