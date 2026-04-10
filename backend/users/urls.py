from django.urls import path

from .views import LoginView, MeView, UserCreateView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("me/", MeView.as_view(), name="me"),
    path("users/", UserCreateView.as_view(), name="users"),
]
