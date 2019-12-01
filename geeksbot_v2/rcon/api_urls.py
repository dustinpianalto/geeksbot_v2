from django.urls import path

from .views import RCONServersAPI, RCONServerDetailAPI, ListPlayers

app_name = "rcon_api"
urlpatterns = [
    path("<str:guild_id>/", view=RCONServersAPI.as_view(), name='guild_servers'),
    path("<str:guild_id>/<str:name>/", view=RCONServerDetailAPI.as_view(), name="server_detail"),
    path("<str:guild_id>/<str:name>/listplayers", view=ListPlayers.as_view(), name='listplayers'),
]
