from django.urls import path

from geeksbot_v2.users.views import UsersAPI

app_name = "users_api"
urlpatterns = [
    path("users/", view=UsersAPI.as_view(), name="list")
]
