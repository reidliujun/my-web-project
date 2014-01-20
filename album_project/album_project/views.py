from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from album_project.forms import *
from django.conf import settings
from django.views.generic.dates import ArchiveIndexView, DateDetailView, DayArchiveView, MonthArchiveView, YearArchiveView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from .models import *



def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            instance = Photo(image=request.FILES['file'])
            instance.title = instance.image_name()
            instance.title_slug = instance.image_name()
            instance.save()
            return HttpResponseRedirect('upload.html')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})



# def CreateGallery(request):
#     if request.method == 'POST':
#         form = CreateGallery(request.POST)
#         if form.is_valid():
#             instance = Photo(image=request.FILES['file'])
#             instance.title = instance.image_name()
#             instance.title_slug = instance.image_name()
#             instance.save()
#             return HttpResponseRedirect('upload.html')
#     else:
#         form = UploadFileForm()
#     return render(request, 'upload.html', {'form': form})


# Number of galleries to display per page.
GALLERY_PAGINATE_BY = getattr(settings, 'ALBUM_GALLERY_PAGINATE_BY', 20)

# Number of photos to display per page.
PHOTO_PAGINATE_BY = getattr(settings, 'ALBUM_PHOTO_PAGINATE_BY', 20)

# Gallery views.


class GalleryView(object):
    queryset = Gallery.objects.filter(is_public=True)


class GalleryListView(GalleryView, ListView):
    paginate_by = GALLERY_PAGINATE_BY


class GalleryDetailView(GalleryView, DetailView):
    slug_field = 'title_slug'


class GalleryDateView(GalleryView):
    date_field = 'date_added'
    allow_empty = True


class GalleryDateDetailView(GalleryDateView, DateDetailView):
    slug_field = 'title_slug'


class GalleryArchiveIndexView(GalleryDateView, ArchiveIndexView):
    pass


class GalleryDayArchiveView(GalleryDateView, DayArchiveView):
    pass


class GalleryMonthArchiveView(GalleryDateView, MonthArchiveView):
    pass


class GalleryYearArchiveView(GalleryDateView, YearArchiveView):
    pass

# Photo views.


class PhotoView(object):
    queryset = Photo.objects.filter(is_public=True)


class PhotoListView(PhotoView, ListView):
    paginate_by = PHOTO_PAGINATE_BY


class PhotoDetailView(PhotoView, DetailView):
    slug_field = 'title_slug'


class PhotoDateView(PhotoView):
    date_field = 'date_added'
    allow_empty = True


class PhotoDateDetailView(PhotoDateView, DateDetailView):
    slug_field = 'title_slug'


class PhotoArchiveIndexView(PhotoDateView, ArchiveIndexView):
    pass


class PhotoDayArchiveView(PhotoDateView, DayArchiveView):
    pass


class PhotoMonthArchiveView(PhotoDateView, MonthArchiveView):
    pass


class PhotoYearArchiveView(PhotoDateView, YearArchiveView):
    pass

