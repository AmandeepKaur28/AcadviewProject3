# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from myapp.forms import SignUpForm
from myapp.forms import LoginForm ,PostForm,LikeForm,CommentForm
from models import UserModel,SessionToken,PostModel,LikeModel,CommentModel,CategoryModel
from django.contrib.auth.hashers import make_password,check_password
from django.shortcuts import render,redirect
from DjangoProject.settings import BASE_DIR
from imgurpython import ImgurClient
from clarifai import rest
from clarifai.rest import ClarifaiApp
from datetime import datetime
from myapp.key import API_KEY
# sendgrid api is used to send automated emails to users
import sendgrid
 # for this we import api key from api.py
 # due to privacy concern i havent uploaded my apikey
from sendgrid.helpers.mail import*

SENDGRID_API_KEY='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'
# Create your views here.
def signup_view(request):
  today = datetime.now()
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
  return render(request, 'index.html', { 'date_to_show':today, 'form':signup_form})


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
              tags=form.cleaned_data.get('tags')
              {tag.strip(" #") for tag in tags.replace('#', ' #').split() if tag.startswith(" #")}
              post = PostModel(user=user, image=image, caption=caption,tags=tags)
              post.save()

              path = str(BASE_DIR + post.image.url)

              client = ImgurClient('319feb40023adce', '2a01664decd3b8b2439bfce7caae16d47b671837')
              post.image_url = client.upload_from_path(path, anon=True)['link']
              post.save()
              add_category(post)

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
                else:
                    existing_like.delete()

                return redirect('feed/')

        else:
            return redirect('/login/')

def comment_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            comment_text = form.cleaned_data.get('comment_text')
            comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
            comment.save()
            return redirect('/feed/    ')
        else:
            return redirect('/feed/')
    else:
        return redirect('/login')



def add_category(post):
    app = ClarifaiApp(api_key=API_KEY)
    model = app.models.get("general-v1.3")
    response = model.predict_by_url(url=post.image_url)


    # Logo model
    #model = app.models.get('logo')

    #response = model.predict_by_url(url=post.image_url)

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

#def workout(request, genre=None):
    #if not request.is_login():
        #return render(request,'/login/')
    #else:
        #posts=PostModel.objects.filter('workout'in genre)
        







def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
           return session.user
    else:
        return None

def logout_view(request):   #for logging out the user
    request.session.modified = True
    response = redirect('/login/')
    response.delete_cookie(key='session_token')
    return response