from django.urls import path

from .views import GuildsAPI

app_name = "users_api"
urlpatterns = [
    path("/", view=GuildsAPI.as_view(), name="list")
]
