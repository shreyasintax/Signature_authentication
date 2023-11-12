# Import necessary libraries and modules
import cv2
import numpy as np
import keras
from keras.models import Model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import UserRegistrationForm, SignatureVerificationForm
from .models import UserProfile

# Load VGG16 model for signature similarity calculation
vgg16 = keras.applications.VGG16(weights='imagenet', include_top=True, pooling='max', input_shape=(224, 224, 3))
basemodel = Model(inputs=vgg16.input, outputs=vgg16.get_layer('fc2').output)

# Helper functions for image processing and similarity calculation
def read_image(image_path):
    img = cv2.imread(image_path)
    return img

def get_feature_vector(img):
    img_resized = cv2.resize(img, (224, 224))
    feature_vector = basemodel.predict(img_resized.reshape(1, 224, 224, 3))
    return feature_vector

def calculate_feature_vectors_dist(f1, f2):
    f1 = f1.flatten()
    f2 = f2.flatten()
    similarity = np.dot(f1, f2) / (np.linalg.norm(f1) * np.linalg.norm(f2))
    distance = 1 - similarity
    return distance

# Calculate signature similarity using VGG16
from io import BytesIO
from PIL import Image

def calculate_signature_similarity(signature1, signature2):
    # Read image content from InMemoryUploadedFile
    img1_content = signature1.read()
    img2_content = signature2.read()

    # Convert the image content to PIL Image
    img1 = Image.open(BytesIO(img1_content))
    img2 = Image.open(BytesIO(img2_content))

    # Resize images if needed
    img1_resized = img1.resize((224, 224))
    img2_resized = img2.resize((224, 224))

    # Convert resized images to numpy arrays
    img1_np = np.array(img1_resized)
    img2_np = np.array(img2_resized)

    # Get feature vectors
    f1 = get_feature_vector(img1_np)
    f2 = get_feature_vector(img2_np)

    # Calculate similarity score
    similarity_score = 1 - calculate_feature_vectors_dist(f1, f2)

    return similarity_score


# Register user view
def register_user(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST, request.FILES)

        if user_form.is_valid():
            # Save user information
            user = user_form.save()
            signature_image = user_form.cleaned_data['signature_image']
            UserProfile.objects.create(user=user, signature_image=signature_image)

            return redirect('verify_signature')  # Redirect to login page after successful registration
    else:
        user_form = UserRegistrationForm()

    return render(request, 'registration.html', {'user_form': user_form})

# Verify signature view
@login_required
def verify_signature(request):
    if request.method == 'POST':
        form = SignatureVerificationForm(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data['username']
            user_signature = form.cleaned_data['signature_image']

            try:
                # Get the user's stored signature
                user_profile = UserProfile.objects.get(user__username=username)
                stored_signature = user_profile.signature_image

                # Perform signature verification using the VGG16-based logic
                similarity = calculate_signature_similarity(user_signature, stored_signature)

                # Set a threshold for similarity
                threshold = 0.9

                if similarity > threshold:
                    # Successful signature verification
                    # Redirect to the original website or return a JsonResponse as needed
                    return JsonResponse({'message': 'Login successful'})
                else:
                    # Failed verification
                    return render(request, 'verification_failed.html')

            except UserProfile.DoesNotExist:
                # UserProfile for the user does not exist
                return render(request, 'user_profile_not_found.html')

    else:
        form = SignatureVerificationForm()

    return render(request, 'login.html', {'form': form})

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def clientsite(request):
    return render(request, 'clientsite.html')
