from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, RedirectView, UpdateView
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from rest_framework.response import Response
from rest_framework.views import APIView


from geeksbot_v2.users.serializers import UserSerializer
from geeksbot_v2.users.serializers import UserLogSerializer
from geeksbot_v2.users.models import UserLog
from geeksbot_v2.utils.api_utils import PaginatedAPIView

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object, user=request.user)
        return self.render_to_response(context)


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, UpdateView):

    model = User
    fields = ["name"]

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    def get_object(self):
        return User.objects.get(username=self.request.user.username)

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.INFO, _("Infos successfully updated")
        )
        return super().form_valid(form)


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()

# API Views


class UsersAPI(PaginatedAPIView):
    def get(self, request, guild, format=None):
        users = User.objects.filter(guilds__id=guild)
        page = self.paginate_queryset(users)
        if page is not None:
            serialized_users = UserSerializer(users, many=True)
            return self.get_paginated_response(serialized_users.data)

        serialized_users = UserSerializer(users, many=True)
        return Response(serialized_users.data)


class UserDetail(APIView):
    def get(self, request, guild, id, format=None):
        user = User.objects.filter(guilds__id=guild).get(id=id)
        return Response(UserSerializer(user).data)


class UserLogList(PaginatedAPIView):
    def get(self, request, user, action=None, format=None):
        if action:
            user_logs = (
                UserLog.objects.filter(user=user)
                .filter(action=action)
                .order_by("-time")
            )
        else:
            user_logs = UserLog.objects.filter(user=user).order_by("-time")

        page = self.paginate_queryset(user_logs)
        if page is not None:
            serialized_logs = UserLogSerializer(page, many=True)
            return self.get_paginated_response(serialized_logs.data)

        serialized_logs = UserLogSerializer(user_logs, many=True)
        return Response(serialized_logs.data)


class UserLogDetail(APIView):
    def get(self, request, id, format=None):
        user_log = UserLog.objects.get(id=id)
        return Response(UserLogSerializer(user_log).data)
