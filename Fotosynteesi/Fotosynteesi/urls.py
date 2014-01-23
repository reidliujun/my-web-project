from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic.base import RedirectView

admin.autodiscover()

urlpatterns = patterns('',
    # url(r'^$', 'website.views.index', name='index'), # album selection view, unless not logged
    
    url(r'^login/$', 'website.views.log_in', name='login'),
    url(r'^logout/$', 'website.views.log_out', name='logout'),
    url(r'^register/$', 'website.views.register', name='register'),
    # url(r'^album/.{20}$', 'website.views.?', name='?'), # share/collaborate
    url(r'^admin/', include(admin.site.urls)),
    url(r'^home/$', 'website.views.list', name='list'),
    url(r'^facebook/', include('django_facebook.urls')),
    url(r'^accounts/', include('django_facebook.auth_urls')),
    url(r'^$', RedirectView.as_view(url='/home/')),
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
