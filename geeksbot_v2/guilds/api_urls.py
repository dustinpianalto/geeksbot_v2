from django.urls import path

from .views import GuildsAPI, GuildDetail

app_name = "users_api"
urlpatterns = [
    path("/", view=GuildsAPI.as_view(), name="list"),
    path("/<str:id>/", view=GuildDetail.as_view(), name='detail')
]
