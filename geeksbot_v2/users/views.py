from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, RedirectView, UpdateView
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


from .models import UserLog
from geeksbot_v2.utils.api_utils import PaginatedAPIView
from .models import User
from .serializers import UserSerializer
from .serializers import UserLogSerializer
from geeksbot_v2.utils.permissions import CustomDjangoModelPermissions
from geeksbot_v2.utils.permissions import CustomDjangoObjectPermissions
from .utils import create_error_response
from .utils import create_success_response
from .utils import create_log_success_response


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


class UsersAPI(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(guilds__id=self.request.data.get('guild'))

    # def get(self, request, guild=None, format=None):
    #     if guild:
    #         users = User.objects.filter(guilds__id=guild)
    #     else:
    #         users = User.objects.all()
    #     page = self.paginate_queryset(users)
    #     if page is not None:
    #         return create_success_response(page, status.HTTP_200_OK, many=True)
    #
    #     return create_success_response(users, status.HTTP_200_OK, many=True)
    #
    # def post(self, request, format=None):
    #     data = dict(request.data)
    #     return User.add_new_user(data)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return User.objects.all()

    # def get(self, request, id, format=None):
    #     user = User.get_user_by_id(id)
    #     if not isinstance(user, User):
    #         return create_error_response("User Does not Exist",
    #                                      status=status.HTTP_404_NOT_FOUND)
    #     return create_success_response(user,
    #                                    status=status.HTTP_200_OK)
    #
    # def put(self, request, id, format=None):
    #     user = User.get_user_by_id(id)
    #     if isinstance(user, User):
    #         data = dict(request.data)
    #         return user.update_user(data)
    #     else:
    #         return create_error_response("User Does Not Exist",
    #                                      status=status.HTTP_404_NOT_FOUND)


class UserLogList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserLogSerializer

    def get_queryset(self):
        return UserLog.objects.all()

    # def get(self, request, user, action=None, format=None):
    #     if action:
    #         user_logs = UserLog.get_logs_by_user_action(user, action)
    #     else:
    #         user_logs = UserLog.get_logs_by_user(user)
    #
    #     page = self.paginate_queryset(user_logs)
    #     if page is not None:
    #         return create_log_success_response(page, status.HTTP_200_OK, many=True)
    #
    #     return create_log_success_response(user_logs, status.HTTP_200_OK, many=True)
    #
    # def post(self, request, user, format=None):
    #     data = dict(request.data)
    #     return UserLog.add_new_log(user, data)


class UserLogDetail(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserLogSerializer
    lookup_url_kwarg = 'log'
    lookup_field = 'id'

    def get_queryset(self):
        user_id = self.kwargs['id']
        return UserLog.objects.filter(user__id=user_id)

    # def get(self, request, id, format=None):
    #     user_log = UserLog.get_log_by_id(id)
    #     if isinstance(user_log, UserLog):
    #         return create_log_success_response(user_log, status.HTTP_200_OK, many=False)
    #     else:
    #         return create_error_response("Log Does Not Exist",
    #                                      status=status.HTTP_404_NOT_FOUND)
