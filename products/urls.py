from django.conf.urls import url
from .views import (DashboardView,UserOrders,vision,mission,values,home,contact,allproducts,
            about,recipe,CustomerPrices,AddCustomerPrice,EditCustomerPrice,
            ProductsView,EditProductView,AddProductView,ProductBatchCreateView,
            CustomerPriceBatchView)

urlpatterns =[
    url(r'^$',home,name='index_view'),
    url(r'^myorders/$',UserOrders.as_view(),name='user_orders'),
    url(r'^dashboard/$',DashboardView.as_view(),name='dashboardview'),
    url(r'^contact/$',contact,name='contact'),
    url(r'^products/$',allproducts,name='products'),
    url(r'^about/$',about,name='about'),
    url(r'^tips/$',recipe,name='recipe'),
    url(r'^vision/$',vision,name='vision'),
    url(r'^mission/$',mission,name='mission'),
    url(r'^values/$',values,name='values'),


    url(r'^allproducts/$',ProductsView.as_view(),name='allproducts'),
    url(r'^addproduct/$',AddProductView.as_view(),name='addproduct'),
    url(r'^editproduct/(?P<pk>[\w-]+)$',EditProductView.as_view(),name='editproduct'),


    url(r'^customerprices/$',CustomerPrices.as_view(),name='customerprices'),
    url(r'^addcustomerprice/$',AddCustomerPrice.as_view(),name='addcustomerprice'),
    url(r'^editcustomerprice/(?P<pk>[\w-]+)$',EditCustomerPrice.as_view(),name='editcustomerprice'),


    url(r'^productbatchentry/$',ProductBatchCreateView.as_view(),name='productbatchentry'),
    url(r'^customer_price_batchentry/$',CustomerPriceBatchView.as_view(),name='customer_price_batchentry'),
]
