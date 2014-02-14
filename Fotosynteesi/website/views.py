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
from django.core import serializers
from django.utils import simplejson
from django.db import OperationalError


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
    with request user filter in database. """
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
    """User create by using  'django.contrib.auth' system 
    see https://docs.djangoproject.com/en/dev/topics/auth/ for more detail"""
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



def account(request):
    return render_to_response("account.html", context_instance=RequestContext(request))


def photo(request):  # TODO: should be refactored
    """Order the images of one user by id, 
    and show the photo on webpage slide form. """

    # Handle file upload
    # if request.method == 'POST':
    #     # form = ImgForm(request.POST, request.FILES)
    #     # if form.is_valid():
    #         #get the image object
    #     imageList = Image.objects.filter(user=request.user)

    #     # Redirect to the images list after POST
    #     return HttpResponseRedirect(reverse('website.views.list'))

    # Load images for the list page
    message = {"status":""}
    images=Image.objects.filter(user=request.user)
    if request.is_ajax():
        if request.POST['setting']=='delete':
            if Image.objects.filter(user=request.user, id=request.POST['id']):         
                setimg=Image.objects.filter(user=request.user, id=request.POST['id'])
                setimg.delete()
                message["status"]="OK"
            else:
                message["status"]="no image!"
        else:
                message["status"]="no image!"
        json = simplejson.dumps(message)
        return HttpResponse(json, content_type = 'application/json')

    if request.method == 'POST':

        #get the image object
        # newimg = Image(imgfile = request.FILES['imgfile'])
        newimg = Image(remote_path = request.POST['imgurl'])
        # newtitle = request.FILES['imgfile'].name
        # newimg.title = newtitle.split('.')[0]
        newimg.save()

        #add user
        user = User.objects.get(username=request.user.username)
        newimg.user.add(user)
        # newimg.album.add(album)
        # newimg.page.add(page)
        # Redirect to the images list after POST
        return HttpResponseRedirect(reverse('website.views.photo'))



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


import re
def album_form(request):
    """Input the album title, when 'POST', create the new album. """

    '''Simple ajax deal with the album title conflict issue. '''
    message = {"status":""}
    template = "albumform.html"
    params = {'message': 'Album already have, choose another title!'} 
    if request.is_ajax():
        mytitle=request.POST['title']
        if not (re.match('^[\w-]+$', mytitle) is not None):
            message["status"] = "Special symbols"
        else:
            if not Album.objects.filter(user=request.user, title=mytitle):
            # if request.POST['title'] == 'wangyi':
                message["status"] = "OK to create"
            else:
                message["status"] = "confilct"
        '''Provide message to html page as json. '''
        json = simplejson.dumps(message)
        return HttpResponse(json, content_type = 'application/json')

    if request.method == 'POST':
        if " " in request.POST['title']:
            '''If title input has space, replace space with '_'. 
            Noticed: it is not a good solution now, should be fixed in the future.'''
            title_array = request.POST['title'].split(" ")
            mytitle = "_".join(title_array)
            if not Album.objects.filter(user=request.user, title=mytitle):
                newalbum = Album(title=mytitle)
            else:
                return render(request,template,params)
        else:
            mytitle = request.POST['title']
            if not Album.objects.filter(user=request.user, title=mytitle):
                newalbum = Album(title=mytitle)
                newalbum = Album(title=request.POST['title'])
            else:
                return render(request,template,params)
        # FIXME: No hard-coding urls!
        '''Assign the public url to album attribute. '''
        # newalbum.public_url_suffix = "http://localhost.foo.fi:8000/public/"+request.user.username+"_"+newalbum.title
        # FIXME: Suffix is still wrong!
        # FIXME: No hard-coding urls!
        '''Generate the public url for the album by use hexdigest'''
        import md5
        albumurl = request.user.username+"_"+newalbum.title
        albumurlm = md5.new(albumurl)  # FIXME: the module md5 is deprecated
        albumurldigest = albumurlm.hexdigest()

        newalbum.public_url_suffix = "http://fotomemo.herokuapp.com/public/"+albumurldigest
        # newalbum.public_url_suffix = "http://localhost.foo.fi:8000/public/"+albumurldigest
        newalbum.collaboration_url_suffix = 'google.com'
        
        #get the user object
        newalbum.save()
        user = User.objects.get(username=request.user.username)
        newalbum.user.add(user)
        return HttpResponseRedirect(reverse('website.views.album'))
    albums = Album.objects.filter(user=request.user)
    return render(request, template)


def albumdetail(request, albumtitle):
    """ Not been used in the url, can be deleted"""

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
    """ Delete the album with the albumtitle and redirect to 'album' page """
    album = Album.objects.filter(user=request.user, title=albumtitle)
    # images = Image.objects.filter(album=album)
    # for image in images:
    # images.delete()  # FIXME: This is wrong, images are not deleted
    album.delete()  # TODO: Realistically, albums shouldn't be either immediatl

    return HttpResponseRedirect(reverse('website.views.album'))
    

