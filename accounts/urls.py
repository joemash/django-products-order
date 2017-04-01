from django.conf.urls import url
from .views import (LoginView,RegisterView,LogoutView,
	  ForgotPasswordView, PasswordResetView, ChangePasswordView,RegisterCompleteView,
	  ActivateUserView)

urlpatterns = [
    url(r'^login/$',LoginView.as_view(),name='login_view'),
    url(r'^register/$',RegisterView.as_view(),name='register_view'),
    url(r'^register_complete/$',RegisterCompleteView.as_view(),name='register_complete_view'),
    url(r'^verify_code/(?P<user_id>\d+)-(?P<verify_code>\w+)/$',
        ActivateUserView.as_view(), name='activate_account'),
    url(r'^logout/$',LogoutView.as_view(), name='accounts_logout'),
    url(r'^forgot_password/$', ForgotPasswordView.as_view(), name='accounts_forgot_password'),
    url(r'^change_password/$', ChangePasswordView.as_view(), name='change_password'),
    url(r'^password_reset/(?P<user_id>\d+)-(?P<reset_code>\w+)/$',
        PasswordResetView.as_view(), name='accounts_password_reset'),
]
