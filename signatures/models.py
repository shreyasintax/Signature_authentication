from django.db import models
'''from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, user_id, email, password=None, **extra_fields):
        if not user_id:
            raise ValueError("The user ID must be set")
        if not email:
            raise ValueError("The email address must be set")
        
        email = self.normalize_email(email)
        user = self.model(user_id=user_id, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

from django.contrib.auth.hashers import make_password

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    device_ip = models.GenericIPAddressField(null=True, blank=True)
    encrypted_samples = models.TextField(null=True, blank=True)
    password = models.CharField(max_length=128, default=make_password(None))  # Dummy password

    objects = UserManager()

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.user_id

    def get_full_name(self):
        return self.user_id

    def get_short_name(self):
        return self.user_id


class SignatureSample(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    signature_image = models.ImageField(upload_to='signature_samples/')

    def __str__(self):
        return f'Sample for {self.user.user_id}'
        '''

# signature_auth/models.py

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    signature_image = models.ImageField(upload_to='signatures/')
