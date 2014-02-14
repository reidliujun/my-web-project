from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy
from django.contrib import admin
from django.views.generic import TemplateView
from django.conf.urls.static import static
from .views import *
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'album_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', TemplateView.as_view(template_name="homepage.html"), name='homepage'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^upload_file/', upload_file),
    url(r'^gallery/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[\-\d\w]+)/$',
        GalleryDateDetailView.as_view(),
        name='al-gallery-detail'),
    url(r'^gallery/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$',
        GalleryDayArchiveView.as_view(),
        name='al-gallery-archive-day'),
    url(r'^gallery/(?P<year>\d{4})/(?P<month>[a-z]{3})/$',
        GalleryMonthArchiveView.as_view(),
        name='al-gallery-archive-month'),
    url(r'^gallery/(?P<year>\d{4})/$',
        GalleryYearArchiveView.as_view(),
        name='al-gallery-archive-year'),
    url(r'^gallery/$',
        GalleryArchiveIndexView.as_view(),
        name='al-gallery-archive'),
    url(r'^$',
        RedirectView.as_view(url=reverse_lazy('al-gallery-archive')),
        name='al-album-root'),
    url(r'^gallery/(?P<slug>[\-\d\w]+)/$', GalleryDetailView.as_view() , name='al-gallery'),
    url(r'^gallery/page/(?P<page>[0-9]+)/$', GalleryListView.as_view(), name='al-gallery-list'),

    url(r'^photo/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[\-\d\w]+)/$',
        PhotoDateDetailView.as_view(),
        name='al-photo-detail'),
    url(r'^photo/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$',
        PhotoDayArchiveView.as_view(),
        name='al-photo-archive-day'),
    url(r'^photo/(?P<year>\d{4})/(?P<month>[a-z]{3})/$',
        PhotoMonthArchiveView.as_view(),
        name='al-photo-archive-month'),
    url(r'^photo/(?P<year>\d{4})/$',
        PhotoYearArchiveView.as_view(),
        name='al-photo-archive-year'),
    url(r'^photo/$',
        PhotoArchiveIndexView.as_view(),
        name='al-photo-archive'),

    url(r'^photo/(?P<slug>[\-\d\w]+)/$',
        PhotoDetailView.as_view(),
        name='al-photo'),
    url(r'^photo/page/(?P<page>[0-9]+)/$',
        PhotoListView.as_view(),
        name='al-photo-list'),
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
