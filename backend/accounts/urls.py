from django.urls import path

from accounts.views import CurrentUserView, RegisterView

urlpatterns = [
    path("auth/user/", CurrentUserView.as_view(), name="current-user"),
    path("auth/register/", RegisterView.as_view(), name="register"),
]