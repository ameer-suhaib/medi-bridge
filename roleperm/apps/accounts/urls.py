from . import views
from django.urls import path

urlpatterns = [
    path("register/",views.register,name="register"),
    path("listing/",views.listing,name="listing"),
    path("logout/",views.logout_view,name="logout"),
]