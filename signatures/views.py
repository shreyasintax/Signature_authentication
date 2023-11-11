# In signatures/views.py
'''import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, SignatureSample
import cv2'''
'''import numpy as np
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
import imghdr
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import User, SignatureSample
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import numpy as np
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from .models import User, SignatureSample


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

            # Validate and process signature samples
            try:
                processed_samples = []
                for signature_sample in signature_samples:
                    content_type = signature_sample.content_type
                    if content_type.startswith('image/'):
                        if imghdr.what(None, h=signature_sample.read()) is not None:
                            processed_samples.append(signature_sample)

                if len(processed_samples) != len(signature_samples):
                    return JsonResponse({'error': 'Invalid image files'}, status=400)

                # Save the processed signature samples for the user
                for i, signature_sample in enumerate(processed_samples, start=1):
                    SignatureSample.objects.create(user=user, signature_image=signature_sample)

                # Rest of your processing...

                return redirect('home')  # Redirect to home page after successful registration

            except Exception as e:
                return JsonResponse({'error': f'Error processing images: {str(e)}'}, status=500)

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

        try:
            # Authenticate the user based on user_id
            user = User.objects.get(user_id=user_id)

            # Retrieve the user's registered signature sample
            registered_signature_sample = SignatureSample.objects.get(user=user)

            # Perform a simple similarity comparison (simplified example)
            similarity_score = calculate_similarity(signature_image, registered_signature_sample.signature_image)

            # You might define a threshold for similarity and adjust as needed
            similarity_threshold = 0.7

            if similarity_score >= similarity_threshold:
                login(request, user)
                print(similarity_score)
                return JsonResponse({'message': 'Login successful'})
            else:
                return JsonResponse({'error': 'Invalid user_id or signature'}, status=400)

        except User.DoesNotExist:
            return JsonResponse({'error': 'User does not exist'}, status=400)
        except SignatureSample.DoesNotExist:
            return JsonResponse({'error': 'User signature not found'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

    return render(request, 'login.html')



from skimage.metrics import structural_similarity as ssim
from PIL import Image
import numpy as np

def calculate_similarity(signature_image1, signature_image2):
    try:
        # Load the images
        img1 = Image.open(signature_image1)
        img2 = Image.open(signature_image2)

        # Get dimensions of the images
        width1, height1 = img1.size
        width2, height2 = img2.size

        # Choose target size based on the larger dimensions of the images
        target_width = max(width1, width2)
        target_height = max(height1, height2)
        target_size = (target_width, target_height)

        # Resize images to the chosen target size
        img1_resized = img1.resize(target_size)
        img2_resized = img2.resize(target_size)

        # Convert resized images to grayscale and numpy arrays
        img1_gray = np.array(img1_resized.convert("L"))
        img2_gray = np.array(img2_resized.convert("L"))

        # Calculate the Structural Similarity Index (SSI)
        similarity_score = ssim(img1_gray, img2_gray)

        return similarity_score

    except Exception as e:
        print(f"Error calculating similarity: {e}")
        return 0  # Return a default similarity score in case of an error

# Usage example
signature_similarity = calculate_similarity('path_to_signature1.jpg', 'path_to_signature2.jpg')
print(f"Similarity score: {signature_similarity}")





# Your other view functions...
def get_all_signature_samples(request):
    all_signature_samples = SignatureSample.objects.all()

    # Convert queryset to a list of dictionaries
    signature_samples_list = [
        {
            'id': sample.id,
            'user_id': sample.user.user_id,
            'signature_image_url': sample.signature_image.url
        }
        for sample in all_signature_samples
    ]

    return JsonResponse({'signature_samples': signature_samples_list})



# User logout view
@api_view(['POST'])
@csrf_exempt
def user_logout(request):
    logout(request)
    return JsonResponse({'message': 'Logout successful'})

# Your existing views'''

# signature_auth/views.py

import json
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, SignatureVerificationForm
from .models import UserProfile
from scipy.spatial.distance import cosine

def register_user(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        signature_form = SignatureVerificationForm(request.POST, request.FILES)

        if user_form.is_valid() and signature_form.is_valid():
            # Save user information
            user = user_form.save()
            print(user)
            signature_image = signature_form.cleaned_data['signature_image']
            UserProfile.objects.create(user=user, signature_image=signature_image)

            return redirect('verify_signature')  # Redirect to login page after successful registration
    else:
        user_form = UserRegistrationForm()
        signature_form = SignatureVerificationForm()

    return render(request, 'registration.html', {'user_form': user_form, 'signature_form': signature_form})

@login_required
def verify_signature(request):
    if request.method == 'POST':
        form = SignatureVerificationForm(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data['username']
            user_signature = form.cleaned_data['signature_image']
            
            # Authenticate the user based on the provided username
            user = authenticate(username=username)
            
            if user and user == request.user:
                try:
                    # Get the user's stored signature
                    stored_signature = UserProfile.objects.get(user=user).signature_image
                    # Perform signature verification (using the logic you provided)
                    similarity = calculate_signature_similarity(user_signature, stored_signature)
                    # Set a threshold for similarity
                    threshold = 0.9
                    if similarity > threshold:
                        # Successful signature verification
                        # Redirect to the original website (replace 'original_website_url' with the actual URL)
                        # return redirect('signatures/home.html')
                        return JsonResponse({'message': 'Login successful'})
                    else:
                        # Failed verification
                        return render(request, 'verification_failed.html')
                except UserProfile.DoesNotExist:
                    # UserProfile for the user does not exist
                    return render(request, 'user_profile_not_found.html')
            else:
                # Invalid username
                return JsonResponse({'message': 'Invalid username'})
    else:
        form = SignatureVerificationForm()

    return render(request, 'login.html', {'form': form})

def calculate_signature_similarity(signature1, signature2):
    # Implement the signature similarity calculation logic
    # Example: Use the code you provided for calculating feature vectors and distances
    # Make sure to properly handle image processing, feature extraction, and similarity calculations
    # Return a similarity score
    return 1
