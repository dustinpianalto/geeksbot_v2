from django.urls import path

from geeksbot_v2.users.views import UsersAPI, UserDetail, UserLogList, UserLogDetail

app_name = "users_api"
urlpatterns = [
    path("", view=UsersAPI.as_view(), name="list"),
    path("<str:id>/", view=UserDetail.as_view(), name="detail"),
    path("<str:id>/logs/", view=UserLogList.as_view(), name="log_list"),
    path("<str:id>/logs/<str:log>", view=UserLogDetail.as_view(), name="log_detail"),
]
