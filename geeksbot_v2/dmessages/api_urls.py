from django.urls import path

from .views import MessageDetailAPI, MessagesAPI
from .views import RequestDetailAPI, RequestsAPI
from .views import CommentDetailAPI, CommentsAPI, CommentsCountAPI
from .views import WaitForMessageAPI
from .views import UserRequestsAPI

app_name = "messages_api"
urlpatterns = [
    path("", view=MessagesAPI.as_view(), name="message_list"),
    path("<str:id>/", view=MessageDetailAPI.as_view(), name='message_detail'),
    path("<str:guild_id>/requests/", view=RequestsAPI.as_view(), name="requests_list"),
    path("<str:guild_id>/requests/<str:request_id>/", view=RequestDetailAPI.as_view(), name='request_detail'),
    path("<str:guild_id>/requests/<str:request_id>/comments/", view=CommentsAPI.as_view(), name="comments_list"),
    path("<str:guild_id>/requests/<str:request_id>/comments/count/", view=CommentsCountAPI.as_view(), name="comments_count"),
    path("<str:guild_id>/requests/<str:request_id>/comments/<str:comment_id>/", view=CommentDetailAPI.as_view(), name='comment_detail'),
    path("<str:guild_id>/requests/user/<str:author_id>/", view=UserRequestsAPI.as_view(), name='user_requests_list'),
    path("<str:id>/wait/", view=WaitForMessageAPI.as_view(), name='wait_for_message'),
    path("<str:id>/wait/<int:timeout>/", view=WaitForMessageAPI.as_view(), name='wait_for_message_timeout'),
]
