#from views we import pages which we are giving url to
from myapp.views import signup_view, login_view, feed_view, post_view,like_view,comment_view,logout_view
# we create urls in django in url.py file
# for this we have to import urls from django.conf.url

from django.conf.urls import url
from django.contrib import admin

# there are the pattenrs which we use to create url for a particular page
# r is the regular expression



urlpatterns = [
    #url(r'^admin/',admin.site.urls),
    url('feed/', feed_view),
    url('logout/', logout_view, name='logout'),
    url('post/', post_view),

    url('comment/', comment_view),
    url('like/', like_view),
    url('login/', login_view),
    url('', signup_view),


]