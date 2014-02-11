from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic.base import RedirectView

admin.autodiscover()

urlpatterns = patterns('',
    # url(r'^$', 'website.views.index', name='index'), # album selection view, unless not logged
    url(r'^admin/', include(admin.site.urls)),


    url(r'^login/$', 'website.views.log_in', name='login'),
    url(r'^logout/$', 'website.views.log_out', name='logout'),
    url(r'^register/$', 'website.views.register', name='register'),
    url(r'^facebook/', include('django_facebook.urls')),
    url(r'^accounts/', include('django_facebook.auth_urls')),
    # url(r'^album/.{20}$', 'website.views.?', name='?'), # share/collaborate

    url(r'^home/$', 'website.views.home', name='home'),
    #url(r'^home/$', 'website.views.home', name='album'),

    url(r'^album_form/', 'website.views.album_form', name='album_form'),

    url(r'^public/(?P<albumurl>\w+)/$', 'website.views.publicalbum', name='publicalbum'),
    url(r'^public/(?P<albumurl>\w+)/(?P<pagenumber>\d{1,3})/$', 'website.views.publicpage', name='publicpage'),


    url(r'^album/(?P<albumtitle>\w+)/page/(?P<pagenumber>\d{1,3})/layout/(?P<layoutstyle>\d{1})/$',
        'website.views.photoadd', name='photoadd'),

    # (Album List View):
    # Displays to the user a list of their albums. This is f.ex.
    # triggered when clicking "ALBUMS" tab item in the navigation bar.
    # FIXME: Should be ^user/album/$
    url(r'^album/$', 'website.views.album', name='Album List View'),
    # This also triggers when a logged in user attempts to access root dir.
    url(r'^$', RedirectView.as_view(url='/album/')),

    # (Single Album View:)
    #  Available upon clicking a specific album in (Album List View)
    url(r'^album/(?P<album_title>\w+)/$',
        'website.views.single_album_view', name='Single Album View'),

    # (Single Page View):
    #  Available upon clicking a page in album view.
    # FIXME: There's currently nothing useful to where this leads.
    url(r'^album/(?P<album_title>\w+)/page/(?P<page_number>\d{1,3})/$',
        'website.views.single_page_view', name='Single Page View'),

    # (Add New Page):
    url(r'^album/(?P<album_title>\w+)/(?P<action>)\w+/$',
        'website.views.add_new_page'),

    # (Layout Selection View):
    #  Available upon clicking "add page" in (Single album view).
    # TODO: Should be available from (Page view), as well.
    url(r'^album/(?P<albumtitle>\w+)/page/(?P<pagenumber>\d{1,3})/layout/$',
        'website.views.select_page_layout', name='Layout Selection View'),

    url(r'^album/(?P<albumtitle>\w+)/page/(?P<pagenumber>\d{1,3})/delete/', 'website.views.page_delete', name='page_delete'),

    url(r'^album/delete/(?P<albumtitle>\w+)', 'website.views.album_delete', name='album_delete'),

    url(r'^album/(?P<albumtitle>\w+)/order/$', 'website.views.album_order', name='album_order'),

    url(r'^album/(?P<albumtitle>\w+)/submit/$', 'website.views.order_submit', name='order_submit'),
    url(r'^album/(?P<albumtitle>\w+)/paysuccess$', 'website.views.paysuccess', name='paysuccess'),
    url(r'^album/(?P<albumtitle>\w+)/paycancel$', 'website.views.paycancel', name='paycancel'),
    url(r'^album/(?P<albumtitle>\w+)/payerror$', 'website.views.payerror', name='payerror'),

    # url(r'^page/$', 'website.views.page', name='page'),
    url(r'^photo/$', 'website.views.photo', name='photo'),
    url(r'^order/$', 'website.views.order_detail', name='order_detail'),
    url(r'^about/$', 'website.views.about', name='about'),
    url(r'^account/$', 'website.views.account', name='account'),
    # url(r'^$', RedirectView.as_view(url='/home/')),
    url(r'^facebook_post/(?P<albumtitle>\w+)/$', 'website.views.facebook_post', name='facebook_post'),

    # TODO: static.static() function not intended for deployment, read below
    # link to docs: https://docs.djangoproject.com/en/1.6/ref/urls/
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
