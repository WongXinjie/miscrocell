#-*- coding: utf8 -*-
from functools import wraps
from django.http import HttpResponseRedirect

def login_required(redirect_url="/"):

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if 'login_author' not in request.session:
                return HttpResponseRedirect(redirect_url)
            else:
                return func(request, *args, **kwargs)
        return wrapper
    return decorator



