from django.shortcuts import render, redirect, render_to_response
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods, require_GET


from models import Album as Albumi
@login_required
def index(request):
    user = request.user
    msg = "hello %s, this is a test." % user.username
    album_objects = Albumi.objects.get(user=user)
    album_titles = [Album.title for Album in album_objects]
    return HttpResponse("albums.html", album_titles)


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
            return redirect('/')
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
        return redirect('/')
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
