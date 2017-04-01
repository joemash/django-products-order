from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import (AbstractBaseUser,
      BaseUserManager,PermissionsMixin)
from django.core.exceptions import ValidationError


class CustomerUserManager(BaseUserManager):
    ''' The default user for the project is the customer '''

    '''creates a user with the specified email and password '''
    def create_user(self,email,password=None,):
        if self.filter(email__iexact=email).count() > 0:
            raise ValidationError('user with this email address already exists')
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,email,password=None):
        '''Creates a superuser with a specified username and password  '''
        user = self.create_user(email=email,password=password)
        user.is_superuser=True
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.save(using=self._db)
        return user

    def get_reset_code(self, email):
        """
        Generates a new password reset code returns user
        """

        try:
            user = self.get(email__iexact=email)
            user.reset_code = self.make_random_password(length=20)
            user.reset_code_expire = timezone.now() + timedelta(days=2)
            user.save()

            return user

        except get_user_model().DoesNotExist:
            raise Exception('We can\'t find that email address, sorry!')

    def get_verify_code(self, email):
        """
        Generates a new verification code returns user
        """

        try:
            user = self.get(email__iexact=email)
            user.verify_code = self.make_random_password(length=20)
            user.verify_code_expire = timezone.now() + timedelta(days=3)
            user.save()

            return user

        except get_user_model().DoesNotExist:
            raise Exception('We can\'t find that email address, sorry!')

    def make_user_active(self, user_id, verify_code):
        """
        Set user account to active
        """

        try:
            user = self.get(id=user_id)
            if not user.verify_code or user.verify_code != verify_code or user.verify_code_expire < timezone.now():
                raise Exception('Verification code is invalid or expired.')

            # Verification code shouldn't be used again
            user.verify_code = None
            user.is_verified  = True
            user.is_active = True
            user.save()

        except get_user_model().DoesNotExist:
            raise Exception('Password reset code is invalid or expired.')


    def reset_password(self, user_id, reset_code, password):
        """
        Set new password for the user
        """

        if not password:
            raise Exception('New password can\'t be blank.')

        try:
            user = self.get(id=user_id)
            if not user.reset_code or user.reset_code != reset_code or user.reset_code_expire < timezone.now():
                raise Exception('Password reset code is invalid or expired.')

            # Password reset code shouldn't be used again
            user.reset_code = None
            user.set_password(password)
            user.save()

        except get_user_model().DoesNotExist:
            raise Exception('Password reset code is invalid or expired.')

    def change_password(self, user, current_password, password):
        """
        Updates user's current password
        """

        if not password:
            raise Exception('New password can\'t be blank.')

        # Changing user's password if old password verifies
        user = self.get(id=user.id)

        if not user.check_password(current_password):
            raise Exception('Your current password is wrong.')

        user.set_password(password)
        user.save()




class Customer(AbstractBaseUser,PermissionsMixin):
    '''
	custom user model for gaea.
	'''
    email = models.EmailField(unique=True,max_length=100)
    first_name= models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    company = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=250, null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    is_active=models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)
    is_admin=models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verify_code = models.CharField(max_length=512, blank=True, null=True,
                                   help_text='User account verification code.', editable=False)
    verify_code_expire = models.DateTimeField(max_length=512, blank=True, null=True,
                                             help_text='Verification  code expire date.', editable=False)

    reset_code = models.CharField(max_length=512, blank=True, null=True,
                                  help_text='Password reset code.', editable=False)
    reset_code_expire = models.DateTimeField(max_length=512, blank=True, null=True,
                                             help_text='Password reset code expire date.', editable=False)

    USERNAME_FIELD = 'email'
    objects = CustomerUserManager()

    def get_short_name(self):
        return self.last_name

    def get_full_name(self):
        return '{0} | {1}'.format(self.first_name,self.last_name)

    def has_perm(self,perm,obj=None):
        return True

    def get_absolute_url(self):
        return '/'

    def __str__(self):
        return  self.email
