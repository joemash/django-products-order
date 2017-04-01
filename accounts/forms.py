from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from accounts.models import Customer

class CustomerRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password',widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirm Password',widget=forms.PasswordInput)

    error_messages = {
        'duplicate_username':('A user with the specified name exists'),
        'too_short':('Password must be more than 8 characters'),
        'password_mismatch':('The password you entered do not match'),
        'user_same_pass':('cannot have username as Password'),
    }

    class Meta:
        model = Customer
        fields = ('email','first_name','last_name','company','address','phone_number')
        widgets ={
             'phone_number':forms.NumberInput,
        }
        labels ={
           'address':'Physical Address',
           'company':'Company Name'
        }


    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 8:
            raise forms.ValidationError(self.error_messages['too_short'])
        return password

    def clean_confirm_password(self):
       # email =self.cleaned_data['email']
        confirm_password =self.cleaned_data['confirm_password']
        if 'password' in self.cleaned_data and self.cleaned_data['password'] != confirm_password:
            raise forms.ValidationError(self.error_messages['password_mismatch'])
        #elif confirm_password == email:
         #   raise forms.ValidationError(self.error_messages['user_same_pass'])
        return confirm_password

    def clean_email(self):
        email =self.cleaned_data['email']
        if not email:
            raise forms.ValidationError('please enter an email address')
        if Customer.objects.filter(email__iexact=email).count() > 0:
            raise forms.ValidationError(self.error_messages['duplicate_username'])
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if not first_name:
            raise forms.ValidationError('please enter your first_name')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if not last_name:
            raise forms.ValidationError('please enter your lastname')
        return last_name


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = Customer
        fields = ('email',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Customer
        fields = ('email', 'password','is_active', 'is_admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

class PasswordResetForm(forms.Form):
    """
    Password reset form
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'New password...'}), min_length=8, max_length=50,
        error_messages={'required': 'Please enter your new password.'})
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password...'}), max_length=50,
        error_messages={'required': 'Please re-enter your new password for confirmation.'})

    def clean_confirm_password(self):
        confirm_password = self.cleaned_data['confirm_password']
        if 'password' in self.cleaned_data and self.cleaned_data['password'] != confirm_password:
            raise forms.ValidationError("Your new password and confirm password didn't matched.")
        return confirm_password


class ChangePasswordForm(PasswordResetForm):
    """
    Change password form
    """
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Current password...'}), max_length=50,
        error_messages={'required': 'Please enter your current password.'})
