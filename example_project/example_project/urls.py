from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.generic import CreateView
from photologue.models import Photo
from example_project.forms import *
from example_project.views import *
from django_facebook.views import *
admin.autodiscover()

# urlpatterns = patterns(
#     'django_facebook.views',
#     url(r'^connect/$', 'connect', name='facebook_connect'),
#     url(r'^disconnect/$',
#         'disconnect', name='facebook_disconnect'),
# )

urlpatterns = patterns('',
    (r'^facebook/', include('django_facebook.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^photologue/', include('photologue.urls')),
    url(r'^photologue/photo/add/$', CreateView.as_view(model=Photo),
        name='add-photo'),
    url(r'^upload_file/', upload_file),
    url(r'^$', TemplateView.as_view(template_name="homepage.html"), name='homepage'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

