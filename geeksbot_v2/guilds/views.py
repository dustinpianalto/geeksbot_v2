from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist

from geeksbot_v2.utils.api_utils import PaginatedAPIView
from .models import Guild
from .utils import create_error_response
from .utils import create_success_response

# Create your views here.

# API Views


class GuildsAPI(PaginatedAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        guilds = Guild.objects.all()
        page = self.paginate_queryset(guilds)
        if page is not None:
            return create_success_response(page, status.HTTP_200_OK, many=True)

        return create_success_response(guilds, status.HTTP_200_OK, many=True)

    def post(self, request, format=None):
        data = dict(request.data)
        return Guild.create_guild(data)


class GuildDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id, format=None):
        try:
            guild = Guild.objects.get(id=id)
        except ObjectDoesNotExist:
            return create_error_response("Guild Does not Exist",
                                         status=status.HTTP_404_NOT_FOUND)
        else:
            return create_success_response(guild,
                                           status=status.HTTP_200_OK)

    def put(self, request, id, format=None):
        guild = Guild.get_guild_by_id(id)

        if guild:
            data = dict(request.data)
            guild = guild.update_guild(data)
            return create_success_response(guild,
                                           status=status.HTTP_202_ACCEPTED)
        else:
            return create_error_response('Guild Does Not Exist',
                                         status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id, format=None):
        guild = Guild.get_guild_by_id(id)

        if guild:
            # data = dict(request.data)
            # TODO Add a check to verify user is allowed to delete...
            # Possibly in object permissions...
            guild.delete()
            return create_success_response(guild,
                                           status=status.HTTP_200_OK)
        else:
            return create_error_response('Guild Does Not Exist',
                                         status=status.HTTP_404_NOT_FOUND)
