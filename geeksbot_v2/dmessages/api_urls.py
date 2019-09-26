from django.urls import path

from .views import MessageDetailAPI, MessagesAPI
from .views import RequestDetailAPI, RequestsAPI
from .views import CommentDetailAPI, CommentsAPI

app_name = "channels_api"
urlpatterns = [
    path("", view=MessagesAPI.as_view(), name="message_list"),
    path("<str:id>/", view=MessageDetailAPI.as_view(), name='message_detail'),
    path("requests/", view=RequestsAPI.as_view(), name="requests_list"),
    path("requests/<str:id>/", view=RequestDetailAPI.as_view(), name='request_detail'),
    path("requests/<str:request_id>/comments/", view=CommentsAPI.as_view(), name="comments_list"),
    path("requests/<str:request_id>/comments/<str:comment_id>/", view=CommentDetailAPI.as_view(), name='comment_detail'),
]
