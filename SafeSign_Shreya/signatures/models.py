# In signatures/models.py
from django.db import models
from django.contrib.auth.models import User

# In signatures/models.py
from django.db import models

class User(models.Model):
    user_id = models.CharField(max_length=50, unique=True)
    email = models.EmailField()
    device_ip = models.GenericIPAddressField(null=True, blank=True)
    encrypted_samples = models.TextField(null=True, blank=True)  # Store the encrypted samples as a JSON string

    def __str__(self):
        return self.user_id

class SignatureSample(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    signature_image = models.ImageField(upload_to='signature_samples/')

    def __str__(self):
        return f'Sample for {self.user.user_id}'
