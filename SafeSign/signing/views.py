from django.conf import settings
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail

def home(request):
    return render(request, 'homepage.html')

def about(request):
    return render(request, 'about.html')

def clientsite(request):
    return render(request, 'clientsite.html')

def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        signatures = request.POST.get('sign1..10')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if User.objects.filter(username = username):
            messages.error(request, 'username already exists')
            return redirect('home')
        if User.objects.filter(email = email):
            messages.error(request, 'email already exists')
            return redirect('home')

        newuser = User.objects.create_user(username, signatures, email)
        newuser.save()

        messages.success(request, 'your account has been created successfully')
        subject = "welcome to SafeSign login, you have signed up"
        message = "hello" + username + " you have successfully signed up. please confirm your email address in order to activate your account. \n Thankyou"
        from_email = settings.EMAIL_HOST_USER
        to_email = [newuser.email]
        send_mail(subject, message, from_email, to_email, fail_silently = True)
        return redirect('signin')
    return render(request, 'signup.html')

def signin_sign(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        sign = request.POST.get('sign..10')

        user = authenticate(username = username, sign = sign)
        if user is not None:
            login(request, User)
            username = User.username
            return render(request, 'clientsite.html', {'user' : username})
        else:
            messages.error(request, "you need to sign up first")
            return redirect('home')
    return render(request, 'signin_sign.html')

def signin_pass(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username = username, password = password)
        if user is not None:
            login(request, User)
            username = User.username
            return render(request, 'clientsite.html', {'user' : username})
        else:
            messages.error(request, "you need to sign up first")
            return redirect('home')
    return render(request, 'signin_pass.html')
        
def signin(request):
    return render(request, 'signin.html')

def signout(request):
    logout(request)
    messages.success(request, 'logged out successfully')
    return redirect(home)