# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from myapp.forms import SignUpForm
from myapp.forms import LoginForm ,PostForm,LikeForm,CommentForm
from models import UserModel,SessionToken,PostModel,LikeModel,CommentModel,CategoryModel# models are imported.
# in this file we are adding functionality to our project
from django.contrib.auth.hashers import make_password,check_password #hashers  converts passwords to hashcode so that they are safe and increases privacy
from django.shortcuts import render,redirect #from django we import forms that we want to view
from DjangoProject.settings import BASE_DIR
from imgurpython import ImgurClient
from clarifai import rest
from clarifai.rest import ClarifaiApp
from datetime import datetime## datetime module is used to display time
from myapp.key import API_KEY
# sendgrid api is used to send automated emails to users
import sendgrid
 # for this we import api key from api.py
 # due to privacy concern i havent uploaded my apikey
from sendgrid.helpers.mail import*
from myapp.sendgrid_key import SENDGRID_API_KEY
import ctypes



def signup_view(request): #function declaration which is used to show signup page to save the information of new user
  today = datetime.now()
  if request.method == "POST":
      signup_form=SignUpForm(request.POST)#save the details in the database
      if signup_form.is_valid():
          username = signup_form.cleaned_data['username']
          name = signup_form.cleaned_data['name']
          email = signup_form.cleaned_data['email']
          password = signup_form.cleaned_data['password']
          if set('abcdefghijklmnopqrstuvwxyz').intersection(name) and set('abcdefghijklmnopqrstuvwxyz@_1234567890').intersection(username):
              if len(username) > 4 and len(password) > 5:#this is for that username should be greater than 4 and pswrd should be greater then 5
                  user = UserModel(name=name, password=make_password(password), email=email, username=username)
                  user.save() # saves the user information
                  sg = sendgrid.SendGridAPIClient(apikey=(SENDGRID_API_KEY))
                  from_email = Email("samraoaman8@gmail.com")
                  to_email = Email(signup_form.cleaned_data['email'])
                  subject = "Welcome "
                  content = Content("text/plain", "Thank you for signing up ")
                  mail = Mail(from_email, subject, to_email, content)
                  response = sg.client.mail.send.post(request_body=mail.get())
                  print(response.status_code)
                  print(response.body)
                  print(response.headers)
                  ctypes.windll.user32.MessageBoxW(0, u"successfully signed up", u"success", 0)
                  return render(request, 'login.html')
              else:
                  ctypes.windll.user32.MessageBoxW(0, u"invalid enteries. please try again", u"Error", 0)
                  signup_form= SignUpForm()

          else:
              ctypes.windll.user32.MessageBoxW(0, u"invalid name/username", u"error", 0)


  elif request.method == 'GET':
      signup_form= SignUpForm()
  return render(request, 'index.html', { 'date_to_show':today, 'form':signup_form})



def login_view(request): # this funtion is for showing the login page for a user that have an account
    response_data = {} # dictionary
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
                    ctypes.windll.user32.MessageBoxW(0, u"invalid username or password", u"Error", 0)# to show message box
                    response_data['message'] = 'Incorrect Password! Please try again!'
            else:
                ctypes.windll.user32.MessageBoxW(0, u"invalid username/password", u"Error", 0)

    elif request.method == 'GET':
        form = LoginForm()
    response_data['form'] = form
    return render(request, 'login.html', response_data)


def feed_view(request):# feed funtion is used to show posts of the user
    user = check_validation(request)
    if user:
        posts = PostModel.objects.all().order_by('-created_on')
        for post in posts:
            existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
            if existing_like:
                post.has_liked = True

        return render(request, 'feed.html', {'posts': posts})

    else:
        return redirect('/login/')

def post_view(request):# post view funtion is used to upload file or image that you want to add to the feed and also provide funtionality to add caption also
    user = check_validation(request)

    if user:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')
                post = PostModel(user=user, image=image, caption=caption)
                post.save()

                path = str(BASE_DIR + '\\' + post.image.url)

                client = ImgurClient('319feb40023adce', '2a01664decd3b8b2439bfce7caae16d47b671837')
                post.image_url = client.upload_from_path(path, anon=True)['link']
                post.save()

                add_category(post)
                ctypes.windll.user32.MessageBoxW(0, u"post successsfully created", u"SUCCESS", 0)

                return redirect('/feed/')

        else:
            form = PostForm()
        return render(request, 'post.html', {'form': form})
    else:
        return redirect('/login/')




def like_view(request):# this function used for like the post of user and if it is already liked then it unlike thet post
        user = check_validation(request)
        if user and request.method == 'POST':
            form = LikeForm(request.POST)
            if form.is_valid():
                post_id = form.cleaned_data.get('post').id

                existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()
                if not existing_like:
                    like=LikeModel.objects.create(post_id=post_id, user=user)
                    sg = sendgrid.SendGridAPIClient(apikey=(SENDGRID_API_KEY))
                    from_email = Email("samraoaman8@gmail.com")
                    to_email = Email(like.post.user.email)
                    subject = "Welcome"
                    content = Content("text/plain", "someone just liked your post. Go checkout!")
                    mail = Mail(from_email, subject, to_email, content)
                    response = sg.client.mail.send.post(request_body=mail.get())
                    print(response.status_code)
                    print(response.body)
                    print(response.headers)
                    ctypes.windll.user32.MessageBoxW(0, u"liked successfully", u"SUCCESS", 0)
                else:
                    existing_like.delete()
                    ctypes.windll.user32.MessageBoxW(0, u"unlike successfully", u"SUCCESS", 0)

                return redirect('feed/')

        else:
            return redirect('/login/')

def comment_view(request):# this function used for posting comment on the post of the user
    user = check_validation(request)
    if user and request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            comment_text = form.cleaned_data.get('comment_text')
            comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
            comment.save()
            sg = sendgrid.SendGridAPIClient(apikey=(SENDGRID_API_KEY))
            from_email = Email("samraoaman8@gmail.com")
            to_email = Email(comment.post.user.email)
            subject = "Welcome to Review book"
            content = Content("text/plain", "someone just commented on your post. Go check")
            mail = Mail(from_email, subject, to_email, content)
            response = sg.client.mail.send.post(request_body=mail.get())
            print(response.status_code)
            print(response.body)
            print(response.headers)
            ctypes.windll.user32.MessageBoxW(0, u"comment posted successfully", u"SUCCESS", 0)
            return redirect('/feed/    ')
        else:
            return redirect('/feed/')
    else:
        return redirect('/login')

def add_category(post): #this function is used to show the category of the images using clarifai api
    app = ClarifaiApp(api_key=API_KEY)
    model = app.models.get("general-v1.3")
    response = model.predict_by_url(url=post.image_url)

    if response["status"]["code"] == 10000:
        if response["outputs"]:
            if response["outputs"][0]["data"]:
                if response["outputs"][0]["data"]["concepts"]:
                    for index in range(0, len(response["outputs"][0]["data"]["concepts"])):
                        category = CategoryModel(post=post, category_text = response["outputs"][0]["data"]["concepts"][index]["name"])
                        category.save()
                else:
                    print "No Concepts List Error"
            else:
                print "No Data List Error"
        else:
            print "No Outputs List Error"
    else:
        print "Response Code Error"

def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
           return session.user
    else:
        return None

def logout_view(request):   #for logging out the user from the account
    request.session.modified = True
    response = redirect('/login/')
    response.delete_cookie(key='session_token')
    return response

