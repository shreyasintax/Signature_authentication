# signature_auth/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']
    
    signature_image = forms.ImageField()
    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True  # Make the email field required


class SignatureVerificationForm(forms.Form):
    username = forms.CharField(label="Username:",max_length=100)
    signature_image = forms.ImageField()

