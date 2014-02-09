#!/usr/bin/env python
# coding: utf8

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




def home(request):
    if request.user.is_authenticated():
        return render_to_response("album.html", context_instance=RequestContext(request))
    else:
        return render_to_response("home.html")

def about(request):
    return render_to_response("about.html", context_instance=RequestContext(request))

@login_required
def album(request):
    """Docstring goes here. """
    user = request.user
    msg = "hello %s, this is a test." % user.username
    try:
        albums = Album.objects.filter(user=user)
    except ObjectDoesNotExist:
        albums = None
    template = "album.html"
    params = {"albums": albums}
    return HttpResponse(content=render(request, template, params))


def order(request):
    """Appears deprecated. """

    template = "order.html"
    return render(request, template)


def create_user(request):
    """Docstring goes here. """
    username = request.POST['username']
    password = request.POST['password']
    retyped_password = request.POST['retypedPassword']
    if password != retyped_password:
        template = "register.html"
        params = {"style": "danger",
                  "message": "Passwords do not match."}
        return HttpResponse(render_to_response(template, params))
    else:
        try:
            # only to check for availability
            u = User.objects.create_user(username=username, password=password)
            return log_user_in(request)
        except IntegrityError:
            template = "register.html"
            params = {"style": "danger",
                      "message": "Chosen username is not available."}
            return HttpResponse(render(request, template, params))


# as in https://docs.djangoproject.com/en/1.6/topics/auth/default/
def log_user_in(request):
    """Attempts to sign the user in with the credentials they have provided.
    Returns the user back to the sign in page and displays an appropriate
    warning if the sign in is unsuccessful.
    """

    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    template = "login.html"
    if user is not None:
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect(reverse('website.views.album'))
        else:
            params = {"style": "danger",
                      "message": "This account has been disabled."}
            page = render(request, template, params)
            return HttpResponse(content=page, status=410)
    else:
        params = {"style": "danger",
                  "message": "Invalid username and/or password."}
        page = render(request, template, params)
        return HttpResponse(content=page, status=401)


@require_http_methods(['GET', 'POST'])
def register(request):
    """On POST -> create_user view. On GET -> registration page. """

    if request.method == 'POST':
        return create_user(request)
    elif request.method == 'GET':
        template = "register.html"
        return HttpResponse(render_to_response(template))


@require_http_methods(['GET', 'POST'])
def log_in(request):
    """Chooses action based on http method and user authentication.

    Authenticated user -> Album view
    Post method -> Login view
    Get method -> Login page

    """

    if request.user.is_authenticated():
        return redirect('/album/')  # TODO: /home/ vs. /album/, remove one
    elif request.method == 'POST':
        return log_user_in(request)
    else:
        template = "login.html"
        return HttpResponse(render_to_response(template))


@require_GET
def log_out(request):
    """Signs user out, or tells them that they are already signed out. """

    template = "login.html"
    if request.user.is_authenticated():
        logout(request)
        params = {"style": "success",
                  "message": "You have successfully signed out."}
    else:
        params = {"style": "info",
                  "message": "You were not signed in."}
    return HttpResponse(content=render(request, template, params))

# def login
#
# def home(request):
#     if not request.user.is_authenticated():
#         return redirect("/login/?next=%s" % request.path)


# as in https://docs.djangoproject.com/en/dev/topics/http/file-uploads/
from django.db import OperationalError


def account(request):
    return render_to_response("account.html", context_instance=RequestContext(request))


def photo(request):  # TODO: should be refactored
    """Docstring goes here. """

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
        first_id=100000
        if images:
            images_order = images.values().order_by('id')
            first_id = images_order.first()['id']
    except OperationalError:
        render_to_response("Serious problem.")

    # Render list page with the images and the form
    template = "photo.html"
    params = {'images': images,"var": first_id}
    return render(request, template, params)

# def album(request):
#     albums = Album.objects.filter(user = request.user)
#     # images = Image.objects.filter(album = albums)
#     return render_to_response(
#         'album.html', {'albums': albums}, context_instance=RequestContext(request))


