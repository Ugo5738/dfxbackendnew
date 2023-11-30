import random
import string

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from helpers.models import TrackingModel


class CustomUserManager(BaseUserManager):
    def _create_user(self, email, username=None, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, username, password, **extra_fields)


class User(AbstractUser, TrackingModel):
    email = models.EmailField(_('email address'), unique=True, blank=False, null=False)
    username = models.CharField(_('username'), max_length=30, unique=True, null=True, blank=True)
    referral_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True) ## REQUIRED FOR CHECKOUT

    email_verified = models.BooleanField(_('email verified'), default=False, help_text='Designates whether this users email is verified.')
    phone_verified = models.BooleanField(default=False)

    accepts_newsletters = models.BooleanField(default=False)
    accepts_terms_and_conditions = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if not self.pk and not self.referral_code:
            # Generate referral code
            self.referral_code = self._generate_referral_code()
        super().save(*args, **kwargs)

    def _generate_referral_code(self, size=20, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        # db_table = 'userprofile_user'


class Profile(TrackingModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True, null=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    address2 = models.CharField(max_length=255, null=True, blank=True)
    country = CountryField(multiple=False, null=True, blank=True)
    zip_code = models.CharField(max_length=200, null=True, blank=True)

    address_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.email}"

    # class Meta:
    #     db_table = 'userprofile_profile'

# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)


# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()


# class BlacklistedToken(models.Model):
#     token = models.CharField(max_length=500, unique=True)
#     blacklisted_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.token