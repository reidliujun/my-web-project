#!/usr/bin/env python
# coding: utf8

from django.shortcuts import render, redirect, render_to_response, get_object_or_404, get_list_or_404
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect,  HttpResponseServerError, Http404
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
from django.core import serializers
from django.utils import simplejson
from django.db import OperationalError

# Note: Never use 301 (it cannot be undone).
CODE = {
    'OK': 200,
    'Unauthorized': 401,            # User needs to authenticate
    'Forbidden': 403,               # Regardless of authentication status
    'Method Not Allowed': 405,      # HTTP methods (GET, etc.)
    'Internal Server Error': 500,   # Generic error
}


def home(request):
    if request.user.is_authenticated():
        return render_to_response("album.html", context_instance=RequestContext(request))
    else:
        return render_to_response("home.html")


def about(request):
    return render_to_response("about.html", context_instance=RequestContext(request))


@login_required
def album(request):
    """The album page show all the albums list 
    with request user filter in database.

    """
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
    """Creates a user using the 'django.contrib.auth' system.
    See https://docs.djangoproject.com/en/dev/topics/auth/ for more details.

    """
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
    """Order the images of one user by id, and show the photo on webpage slide
    form.

    """
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
    params = {'images': images,"var": first_id}  # TODO: What if not images?
    return render(request, template, params)

# def album(request):
#     albums = Album.objects.filter(user = request.user)
#     # images = Image.objects.filter(album = albums)
#     return render_to_response(
#         'album.html', {'albums': albums}, context_instance=RequestContext(request))


def album_form(request):
    """Input the album title, when 'POST', create the new album. """

    '''Simple ajax deal with the album title conflict issue. '''
    message = {"status": ""}
    template = "albumform.html"
    params = {'message': 'Album already have, choose another title!'} 

    if request.is_ajax():
        mytitle = request.POST['title_string']
        if not Album.objects.filter(user=request.user, title_string=mytitle):
            message["status"] = "OK to create"
        else:
            message["status"] = "fail to create"
        '''Provide message to html page as json. '''
        json = simplejson.dumps(message)
        return HttpResponse(json, content_type='application/json')

    if request.method == 'POST':
        mytitle = request.POST['title']
        if not Album.objects.filter(user=request.user, title_string=mytitle):
            newalbum = Album(user=request.user, title_string=mytitle)
        else:
            return render(request, template, params)

        #get the user object
        newalbum.save()
        return HttpResponseRedirect(reverse('website.views.album'))
    albums = Album.objects.filter(user=request.user)
    return render(request, template)


def albumdetail(request, albumtitle):
    """Not been used in the url, can be deleted. """

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
    """Delete the album with the albumtitle and redirect to 'album' page. """
    album_obj = Album.objects.filter(user=request.user, title=albumtitle)
    images = Image.objects.filter(album=album_obj)
    # for image in images:
    images.delete()  # FIXME: This is wrong, images are not deleted
    album_obj.delete()  # TODO: Realistically, albums shouldn't be either immediatl

    return HttpResponseRedirect(reverse('website.views.album'))
    

def single_album_view(request, title_slug):
    """Show the page detail inside one chosen album with its title. """
    album_obj = get_object_or_404(Album, title_slug=title_slug)

    if request.user == album_obj.user:
        access_right = 'owner'
    # elif request.user in album_obj.collaborators:
    #     access_right = 'collaborator'
    # elif request.REQUEST['collaborator_url_suffix'] == album_obj.collaboration_url_suffix:
    #     album_obj.collaborators = request.user
    #     access_right = 'collaborator'
    # elif request.REQUEST['public_url_suffix'] == album_obj.public_url_suffix:
    #     access_right = 'guest'
    else:
        return HttpResponse(status=CODE["Unauthorized"])

    template = "single_album_view.html"
    params = {'album_obj': album_obj, 'access_right': access_right}
    return render(request, template, params)


def single_page_view(request, title_slug, page_number):

    album_obj = Album.objects.get(title_slug=title_slug)  # TODO: rights
    page_obj = Page.objects.get(album=album_obj, number=page_number)

    template = "page_detail.html"
    params = {'page_obj': page_obj, 'album_title': title_slug}
    return render(request, template, params)


