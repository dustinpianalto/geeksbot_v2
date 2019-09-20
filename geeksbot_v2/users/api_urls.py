from django.urls import path

from geeksbot_v2.users.views import UsersAPI, UserDetail

app_name = "users_api"
urlpatterns = [
    path("/", view=UsersAPI.as_view(), name="list"),
    path("/<str:id>/", view=UserDetail.as_view(), name="detail"),
]
