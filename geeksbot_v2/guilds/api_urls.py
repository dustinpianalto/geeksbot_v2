from django.urls import path

from .views import GuildsAPI, GuildDetail
from .views import RolesAPI, RoleDetailAPI
from .views import AdminRolesAPI

app_name = "guilds_api"
urlpatterns = [
    path("", view=GuildsAPI.as_view(), name="list"),
    path("<str:id>/", view=GuildDetail.as_view(), name='detail'),
    path("<str:guild_id>/roles/", view=RolesAPI.as_view(), name="list"),
    path("<str:guild_id>/roles/admin/", view=AdminRolesAPI.as_view(), name='admin'),
    path("<str:guild_id>/roles/<str:id>/", view=RoleDetailAPI.as_view(), name='detail'),
]
