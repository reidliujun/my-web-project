from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic.base import RedirectView

admin.autodiscover()

urlpatterns = patterns('',

    # # url(r'^$', 'website.views.index', name='index'), # album selection view, unless not logged
    
    # url(r'^login/$', 'website.views.log_in', name='login'),
    # url(r'^logout/$', 'website.views.log_out', name='logout'),
    # url(r'^register/$', 'website.views.register', name='register'),
    # # url(r'^album/.{20}$', 'website.views.?', name='?'), # share/collaborate
    # url(r'^admin/', include(admin.site.urls)),
    # url(r'^home/$', 'website.views.home', name='album'),
    # url(r'^home/$', 'website.views.home', name='album'),
    # url(r'^album/$', 'website.views.home', name='album'),
    # url(r'^facebook/', include('django_facebook.urls')),
    # url(r'^accounts/', include('django_facebook.auth_urls')),
    # url(r'^album_form/', 'website.views.album_form', name='album_form'),
    # url(r'^album/(?P<albumtitle>\w+)', 'website.views.albumdetail', name='albumdetail'),

    

    # url(r'^photo/$', 'website.views.list', name='list'),
    # url(r'^order/$', 'website.views.order', name='order'),
    # url(r'^$', RedirectView.as_view(url='/album/')),



    ###add in 30.1.2014
    

    # url(r'^$', 'website.views.index', name='index'), # album selection view, unless not logged
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'website.views.log_in', name='login'),
    url(r'^logout/$', 'website.views.log_out', name='logout'),
    url(r'^register/$', 'website.views.register', name='register'),
    url(r'^facebook/', include('django_facebook.urls')),
    url(r'^accounts/', include('django_facebook.auth_urls')),
    # url(r'^album/.{20}$', 'website.views.?', name='?'), # share/collaborate
    
    url(r'^home/$', 'website.views.home', name='album'),
    url(r'^album/$', 'website.views.home', name='album'),
    
    url(r'^album_form/', 'website.views.album_form', name='album_form'),
    
    url(r'^album/(?P<albumtitle>\w+)/page/(?P<pagenumber>\d{1,3})/layout/(?P<layoutstyle>\d{1})/$', 
        'website.views.photoadd', name='photoadd'),

    url(r'^album/(?P<albumtitle>\w+)/page/(?P<pagenumber>\d{1,3})/layout/$', 
        'website.views.page_layout', name='page_layout'),

    # url(r'^album/page/(?P<albumtitle>\w+)/(?P<pagenumber>\d{1,3})/$', 
    #     'website.views.page_detail', name='page_detail'),
    url(r'^album/(?P<albumtitle>\w+)/page/(?P<pagenumber>\d{1,3})/$', 
        'website.views.page_detail', name='page_detail'),

    url(r'^album/(?P<albumtitle>\w+)/page/(?P<pagenumber>\d{1,3})/delete/', 'website.views.page_delete', name='page_delete'),

    url(r'^album/delete/(?P<albumtitle>\w+)', 'website.views.album_delete', name='album_delete'),
    
    url(r'^album/(?P<albumtitle>\w+)/$', 'website.views.album_page', name='album_page'),

    # url(r'^page/$', 'website.views.page', name='page'),
    url(r'^photo/$', 'website.views.photo', name='photo'),
    url(r'^order/$', 'website.views.order', name='order'),
    url(r'^$', RedirectView.as_view(url='/album/')),
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