def album_page(request, albumtitle):
    """ Show the page detail inside one chosen album with its title """
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
    """ Choose the possible layout of the page, 
    and the layout attribute of the page will be given.
    Notice: when user click the layout style, 
    the page will be created no matter user upload photoes or not. """
    album = get_object_or_404(Album, user=request.user, title=albumtitle)
    alb_page = Page.objects.create(album=album, number=pagenumber, layout=1)

    template = "page_layout.html"
    params = {'album': album, 'page': alb_page}
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
            if Image.objects.filter(user=request.user, id=request.POST['id']):         
                setimg=Image.objects.get(user=request.user, id=request.POST['id'])
                setimg.album.add(album)
                setimg.page.add(page)
                message["status"]="OK"
            else:
                message["status"]="no image!"
        else:
            if Image.objects.filter(user=request.user, id=request.POST['id']):
                setimg=Image.objects.get(user=request.user, id=request.POST['id'])
                setimg.album.remove(album)
                setimg.page.remove(page)
                message["status"]="OK"
            else:
                message["status"]="no image!"
        json = simplejson.dumps(message)
        return HttpResponse(json, content_type = 'application/json')

    if request.method == 'POST':

        #get the image object
        # newimg = Image(imgfile = request.FILES['imgfile'])
        newimg=Image(remote_path=request.POST['imgurl'])
        # newtitle = request.FILES['imgfile'].name
        # newimg.title = newtitle.split('.')[0]
        newimg.save()

        #add user
        user = User.objects.get(username=request.user.username)
        newimg.user.add(user)
        # newimg.album.add(album)
        # newimg.page.add(page)
        # Redirect to the images list after POST
        return HttpResponseRedirect(reverse('website.views.photoadd', 
            kwargs={'albumtitle':album.title, 'pagenumber': page.number, 'layoutstyle':page.layout}))

    # images = Image.objects.filter(album=album,page=page)
    
    return render_to_response(
        'photoadd.html', {'images': images, 'album': album, 'page': page, 'layoutstyle':page.layout}, 
        context_instance=RequestContext(request))


def page_detail(request, albumtitle, pagenumber):
    """Show the page with its photo in the webpage """
    album = get_object_or_404(Album, user=request.user, title=albumtitle)
    page = Page.objects.filter(album=album, number=pagenumber)
    images = Image.objects.filter(user=request.user, album=album, page=page)
    allimages = Image.objects.filter(user=request.user)
    template = "page_detail.html"
    params = {'album': album, 'page': page, 'images': images, 'allimages':allimages}

    return render(request, template, params)


def page_delete(request, albumtitle, pagenumber):
    """Delete the selected page. """
    album = get_object_or_404(Album, user=request.user, title=albumtitle)
    page = Page.objects.filter(album=album, number=pagenumber)
    # images = Image.objects.filter(user=request.user, album=album, page=page)
    # images.delete()
    page.delete()
    viewname = 'website.views.album_page'
    params = {'albumtitle':album.title}

    return HttpResponseRedirect(reverse(viewname, kwargs=params))


def album_order(request, albumtitle):
    """Order the album by filling a order form """

    album = get_object_or_404(Album,user=request.user, title=albumtitle)

    template = "album_order.html"
    params = {'album': album}
    return render(request, template, params)


def order_submit(request, albumtitle):
    """Submit the order to order system.
    'sid', 'pid', 'redirect url' as well as 'amount' value need to given in the system. """

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

        # FIXME: No hard-coding urls!
        neworder.success_url = "http://fotomemo.herokuapp.com/album/"
        neworder.cancel_url = "http://fotomemo.herokuapp.com/album/"+album.title+"/paycancel"
        neworder.error_url = "http://fotomemo.herokuapp.com/album/"+album.title+"/payerror"
        
        # FIXME: No hard-coding urls!
        # neworder.success_url = "http://localhost.foo.fi:8000/album/"
        # neworder.cancel_url = "http://localhost.foo.fi:8000/album/"+album.title+"/paycancel"
        # neworder.error_url = "http://localhost.foo.fi:8000/album/"+album.title+"/payerror"

        neworder.save()

        template = "order_submit.html"
        params = {'album': album, 'order': neworder}
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
    """Pay cancel. Notice: when click cancel in the order syste, 
    the order still there need to be deleted in the future. """

    return HttpResponse("paycancel")


def payerror(request, albumtitle):
    """Pay error, same as paycancel """

    return HttpResponse("payerror")


def order_detail(request):
    """Give the order lists with details of a user """

    orders = Order.objects.filter(user=request.user)
    params = {'orders': orders}

    template = "order_detail.html"
    return render(request, template, params)


@facebook_required(scope='publish_stream')
@csrf_protect
def facebook_post(request, graph, albumtitle):
    """By using the django_facebook app, get the graph object, 
    and post directly on user's facebook.
    Reference:  https://github.com/tschellenbach/django-facebook """

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
    """The webpage when user visit the shared album. """

    # FIXME: suffix should be a suffix, read below
    # url formation should look something like this:
    # http://domain.tld[:port]/user/album/suffix
    # suffix should look something like this: t7E5UEqsjgxFjjFRXw7h
    # public url: http://domain.tld[:port]/user/album/t7E5UEqsjgxFjjFRXw7h

    # FIXME: No hard-coding urls!
    # my_public_url_suffix = "http://localhost.foo.fi:8000/public/"+albumurl
    my_public_url_suffix = "http://fotomemo.herokuapp.com/public/"+albumurl
    album = get_object_or_404(Album,public_url_suffix=my_public_url_suffix)
    pages = Page.objects.filter(album=album)

    template = "public_album.html"
    params = {'pages': pages, 'url':albumurl}

    return render_to_response(template, params)


def publicpage(request,albumurl,pagenumber):
    """The webpage when user visit the page of the shared album. """

    # FIXME: No hard-coding urls!
    # FIXME: Not the right idea for suffix!
    # my_public_url_suffix = "http://localhost.foo.fi:8000/public/"+albumurl
    my_public_url_suffix = "http://fotomemo.herokuapp.com/public/"+albumurl
    album = get_object_or_404(Album,public_url_suffix=my_public_url_suffix)
    page = Page.objects.filter(album=album, number=pagenumber)
    images = Image.objects.filter(album=album, page=page)

    return render_to_response(
        'public_page.html', {'album': album, 'page': page, 'images': images})