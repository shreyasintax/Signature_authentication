# In signatures/views.py
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, SignatureSample
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.files.uploadedfile import InMemoryUploadedFile


@api_view(['POST'])
@csrf_exempt
def verify_signature(request):
    if request.method == 'POST':
        user_id = request.data.get('user_id')
        signature_image = request.FILES.get('signature_image')

        if user_id and signature_image:
            # Find the user with the provided user_id
            user = get_object_or_404(User, user_id=user_id)

            # Convert the uploaded image to grayscale
            uploaded_image = cv2.imdecode(np.fromstring(signature_image.read(), np.uint8), cv2.IMREAD_GRAYSCALE)

            # Load the reference images from the user's samples
            samples = user.signaturesample_set.all()
            threshold = 0.9
            similar_count = 0

            for ref_sample in samples:
                reference_image = cv2.imread(ref_sample.signature_image.path, cv2.IMREAD_GRAYSCALE)

                # Calculate the similarity score using SSIM
                similarity_score = ssim(uploaded_image, reference_image)

                # Set a threshold for similarity score
                if similarity_score > threshold:
                    similar_count += 1

            if similar_count == len(samples):
                # All samples are similar to the uploaded signature
                # Authenticate the user and log them in
                user_obj = authenticate(request, user_id=user_id, signature_image=signature_image)
                if user_obj is not None:
                    login(request, user_obj)
                    return JsonResponse({'message': 'Login successful'})

        return JsonResponse({'error': 'Invalid user ID or signature'}, status=401)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

@api_view(['POST'])
@csrf_exempt
def encrypt_signature(request):
    if request.method == 'POST':
        # Get the signature image from the request
        signature_image = request.FILES.get('signature_image')

        # Perform signature encryption
        encrypted_signature = None

        if signature_image:
            # Load the public key used for encryption
            with open('public_key.pem', 'rb') as file:
                public_key = RSA.import_key(file.read())

            # Create a cipher object with the public key
            cipher = PKCS1_OAEP.new(public_key)

            # Read the signature image data
            image_data = signature_image.read()

            # Encrypt the signature image data
            encrypted_data = cipher.encrypt(image_data)

            # Convert the encrypted data to base64 for easier transmission
            encrypted_signature = base64.b64encode(encrypted_data).decode('utf-8')

            # Save the encrypted signature in the database or do further processing

        # Return the encrypted signature
        return JsonResponse({'encrypted_signature': encrypted_signature})

    # Handle invalid request methods
    return JsonResponse({'error': 'Invalid request method'})


@api_view(['GET', 'POST'])
@csrf_exempt
def user_registration(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        signature_samples = request.FILES.getlist('signature_sample')

        # Check if the user ID is not empty and if exactly 10 signature samples are provided
        if user_id and len(signature_samples) == 10:
            # Create a new user with the provided user ID
            user, created = User.objects.get_or_create(user_id=user_id)

            # Save the 10 signature samples for the user
            for i, signature_sample in enumerate(signature_samples, start=1):
                SignatureSample.objects.create(user=user, signature_image=signature_sample)

            # Fetch the samples again after saving them to the database
            samples = user.signaturesample_set.all()

            # Define the threshold for similarity score
            threshold = 0.9

            # Create a list to hold similarity counts for each reference sample
            similarity_counts = [0] * len(samples)

            # Calculate similarity scores for each combination of reference and uploaded images
            for i, ref_sample in enumerate(samples):
                reference_image = cv2.imread(ref_sample.signature_image.path, cv2.IMREAD_GRAYSCALE)

                for j, signature_sample in enumerate(samples):
                    uploaded_image_data = signature_sample.signature_image.read()
                    uploaded_image = cv2.imdecode(np.frombuffer(uploaded_image_data, np.uint8), cv2.IMREAD_GRAYSCALE)

                    similarity_score = ssim(uploaded_image, reference_image)

                    if similarity_score > threshold:
                        similarity_counts[i] += 1

            # Check if all similarity counts are equal to the number of samples
            if all(count == len(samples) for count in similarity_counts):
                # All samples are similar to each other
                # Perform further processing or encryption

                # Check if this is the first time the user logs in from this device
                device_ip = request.META.get('REMOTE_ADDR')
                first_login = not user.device_ip or user.device_ip != device_ip
                user.device_ip = device_ip
                user.save()

                # Redirect the user to the home page after successful registration
                return redirect('home')
            else:
                # Uploaded samples are not similar to each other
                # Delete all the uploaded samples and return an error message
                user.signaturesample_set.all().delete()
                return JsonResponse({'error': 'The uploaded samples are not similar to each other'}, status=400)

    return render(request, 'registration.html')


# Django imports
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.conf import settings

# ... Your other views

# Home view with login_required decorator
@login_required
def home(request):
    # Your existing code for the home view
    # You can use `request.user` to access the logged-in user object
    # For example:
    # user = request.user
    # user_id = user.user_id

    return render(request, 'home.html', {'user': request.user})

# In signatures/views.py
# ... Other imports ...

# Add the necessary import for authentication-related functions
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse

# Your existing views

# User login view
# In signatures/views.py

# Import other necessary modules...

from django.shortcuts import render

# Your other view functions...

# User login view
@api_view(['GET', 'POST'])
@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        user_id = request.data.get('user_id')
        signature_image = request.FILES.get('signature_image')

        # Authenticate the user based on user_id and signature
        user = authenticate(request, user_id=user_id, signature_image=signature_image)

        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'Login successful'})
        else:
            return JsonResponse({'error': 'Invalid user_id or signature'}, status=400)

    return render(request, 'login.html')  # Render the login form on GET request

# Your other view functions...


# User logout view
@api_view(['POST'])
@csrf_exempt
def user_logout(request):
    logout(request)
    return JsonResponse({'message': 'Logout successful'})

# Your existing views
