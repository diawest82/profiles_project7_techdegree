from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from smartfields import fields


# Create your models here.

class CustomUser(BaseUserManager):
    # Create the custom model for the user.
    def create_user(self, first_name, last_name, email,
                    password=None, ):
        if not first_name:
            raise ValueError('Name required.')
        if not last_name:
            raise ValueError('Name required.')
        if not email:
            raise ValueError('Email required.')
        else:
            user = self.model(
                first_name=first_name,
                last_name=last_name,
                email=self.normalize_email(email),
            )
            user.set_password(password)
            user.save()
            return user

    def create_superuser(self, first_name, last_name, email,
                         password=None):
        user = self.create_user(
            first_name,
            last_name,
            email,
            password
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        max_length=255,
        unique=True,
    )
    first_name = models.CharField(max_length=75)
    last_name = models.CharField(max_length=75)
    joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUser()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    def get_short_name(self):
        return self.first_name

    def get_full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    avatar = fields.ImageField(upload_to='avatars/', blank=True, null=True)
    location = models.CharField(max_length=50, blank=True, null=True)
    fav_animal = models.CharField(max_length=50, blank=True, null=True)
    hobbies = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=75, blank=True,
                               null=True)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()