def add_new_page(request, album_obj):
    # album_obj = get_object_or_404(Album, user=request.user, title=album_title)
    new_page = Page.objects.create(album=album_obj)
    first_free_page_number = new_page.get_last() + 1
    album_obj.add_page(new_page, None)

    if new_page.number.__class__ is None:
        raise TypeError("Page number of new page is not an int.")

    return select_page_layout(request, new_page)


def select_page_layout(request, page_obj):
    """Allows user to select a new layout for a page. """
    # album_obj = get_object_or_404(Album, user=request.user, title=albumtitle)
    # alb_page = Page.objects.get(id=page_id)

    template = "select_page_layout.html"
    params = {'album': page_obj.album, 'page': page_obj}
    return render(request, template, params)


def photoadd(request, albumtitle, pagenumber, layoutstyle):
    '''Add photo by using 'file' type of input tag, 
    and the photo is added according to the album, page as well as user.'''

    album=get_object_or_404(Album,user=request.user, title=albumtitle)
    page=get_object_or_404(Page, album=album, number=pagenumber)
    page.layout = layoutstyle
    message = {"status":""}
    images=Image.objects.filter(user=request.user)
    if request.is_ajax():
        if request.POST['setting']=='set':
            if Image.objects.filter(user=request.user, title=request.POST['title']):
                message["status"]="get the image!"
                setimg=Image.objects.get(user=request.user, title=request.POST['title'])
                setimg.album.add(album)
                setimg.page.add(page)
            else:
                message["status"]="no image!"
                return HttpResponse("error get the image")
        else:
            if Image.objects.filter(user=request.user, title=request.POST['title']):
                message["status"]="get the image!"
                setimg=Image.objects.get(user=request.user, title=request.POST['title'])
                # setimg.album.remove(album)
                # setimg.page.remove(page)
            else:
                message["status"]="no image!"
                return HttpResponse("error get the image")

        json = simplejson.dumps(message)
        return HttpResponse(json, content_type = 'application/json')

    # if request.method == 'POST':

    #     #get the image object
    #     newimg = Image(imgfile = request.FILES['imgfile'])
    #     newtitle = request.FILES['imgfile'].name
    #     newimg.title = newtitle.split('.')[0]
    #     newimg.save()

    #     #add user
    #     user = User.objects.get(username=request.user.username)
    #     newimg.user.add(user)
    #     newimg.album.add(album)
    #     newimg.page.add(page)
    #     # Redirect to the images list after POST
    #     return HttpResponseRedirect(reverse('website.views.photoadd', 
    #         kwargs={'albumtitle':album.title, 'pagenumber': page.number, 'layoutstyle':page.layout}))

    # images = Image.objects.filter(album=album,page=page)
    
    return render_to_response(
        'photoadd.html', {'images': images, 'album': album_obj, 'page': page},
        context_instance=RequestContext(request))


# def page_detail(request, albumtitle, pagenumber):
#     """Show the page with its photo in the webpage. """
#     album_obj = get_object_or_404(Album, user=request.user, title=albumtitle)
#     page = Page.objects.filter(album=album_obj, number=pagenumber)
#     images = Image.objects.filter(user=request.user, album=album_obj, page=page)

    # template = "page_detail.html"
    # params = {'album': album_obj, 'page': page, 'images': images}
    # return render(request, template, params)


def page_delete(request, albumtitle, pagenumber):
    """Delete the selected page. """
    album_obj = get_object_or_404(Album, user=request.user, title=albumtitle)
    page = Page.objects.filter(album=album_obj, number=pagenumber)
    images = Image.objects.filter(user=request.user, album=album_obj, page=page)
    images.delete()
    page.delete()
    viewname = 'website.views.single_album_view', "kwargs={'albumtitle':album.title}"

    return HttpResponseRedirect(reverse(viewname))


def album_order(request, albumtitle):
    """Order the album by filling a order form. """

    album_obj = get_object_or_404(Album,user=request.user, title=albumtitle)

    template = "album_order.html"
    params = {'album': album_obj}
    return render(request, template, params)


