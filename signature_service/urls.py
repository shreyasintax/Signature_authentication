"""
URL configuration for signature_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# In signature_service/urls.py

from django.conf import settings
from django.conf.urls.static import static



# SignatureAuth/urls.py

'''from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signature/', include('signatures.urls')),
    # Add more paths as needed
]'''


from django.urls import path
from signatures import views
from django.contrib import admin

urlpatterns = [
    path('', views.home, name='home'),  # Add this line for the root URL
    path('about/', views.about, name='about'),
    #path('logout/', views.user_logout, name='logout'),
    path('verify_signature/', views.verify_signature, name='verify_signature'),
    #path('encrypt_signature/', views.encrypt_signature, name='encrypt_signature'),
    path('register/', views.register_user, name='register'),
    #path('all-signature-samples/', views.get_all_signature_samples, name='get_all_signature_samples'),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