def album_form(request):
    """Docstring goes here. """
    if request.method == 'POST':
        #get the album object
        if " " in request.POST['title']:
            title_array=request.POST['title'].split(" ")
            mytitle="_".join(title_array)
            newalbum = Album(title = mytitle)
        else:
            newalbum = Album(title = request.POST['title'])
        ## use for local test
        newalbum.public_url_suffix = "http://localhost.foo.fi:8000/public/"+request.user.username+"_"+newalbum.title
        ## use on heroku
        #newalbum.public_url_suffix = "http://fotosynteesi.herokuapp.com/public/"+request.user.username+"_"+newalbum.title
        newalbum.collaboration_url_suffix = 'google.com'
        
        #get the user object
        newalbum.save()
        user = User.objects.get(username=request.user.username)
        newalbum.user.add(user)
        return HttpResponseRedirect(reverse('website.views.album'))
    albums = Album.objects.filter(user=request.user)

    template = "albumform.html"
    return render(request, template)


def albumdetail(request, albumtitle):
    """ Docstring goes here. """

    albums = get_object_or_404(Album, user=request.user, title=albumtitle)
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
            redirect_path = reverse('website.views.albumdetail')
            params = albums.title
            return HttpResponseRedirect(redirect_path, args=params)
    else:
        form = ImgForm()  # A empty, unbound form

    # Load images for the list page
    images = Image.objects.filter(album=albums)

    template = "albumdetail.html"
    params = {'images': images, 'albums': albums, 'form': form}
    return render(request, template, params)


def album_delete(request, albumtitle):
    """ Docstring goes here. """
    album = Album.objects.filter(user=request.user, title=albumtitle)
    images = Image.objects.filter(album=album)
    # for image in images:
    images.delete()
    album.delete()

    return HttpResponseRedirect(reverse('website.views.album'))
    

def album_page(request, albumtitle):
    """ Docstring goes here. """
    album = get_object_or_404(Album,user=request.user, title=albumtitle)
    pages = Page.objects.filter(album=album)
    if not pages:
        next_page = 1
    else:
        page_objects = Page.objects.filter(album=album)
        page_number = page_objects.aggregate(Max('number'))['number__max']
        next_page = page_number + 1

    template = "album_page.html"
    params = {'album': album, 'pages': pages, 'next_page': next_page}
    return render(request, template, params)


def page_layout(request, albumtitle, pagenumber):
    """ Docstring goes here. """
    album = get_object_or_404(Album, user=request.user, title=albumtitle)
    alb_page = Page.objects.create(album=album, number=pagenumber, layout=1)

    template = "page_layout.html"
    params = {'album': album, 'page': alb_page}
    return render(request, template, params)


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
    """Docstring goes here. """
    album = get_object_or_404(Album, user=request.user, title=albumtitle)
    page = Page.objects.filter(album=album, number=pagenumber)
    images = Image.objects.filter(user=request.user, album=album, page=page)

    template = "page_detail.html"
    params = {'album': album, 'page': page, 'images': images}
    return render(request, template, params)


def page_delete(request, albumtitle, pagenumber):
    """Docstring goes here. """
    album = get_object_or_404(Album, user=request.user, title=albumtitle)
    page = Page.objects.filter(album=album, number=pagenumber)
    images = Image.objects.filter(user=request.user, album=album, page=page)
    images.delete()
    page.delete()
    viewname = 'website.views.album_page', "kwargs={'albumtitle':album.title}"

    return HttpResponseRedirect(reverse(viewname))


def album_order(request, albumtitle):
    """Docstring goes here. """

    album = get_object_or_404(Album,user=request.user, title=albumtitle)

    template = "album_order.html"
    params = {'album': album}
    return render(request, template, params)


