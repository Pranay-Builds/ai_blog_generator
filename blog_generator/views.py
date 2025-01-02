from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from pytube import YouTube
from django.conf import settings
import os

# Create your views here.
@login_required
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data["link"]

            return JsonResponse({'content': f'Dummy blog content for {yt_link}'})
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent'}, status=400)
        # Get video title
        title = yt_title(yt_link)

        # Get transcript


        # use OpenAI api to generate blog content

        # return blog article as json
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
def yt_title(link):
    yt = YouTube(link)
    return yt.title

def download_audio(link):
    yt = YouTube(link)
    audio = yt.streams.filter(only_audio=True).first()
    audio.download(output_path=settings.MEDIA_ROOT)
    base, ext = os.path

def yt_transcript(link):
    # audio_file = pass
    pass
    

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    return render(request, 'login.html')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeatPassword = request.POST['repeatPassword']

        if password == repeatPassword:
            try:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                login(request, user)
                return redirect('/')
            except:
                error_message = 'Username or email already exists'
                return render(request, 'signup.html', {'error_message': error_message})
        else:
            error_message = 'Passwords do not match'
            return render(request, 'signup.html', {'error_message': error_message})
    return render(request, 'signup.html')

@login_required(login_url='login')
def user_logout(request):
    logout(request)
    return redirect('login')