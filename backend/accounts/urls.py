from django.urls import path

from accounts.views import CurrentUserView

urlpatterns = [
    path("auth/user/", CurrentUserView.as_view(), name="current-user"),
]
