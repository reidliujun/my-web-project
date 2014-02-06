from django.shortcuts import render, redirect, render_to_response, get_object_or_404, get_list_or_404
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect,  HttpResponseServerError
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods, require_GET
from .forms import *
from .models import *
from django.template import RequestContext
from django.core.urlresolvers import reverse

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max
import datetime
from django_facebook.api import get_persistent_graph, require_persistent_graph
from django_facebook.decorators import facebook_required_lazy, facebook_required
from django_facebook.utils import next_redirect, parse_signed_request
from django.contrib import messages

@login_required
def home(request):
    user = request.user
    msg = "hello %s, this is a test." % user.username
    try:
        albums = Album.objects.filter(user=user)
        # album_titles = [Album.title for Album in Albumi.objects.filter(user=user)]
    except ObjectDoesNotExist:
        albums = None
    return HttpResponse(content=render(request, "album.html", {"albums": albums}))


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
            return HttpResponse(render(request, "login.html",
                {"style": "danger", "message": "This account has been disabled."}),
                                status=410)
    else:
        return HttpResponse(content=render(request, 'login.html', 
            {"style": "danger", "message": "Invalid username or password."}),
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
    return HttpResponse(content=render(request, 'login.html', 
        {"style": "success","message": "You have successfully signed out."}))

# def login
#
# def home(request):
#     if not request.user.is_authenticated():
#         return redirect("/login/?next=%s" % request.path)


# as in https://docs.djangoproject.com/en/dev/topics/http/file-uploads/
from django.db import OperationalError


def photo(request):  # TODO: should be refactored
    # Handle file upload
    # if request.method == 'POST':
    #     # form = ImgForm(request.POST, request.FILES)
    #     # if form.is_valid():
    #         #get the image object
    #     imageList = Image.objects.filter(user=request.user)

    #     # Redirect to the images list after POST
    #     return HttpResponseRedirect(reverse('website.views.list'))

    # Load images for the list page
    try:
        images = Image.objects.filter(user=request.user)
    except OperationalError:
        render_to_response("Serious problem.")

    # Render list page with the images and the form
    return render_to_response(
        'photo.html', {'images': images}, 
        context_instance=RequestContext(request))


# def album(request):
#     albums = Album.objects.filter(user = request.user)
#     # images = Image.objects.filter(album = albums)
#     return render_to_response(
#         'album.html', {'albums': albums}, context_instance=RequestContext(request))


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
        return HttpResponseRedirect(reverse('website.views.home'))
    albums = Album.objects.filter(user=request.user)

    return render_to_response(
        'albumform.html', context_instance=RequestContext(request))


def albumdetail(request, albumtitle):
    albums=get_object_or_404(Album,user=request.user, title=albumtitle)
    if request.method == 'POST':
        form = ImgForm(request.POST, request.FILES)
        if form.is_valid():
            #get the image object
            newimg = Image(imgfile=request.FILES['imgfile'])
            newtitle = request.FILES['imgfile'].name
            newimg.title = newtitle.split('.')[0]
            newimg.save()

            #add user
            user = User.objects.get(username=request.user.username)
            
            newimg.user.add(user)
            newimg.album.add(albums)
            
            # Redirect to the images list after POST
            return HttpResponseRedirect(reverse('website.views.albumdetail', 
                args=albums.title))
    else:
        form = ImgForm()  # A empty, unbound form

    # Load images for the list page
    images = Image.objects.filter(album=albums)
    return render_to_response(
        'albumdetail.html', 
        {'images': images, 'albums': albums, 'form': form}, 
        context_instance=RequestContext(request))


def album_delete(request, albumtitle):
    album = Album.objects.filter(user=request.user, title=albumtitle)
    images = Image.objects.filter(album=album)
    # for image in images:
    images.delete()
    album.delete()
    return HttpResponseRedirect(reverse('website.views.home'))
    

def album_page(request, albumtitle):
    album=get_object_or_404(Album,user=request.user, title=albumtitle)
    pages = Page.objects.filter(album=album)
    if not pages:
        next_page = 1
    else:
        page_number=Page.objects.filter(album=album).aggregate(Max('number'))['number__max']
        next_page = page_number+1
    return render_to_response(
        'album_page.html', {'album': album, 'pages': pages, 'next_page': next_page}, context_instance=RequestContext(request))


def page_layout(request, albumtitle, pagenumber):
    album=get_object_or_404(Album,user=request.user, title=albumtitle)
    page = Page.objects.create(album=album, number=pagenumber, layout=1)


    return render_to_response(
        'page_layout.html', {'album': album, 'page': page}, context_instance=RequestContext(request))


def photoadd(request, albumtitle, pagenumber, layoutstyle):
    album=get_object_or_404(Album,user=request.user, title=albumtitle)
    page=get_object_or_404(Page, album=album, number=pagenumber)
    page.layout = layoutstyle

    if request.method == 'POST':

        #get the image object
        newimg = Image(imgfile = request.FILES['imgfile'])
        newtitle = request.FILES['imgfile'].name
        newimg.title = newtitle.split('.')[0]
        newimg.save()

        #add user
        user = User.objects.get(username=request.user.username)
        newimg.user.add(user)
        newimg.album.add(album)
        newimg.page.add(page)
        # Redirect to the images list after POST
        return HttpResponseRedirect(reverse('website.views.photoadd', 
            kwargs={'albumtitle':album.title, 'pagenumber': page.number, 'layoutstyle':page.layout}))

    images = Image.objects.filter(album=album,page=page)

    return render_to_response(
        'photoadd.html', {'images': images, 'album': album, 'page': page}, 
        context_instance=RequestContext(request))


def page_detail(request, albumtitle, pagenumber):
    album=get_object_or_404(Album,user=request.user, title=albumtitle)
    page = Page.objects.filter(album=album, number=pagenumber)
    images = Image.objects.filter(user=request.user, album=album, page=page)

    return render_to_response(
        'page_detail.html', {'album': album, 'page': page, 'images': images}, context_instance=RequestContext(request))


def page_delete(request, albumtitle, pagenumber):
    album=get_object_or_404(Album,user=request.user, title=albumtitle)
    page = Page.objects.filter(album=album, number=pagenumber)
    images = Image.objects.filter(user=request.user, album=album, page=page)
    images.delete()
    page.delete()
    return HttpResponseRedirect(reverse('website.views.album_page', kwargs={'albumtitle':album.title}))



def album_order(request, albumtitle):
    album=get_object_or_404(Album,user=request.user, title=albumtitle)
    return render_to_response(
        'album_order.html', {'album': album}, context_instance=RequestContext(request))


def order_submit(request, albumtitle):
    album=get_object_or_404(Album,user=request.user, title=albumtitle)
    if request.method == "POST":
        ##set the new order object
        neworder = Order.objects.create(user = request.user, firstname = request.POST.get('firstname', False),
            lastname = request.POST.get('lastname', False), street_address = request.POST.get('street_address', False),
            post_code_and_city = request.POST.get('post_code_and_city', False), country = request.POST.get('country', False), 
            number = request.POST.get('number', False), sid = "group42", album= album)
        # neworder = Order(album = album, user=request.user)

        #set the pid for each independent order
        # neworder.pid= "oktopay"

        neworder.amount = str(10*int(neworder.number))
        #use order_time as pid, then it will be unique to each pid.
        neworder.pid = str(neworder.order_time)
        neworder.checksum = neworder.checksumfunc()
        neworder.success_url = "http://localhost.foo.fi:8000/album/"+album.title+"/paysuccess"
        neworder.cancel_url = "http://localhost.foo.fi:8000/album/"+album.title+"/paycancel"
        neworder.error_url = "http://localhost.foo.fi:8000/album/"+album.title+"/payerror"
        neworder.save()
        return render_to_response(
            'order_submit.html', {'album': album, 'order':neworder}, context_instance=RequestContext(request))
    else:
        return render_to_response(
            'album.html', context_instance=RequestContext(request))

def paysuccess(request, albumtitle):
    pid = request.GET['pid']
    ref = request.GET['ref']
    checksum = request.GET['checksum']

    return render_to_response('paysuccess.html', {'pid':pid, 'ref':ref, 'checksum':checksum},
        context_instance=RequestContext(request))


def paycancel(request, albumtitle):
    return HttpResponse("paycancel")

def payerror(request, albumtitle):
    return HttpResponse("payerror")

def order_detail(request):
    orders = Order.objects.filter(user=request.user)
    return render_to_response('order_detail.html', {'orders':orders}, 
        context_instance=RequestContext(request))


@facebook_required(scope='publish_stream')
@csrf_protect
def facebook_post(request,graph,albumtitle):
    album=get_object_or_404(Album,user=request.user, title=albumtitle)
    message = album.public_url_suffix
    if message:
        graph.set('me/feed', message=message)
        messages.info(request, 'Posted the message to your wall')
        # return next_redirect(request)
        # return HttpResponseRedirect(reverse('album'))
        # return HttpResponseRedirect("post success!")
        return render_to_response('post_succeed.html')
    return HttpResponse("post error")