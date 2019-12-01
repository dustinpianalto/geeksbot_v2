from django.urls import path

from .views import ChannelsAPI, ChannelDetail, AdminChannelAPI

app_name = "channels_api"
urlpatterns = [
    path("", view=ChannelsAPI.as_view(), name="list"),
    path("<str:id>/", view=ChannelDetail.as_view(), name='detail'),
    path("<str:guild_id>/admin/", view=AdminChannelAPI.as_view(), name='admin')
]
