"""
WSGI config for Fotosynteesi project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Fotosynteesi.settings")

from django.core.wsgi import get_wsgi_application

##uncommeet the following when deployed on heroku

# from dj_static import Cling
# application = Cling(get_wsgi_application())


##commet the following when deployed on heroku
application = get_wsgi_application()
