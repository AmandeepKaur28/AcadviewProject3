# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from myapp.forms import SignUpForm
from myapp.forms import LoginForm ,PostForm,LikeForm,CommentForm
from models import UserModel,SessionToken,PostModel,LikeModel,CommentModel
from django.contrib.auth.hashers import make_password,check_password
from django.shortcuts import render,redirect
from DjangoProject.settings import BASE_DIR
from imgurpython import ImgurClient
from datetime import datetime

# Create your views here.
def signup_view(request):
  if request.method == "POST":
      signup_form=SignUpForm(request.POST)
      if signup_form.is_valid():
          username = signup_form.cleaned_data['username']
          name = signup_form.cleaned_data['name']
          email = signup_form.cleaned_data['email']
          password = signup_form.cleaned_data['password']
          user = UserModel(name=name, password=make_password(password), email=email, username=username)
          user.save()
          return render(request, 'login.html')
  elif request.method == 'GET':
      signup_form= SignUpForm()
  return render(request, 'index.html', {'form': signup_form})


def login_view(request):
    response_data = {}
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = UserModel.objects.filter(username=username).first()

            if user:
                if check_password(password, user.password):
                    token = SessionToken(user=user)
                    token.create_token()
                    token.save()
                    response = redirect('feed/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response
                else:
                    response_data['message'] = 'Incorrect Password! Please try again!'

    elif request.method == 'GET':
        form = LoginForm()

    response_data['form'] = form
    return render(request, 'login.html', response_data)

def feed_view(request):
    user = check_validation(request)
    if user:
        posts = PostModel.objects.all().order_by('created_on')
        for post in posts:
            existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
            if existing_like:
                post.has_liked = True

        return render(request, 'feed.html', {'posts': posts})

    else:
        return redirect('/login/')

def post_view(request):
  user = check_validation(request)
  if user:
      if request.method == 'POST':
          form = PostForm(request.POST, request.FILES)
          if form.is_valid():
              image = form.cleaned_data.get('image')
              caption = form.cleaned_data.get('caption')
              post = PostModel(user=user, image=image, caption=caption)
              post.save()

              path = str(BASE_DIR + post.image.url)

              client = ImgurClient('319feb40023adce', '2a01664decd3b8b2439bfce7caae16d47b671837')
              post.image_url = client.upload_from_path(path, anon=True)['link']
              post.save()

              return redirect('/feed/')

      else:
          form = PostForm()
      return render(request, 'post.html', {'form': form})
  else:
      return redirect('/login/')

def like_view(request):
        user = check_validation(request)
        if user and request.method == 'POST':
            form = LikeForm(request.POST)
            if form.is_valid():
                post_id = form.cleaned_data.get('post').id

                existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()
                if not existing_like:
                    LikeModel.objects.create(post_id=post_id, user=user)
                else:
                    existing_like.delete()

                return redirect('/feed/')


        else:
            return redirect('/login/')


def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
           return session.user
    else:
        return None
