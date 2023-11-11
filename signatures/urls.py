# signature_auth/urls.py

from django.urls import path
from signatures.views import register_user, verify_signature

urlpatterns = [
    path('register_user/', register_user, name='register_user'),
    path('verify_signature/', verify_signature, name='verify_signature'),
    # Add more paths as needed
]
