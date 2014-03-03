from django.conf.urls import patterns,url,include

urlpatterns = patterns('demo.views',    
    (r'^$','main'),
    (r'^feedly/',include('feedly.urls')),
)