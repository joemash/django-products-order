from django.conf.urls import url
from payments.views import PaymentAllocationView

urlpatterns = [
    url(r'^allorders/$',PaymentAllocationView.as_view(),name='payment_allocation'),

]
