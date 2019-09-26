from django.urls import path

from .views import ChannelsAPI, ChannelDetail

app_name = "channels_api"
urlpatterns = [
    path("", view=ChannelsAPI.as_view(), name="list"),
    path("<str:id>/", view=ChannelDetail.as_view(), name='detail')
]
