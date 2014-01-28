from django.shortcuts import render, redirect, render_to_response
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods, require_GET
from .forms import *
from .models import *
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from models import Album as Albumi
@login_required
def index(request):
    user = request.user
    msg = "hello %s, this is a test." % user.username
    album_objects = Albumi.objects.get(user=user)
    album_titles = [Album.title for Album in album_objects]
    return HttpResponse("albums.html", album_titles)


def home(request):
    return render_to_response('home.html', context_instance=RequestContext(request))

def order(request):
    return render_to_response('order.html', context_instance=RequestContext(request))


def create_user(request):
    username = request.POST['username']
    password = request.POST['password']
    retyped_password = request.POST['retypedPassword']
    if password != retyped_password:
        return HttpResponse(render_to_response("register.html", {"style": "danger",
                                                                 "message": "Passwords do not match."}))
    else:
        try:
            user = User.objects.create_user(username=username, password=password)
            return log_user_in(request)
        except IntegrityError:
            return HttpResponse(render_to_response("register.html", {"style": "danger",
                                                                     "message": "Chosen username is not available."}))


# as in https://docs.djangoproject.com/en/1.6/topics/auth/default/
def log_user_in(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            # return redirect('/list/')
            return HttpResponseRedirect(reverse('website.views.home'))
        else:
            return HttpResponse(render(request, "login.html", {"style": "danger",
                                                               "message": "This account has been disabled."}),
                                status=410)
    else:
        return HttpResponse(content=render(request, 'login.html', {"style": "danger",
                                                                   "message": "Invalid username or password."}),
                            status=401)


@require_http_methods(['GET', 'POST'])
def register(request):
    if request.method == 'POST':
        return create_user(request)
    elif request.method == 'GET':
        return HttpResponse(render_to_response('register.html'))


@require_http_methods(['GET', 'POST'])
def log_in(request):
    if request.user.is_authenticated():
        return redirect('/home/')
    elif request.method == 'POST':
        return log_user_in(request)
    else:
        return HttpResponse(render_to_response('login.html'))


@require_GET
def log_out(request):
    logout(request)
    return HttpResponse(content=render(request, 'login.html', {"style": "success",
                                                               "message": "You have successfully signed out."}))

# def login
#
# def home(request):
#     if not request.user.is_authenticated():
#         return redirect("/login/?next=%s" % request.path)

# as in https://docs.djangoproject.com/en/dev/topics/http/file-uploads/
def list(request):
    # Handle file upload
    # if request.method == 'POST':
    #     # form = ImgForm(request.POST, request.FILES)
    #     # if form.is_valid():
    #         #get the image object
    #     imageList = Image.objects.filter(user=request.user)

    #     # Redirect to the images list after POST
    #     return HttpResponseRedirect(reverse('website.views.list'))

    # Load images for the list page
    images = Image.objects.filter(user=request.user)

    # Render list page with the images and the form
    return render_to_response(
        'list.html', {'images': images}, context_instance=RequestContext(request))


def album(request):
    albums = Album.objects.filter(user = request.user)
    # images = Image.objects.filter(album = albums)
    return render_to_response(
        'album.html', {'albums': albums}, context_instance=RequestContext(request))


def album_form(request):
    if request.method == 'POST':
        #get the album object
        newalbum = Album(title = request.POST['title'])
        newalbum.public_url_suffix = 'http://www.google.com'
        newalbum.collaboration_url_suffix = 'http://www.google.com'
        
        #get the user object
        newalbum.save()
        user = User.objects.get(username=request.user.username)
        newalbum.user.add(user)
        return HttpResponseRedirect(reverse('website.views.album_form'))
    albums = Album.objects.filter(user=request.user)

    return render_to_response(
        'albumform.html',{'albums': albums}, context_instance=RequestContext(request))


def albumdetail(request, albumtitle):
    albums = Album.objects.get(user=request.user, title=albumtitle)
    if request.method == 'POST':
        form = ImgForm(request.POST, request.FILES)
        if form.is_valid():
            #get the image object
            newimg = Image(imgfile = request.FILES['imgfile'])
            newtitle = request.FILES['imgfile'].name
            newimg.title = newtitle.split('.')[0]
            newimg.save()

            #add user
            user = User.objects.get(username=request.user.username)
            
            newimg.user.add(user)
            newimg.album.add(albums)
            
            # Redirect to the images list after POST
            return HttpResponseRedirect(reverse('website.views.albumdetail', args=(albums.title)))
    else:
        form = ImgForm() # A empty, unbound form

    # Load images for the list page
    images = Image.objects.filter(album=albums)
    return render_to_response(
        'albumdetail.html', {'images': images, 'albums': albums, 'form': form}, context_instance=RequestContext(request))