def order_submit(request, albumtitle):
    """Submit the order to the order system.

    Required keywords for the system:
    sid --
    pid --
    redirect_url --
    amount --

    """

    album_obj = get_object_or_404(Album, user=request.user, title=albumtitle)
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
            album=album_obj)
        # neworder = Order(album = album, user=request.user)

        #set the pid for each independent order
        # neworder.pid= "oktopay"

        neworder.total_cost = str(10*int(neworder.item_count))
        #use time_placed as pid, then it will be unique to each pid.
        neworder.pid = str(neworder.time_placed)
        neworder.checksum = neworder.generate_checksum()

        # FIXME: No hard-coding urls!
        #neworder.success_url = "http://fotosynteesi.herokuapp.com/album/"
        #neworder.cancel_url = "http://fotosynteesi.herokuapp.com/album/"+album.title+"/paycancel"
        #neworder.error_url = "http://fotosynteesi.herokuapp.com/album/"+album.title+"/payerror"
        
        # FIXME: No hard-coding urls!
        neworder.success_url = "http://localhost.foo.fi:8000/album/"
        neworder.cancel_url = "http://localhost.foo.fi:8000/album/"+album_obj.title+"/paycancel"
        neworder.error_url = "http://localhost.foo.fi:8000/album/"+album_obj.title+"/payerror"

        neworder.save()

        template = "order_submit.html"
        params = {'album': album_obj, 'order': neworder}
    else:
        template = "album.html"
        params = {}

    return render(request, template, params)


def paysuccess(request, albumtitle):
    """If pay success, redirect to the paysuccess page. """
    pid = request.GET['pid']
    ref = request.GET['ref']
    checksum = request.GET['checksum']

    template = "paysuccess.html"
    params = {'pid': pid, 'ref': ref, 'checksum': checksum}

    return render(request, template, params)


def paycancel(request, albumtitle):
    """Pay cancel.

    Note: when click cancel in the order system, the order still there need to
    be deleted in the future. """

    return HttpResponse("paycancel")


def payerror(request, albumtitle):
    """Pay error, same as paycancel. """

    return HttpResponse("payerror")


def order_detail(request):
    """Give the order lists with details of a user. """

    orders = Order.objects.filter(user=request.user)
    params = {'orders': orders}

    template = "order_detail.html"
    return render(request, template, params)


@facebook_required(scope='publish_stream')
@csrf_protect
def facebook_post(request, graph, albumtitle):
    """By using the django_facebook app, get the graph object, and post
    directly on user's facebook.

    Reference:  https://github.com/tschellenbach/django-facebook

    """

    album_obj = get_object_or_404(Album, user=request.user, title=albumtitle)
    message = album_obj.public_url_suffix
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
    """The webpage when user visit the shared album. """

    # FIXME: suffix should be a suffix, read below
    # url formation should look something like this:
    # http://domain.tld[:port]/user/album/suffix
    # suffix should look something like this: t7E5UEqsjgxFjjFRXw7h
    # public url: http://domain.tld[:port]/user/album/t7E5UEqsjgxFjjFRXw7h

    # FIXME: No hard-coding urls!
    my_public_url_suffix = "http://localhost.foo.fi:8000/public/"+albumurl
    album_obj = get_object_or_404(Album,public_url_suffix=my_public_url_suffix)
    pages = Page.objects.filter(album=album_obj)

    template = "public_album.html"
    params = {'pages': pages, 'url':albumurl}

    return render_to_response(template, params)


def publicpage(request,albumurl,pagenumber):
    """The webpage when user visit the page of the shared album. """

    # FIXME: No hard-coding urls!
    # FIXME: Not the right idea for suffix!
    my_public_url_suffix = "http://localhost.foo.fi:8000/public/"+albumurl
    album_obj = get_object_or_404(Album,public_url_suffix=my_public_url_suffix)
    page = Page.objects.filter(album=album_obj, number=pagenumber)
    images = Image.objects.filter(album=album_obj, page=page)

    return render_to_response(
        'public_page.html', {'album': album_obj, 'page': page, 'images': images})