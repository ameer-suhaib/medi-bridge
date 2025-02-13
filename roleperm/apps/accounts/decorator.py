

from django.shortcuts import redirect
from django.http import HttpResponse


def unauthenticated_user(view_fun):
    def wrapper_fun(request, *args,**kwargs):
        if request.user.is_authenticated:
            return redirect("admin_dashboard")
        return view_fun(request,*args,**kwargs)
    return wrapper_fun


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_fun(request,*args,**kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
            if group in allowed_roles:
                return view_func(request,*args,**kwargs)
            else:
                return HttpResponse("You are not allowded to view this page!!")
        return wrapper_fun
    return decorator