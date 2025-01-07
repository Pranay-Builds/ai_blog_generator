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
import assemblyai as aai
from youtubesearchpython import VideosSearch
import yt_dlp
import time
import requests


@login_required
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data["link"]

        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent'}, status=400)

        title = yt_title(yt_link)
        transcript = yt_transcript(yt_link)
        if not transcript:
            return JsonResponse({'error': 'Transcript not found'}, status=500)

        blog_content = generate_blog_from_transcript(transcript)
        if not blog_content:
            return JsonResponse({'error': 'Blog content not generated due to a problem, Try again later'}, status=500)

        return JsonResponse({'title': title, 'content': blog_content})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def yt_title(link):
    ydl_opts = {
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=False)
        return info.get('title', None)

def download_audio(yt_link):
    download_dir = 'downloads'
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{download_dir}/%(id)s.%(ext)s',
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(yt_link, download=True)
        audio_file_path = f"{download_dir}/{info['id']}.webm"
        return audio_file_path

def yt_transcript(link):
    audio_file_path = download_audio(link)
    aai.settings.api_key = "d9c34879abfc427c9acc06c4e3b4a384"

    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file_path)

    while transcript.status != "completed":
        time.sleep(5)
        transcript = transcriber.get(transcript.id)

    if transcript.status == "completed" and transcript.text:
        return transcript.text
    else:
        return None

@login_required
def generate_blog_from_transcript(transcript):
    gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    gemini_api_key = "AIzaSyC5RyGOs_00EQbPSdSY7LllAuPq95SrmcQ"

    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "contents": [
            {
                "parts": [{"text": f"Convert the following YouTube transcript into a well-structured blog post:\n\n{transcript}"}]
            }
        ]
    }

    response = requests.post(
        f"{gemini_api_url}?key={gemini_api_key}", headers=headers, json=payload
    )

    print("API Response:", response.json())

    if response.status_code == 200:
        try:
            content = response.json()
            # Extracting the generated text
            generated_content = content['candidates'][0]['content']['parts'][0]['text']
            return generated_content
        except KeyError:
            return "Blog content could not be generated."
    else:
        return f"Error: {response.status_code} - {response.text}"

    

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

        if password != repeatPassword:
            error_message = 'Passwords do not match'
            return render(request, 'signup.html', {'error_message': error_message})

        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            error_message = 'Username or email already exists'
            return render(request, 'signup.html', {'error_message': error_message})

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        login(request, user)
        return redirect('/')

    return render(request, 'signup.html')

@login_required(login_url='login')
def user_logout(request):
    logout(request)
    return redirect('login')
