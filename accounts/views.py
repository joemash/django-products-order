import json
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail,EmailMultiAlternatives,EmailMessage
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.template import Context
from django.template.loader import get_template,render_to_string
from accounts.models import Customer
from .forms import CustomerRegistrationForm,PasswordResetForm,ChangePasswordForm

class UsersView(TemplateView):
    pass

class LoginView(TemplateView):
    template_name = 'login.html'

    def get(self,request,*args,**kwargs):

        return super(LoginView,self).get(request)

    def post(self,request,*args,**kwargs):
        username = request.POST['username']
        password = request.POST['password']
        print(username)
        user = authenticate(email=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if request.user.is_staff:
                    return HttpResponseRedirect('/dashboard/')
                else:
                    return HttpResponseRedirect('/myorders/')

            else:
                messages.info(request,'Your account is inactive kindly '
						'activate via the email we sent you')
        else:
            messages.info(request,'Your  password or username is wrong')

        return super(LoginView,self).get(request)


class LogoutView(TemplateView):

    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/accounts/login/')

class RegisterView(TemplateView):
    template_name = 'register.html'

    def get(self,request,*args,**kwargs):
        form = CustomerRegistrationForm()
        return super(RegisterView,self).get(request,form=form)

    def post(self,request,*args,**kwargs):
        error = None
        success = None

        form = CustomerRegistrationForm(request.POST)
        #password = request.POST['password']
        #email = request.POST['email']

        if form.is_valid():

            #form = CustomerRegistrationForm()


            #Send verification code to user to activate account



            try:
                data = form.cleaned_data
                password = data['password']
                email = data['email']

                user = form.save(commit=False)
                user.set_password(password)
                user.save()
                email = email.strip()
                user = Customer.objects.get_verify_code(email)

                context = {'user': user, 'SITE_NAME': settings.SITE_NAME, 'DOMAIN': settings.DOMAIN}
                print(context)
                msg_subject = 'Activate Account'
                text_content = render_to_string("accounts/email/email_signup_confirm.txt",context)
                to_email = '%s <%s>' % (user.get_full_name(),user)
                html_content = render_to_string('accounts/email/email_signup_confirm.html', context)
                msg = EmailMultiAlternatives(msg_subject, text_content)
                msg.attach_alternative(html_content, "text/html")

                msg.from_email = 'Daniel@gaeafoods.com'
                msg.to = [to_email]

                # Send a notification copy to admin
                text_content2 = render_to_string("accounts/email/admin_notify.txt",context)
                html_content2 = render_to_string('accounts/email/admin_notify.html', context)
                msg_copy = EmailMultiAlternatives("New Customer Registration", text_content2)
                msg_copy.attach_alternative(html_content2, "text/html")
                msg_copy.to = ['Daniel@gaeafoods.com']
                msg_copy.from_email = 'Daniel@gaeafoods.com'

                msg.send()
                msg_copy.send()


                return HttpResponseRedirect('/accounts/register_complete/')

            except ValidationError as e:
                error = e.message


        return super(RegisterView,self).get(request,form=form,success=success,error=error)



class RegisterCompleteView(TemplateView):
    template_name = 'accounts/register_complete.html'

    def get(self,request):

        messages.success(request,'Thank you for registering with Gaea Foods An activation email will arrive shortly Please click the link in the email and complete your registration')

        return super(RegisterCompleteView,self).get(request)


class ActivateUserView(TemplateView):
    """
    Activate User Account
    """

    template_name = 'accounts/account_active.html'


    def get(self, request, user_id,verify_code):
        error = None
        success = None

        try:
            Customer.objects.make_user_active(user_id, verify_code)
            success = 'Your account has been successfully activated.'
        except Exception as e:
            error = e.message
        return super(ActivateUserView, self).get(request,user_id=user_id,verify_code=verify_code,
                         error=error, success=success)


class ForgotPasswordView(TemplateView):
    """
    Password recovery view
    """
    template_name = 'accounts/forgot_password.html'


    def post(self, request):
        error = None
        success = None
        email = request.POST.get('email', None)

        if email:
            email = email.strip()
            try:
                user = Customer.objects.get_reset_code(email)

                # Sending password reset link email to user

                context = {'user': user, 'SITE_NAME': settings.SITE_NAME, 'DOMAIN': settings.DOMAIN}
                msg_subject = 'Password Reset'
                text_content = render_to_string("accounts/email/password_reset_subject.txt",context)
                to_email = '%s <%s>' % (user.get_full_name(),user)
                html_content = render_to_string('accounts/email/password_reset.html', context)
                msg = EmailMultiAlternatives(msg_subject, text_content)
                msg.attach_alternative(html_content, "text/html")

                msg.from_email = 'admin@gaeafoods.com'
                msg.to = [to_email]

                msg.send()

                success = 'Password reset intructions has been sent to your email address.'
            except Exception as e:
                error = e.message
        else:
            error = 'Please provide an email address'

        return self.get(request, error=error, success=success)


class PasswordResetView(TemplateView):
    """
    Password recovery view
    """

    template_name = 'accounts/password_reset.html'


    def get(self, request, user_id, reset_code):
        form = PasswordResetForm()
        return super(PasswordResetView, self).get(request, form=form, user_id=user_id, reset_code=reset_code)

    def post(self, request, user_id, reset_code):
        error = None
        success = None
        form = PasswordResetForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            try:
                Customer.objects.reset_password(user_id, reset_code, data['password'])
                success = 'Your password has been reset successfully.'
            except Exception as e:
                error = e.message

        return super(PasswordResetView, self).get(request, form=form, user_id=user_id, reset_code=reset_code,
                                                  error=error, success=success)


class ChangePasswordView(TemplateView):
    """
    Password recovery view
    """

    template_name = 'accounts/change_password.html'


    def get(self, request):
        form = ChangePasswordForm()
        return super(ChangePasswordView, self).get(request, form=form)

    def post(self, request):
        error = None
        success = None
        form = ChangePasswordForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            try:
                Customer.objects.change_password(request.user, data['current_password'], data['password'])
                success = 'Your password has been changed successfully.'
            except Exception as e:
                error = e.message

        return super(ChangePasswordView, self).get(request, form=form, error=error, success=success)
