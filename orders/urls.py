from django.conf.urls import url
from .views import (OrderCreateView,single_order,SingleOrder,
       generate_PDF,ReportsView,AdminReportsView)


urlpatterns =[
    url(r'^create_order/$',OrderCreateView.as_view(),name='create_order'),
    url(r'^single_order/(?P<order_id>[0-9]+)/$',SingleOrder.as_view(),name='single_order'),
    #url(r'^pdf/(?P<order_id>[0-9]+)/$',GeneratePdf.as_view(),name='pdf_view'),
    url(r'^pdf/(?P<order_id>[0-9]+)/$',generate_PDF,name='pdf_view'),
    url(r'^order_reports/$',ReportsView.as_view(),name='order_reports'),
    url(r'^all_order_reports/$',AdminReportsView.as_view(),name='all_order_reports'),

]