def order_submit(request, albumtitle):
    """Docstring goes here. """

    album = get_object_or_404(Album, user=request.user, title=albumtitle)
    if request.method == "POST":
        # set the new order object
        neworder = Order.objects.create(
            user=request.user,
            firstname=request.POST.get('firstname', False),
            lastname=request.POST.get('lastname', False),
            street_address=request.POST.get('street_address', False),
            post_code_and_city=request.POST.get('post_code_and_city', False),
            country=request.POST.get('country', False),
            item_count=request.POST.get('item_count', False),
            sid="group42",
            album=album)
        # neworder = Order(album = album, user=request.user)

        #set the pid for each independent order
        # neworder.pid= "oktopay"

        neworder.total_cost = str(10*int(neworder.item_count))
        #use time_placed as pid, then it will be unique to each pid.
        neworder.pid = str(neworder.time_placed)
        neworder.checksum = neworder.checksumfunc()
        ## TODO: uncomment the following when deployed on heroku
        #neworder.success_url = "http://fotosynteesi.herokuapp.com/album/"
        #neworder.cancel_url = "http://fotosynteesi.herokuapp.com/album/"+album.title+"/paycancel"
        #neworder.error_url = "http://fotosynteesi.herokuapp.com/album/"+album.title+"/payerror"
        
        ## TODO: comment the following when deployed on heroku
        neworder.success_url = "http://localhost.foo.fi:8000/album/"
        neworder.cancel_url = "http://localhost.foo.fi:8000/album/"+album.title+"/paycancel"
        neworder.error_url = "http://localhost.foo.fi:8000/album/"+album.title+"/payerror"
        neworder.save()

        template = "order_submit.html"
        params = {'album': album, 'order': neworder}
    else:
        template = "album.html"
        params = {}

    return render(request, template, params)


def paysuccess(request, albumtitle):
    """Docstring goes here. """
    pid = request.GET['pid']
    ref = request.GET['ref']
    checksum = request.GET['checksum']

    template = "paysuccess.html"
    params = {'pid': pid, 'ref': ref, 'checksum': checksum}

    return render(request, template, params)


def paycancel(request, albumtitle):
    """Docstring goes here. """

    return HttpResponse("paycancel")


def payerror(request, albumtitle):
    """Docstring goes here. """

    return HttpResponse("payerror")


def order_detail(request):
    """Docstring goes here. """

    orders = Order.objects.filter(user=request.user)
    params = {'orders': orders}

    template = "order_detail.html"
    return render(request, template, params)


@facebook_required(scope='publish_stream')
@csrf_protect
def facebook_post(request, graph, albumtitle):
    """Docstring goes here. """

    album = get_object_or_404(Album, user=request.user, title=albumtitle)
    message = album.public_url_suffix
    if message:
        graph.set('me/feed', message=message)
        messages.info(request, 'Posted the message to your wall.')
        # return next_redirect(request)
        # return HttpResponseRedirect(reverse('album'))
        # return HttpResponseRedirect("post success!")

        template = "post_succeed.html"

        return render_to_response(template)

    return HttpResponse("post error")


def publicalbum(request, albumurl):
    """Docstring goes here. """

    # FIXME: suffix should be a suffix, read below
    # url formation should look something like this:
    # http://domain.tld[:port]/user/album/suffix
    # suffix should look something like this: t7E5UEqsjgxFjjFRXw7h
    # public url: http://domain.tld[:port]/user/album/t7E5UEqsjgxFjjFRXw7h

    my_public_url_suffix = "http://localhost.foo.fi:8000/public/"+albumurl
    album = get_object_or_404(Album,public_url_suffix=my_public_url_suffix)
    pages = Page.objects.filter(album=album)

    template = "public_album.html"
    params = {'pages': pages, 'url':albumurl}

    return render_to_response(template, params)

def publicpage(request,albumurl,pagenumber):
    my_public_url_suffix = "http://localhost.foo.fi:8000/public/"+albumurl
    album = get_object_or_404(Album,public_url_suffix=my_public_url_suffix)
    page = Page.objects.filter(album=album, number=pagenumber)
    images = Image.objects.filter(album=album, page=page)

    return render_to_response(
        'public_page.html', {'album': album, 'page': page, 'images': images})