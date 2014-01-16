from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from example_project.forms import *
from photologue.models import *



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