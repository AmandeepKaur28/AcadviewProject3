from myapp.views import signup_view, login_view, feed_view, post_view,like_view,comment_view,logout_view
from django.conf.urls import url
from django.contrib import admin



urlpatterns = [
    #url(r'^admin/',admin.site.urls),
    url('feed/', feed_view),
    url('logout/', logout_view, name='logout'),
    url('post/', post_view),
    #url('feed/', feed_view),
    url('comment/', comment_view),
    url('like/', like_view),
    url('login/', login_view),
    url('', signup_view),


]