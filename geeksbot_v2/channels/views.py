from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist

from geeksbot_v2.utils.api_utils import PaginatedAPIView
from .models import Channel
from .utils import create_error_response
from .utils import create_success_response

# Create your views here.

# API Views


class ChannelsAPI(PaginatedAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, guild_id, format=None):
        channels = Channel.get_guild_channels(guild_id)
        page = self.paginate_queryset(channels)
        if page is not None:
            return create_success_response(page, status.HTTP_200_OK, many=True)

        return create_success_response(channels, status.HTTP_200_OK, many=True)

    def post(self, request, format=None):
        data = dict(request.data)
        return Channel.add_new_channel(data)


class AdminChannelAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, guild_id, format=None):
        channel = Channel.get_admin_channel(guild_id)
        if channel:
            return create_success_response(channel, status=status.HTTP_200_OK)
        return create_error_response('There is no admin channel configured for that guild',
                                     status=status.HTTP_404_NOT_FOUND)

    def put(self, request, guild_id, format=None):
        data = dict(request.data)
        channel = Channel.get_channel_by_id(guild_id, data['channel'])
        if channel:
            channel = channel.update_channel({'admin': True})
            return create_success_response(channel, status=status.HTTP_202_ACCEPTED)
        return create_error_response("That channel does not exist",
                                     status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, guild_id, format=None):
        channel = Channel.get_admin_channel(guild_id)
        if channel:
            channel = channel.update_channel({'admin': False})
            return create_success_response(channel, status=status.HTTP_202_ACCEPTED)
        return create_error_response("There is no admin channel configured",
                                     status=status.HTTP_404_NOT_FOUND)


class ChannelDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, guild_id, channel_id, format=None):
        try:
            guild = Channel.get_channel_by_id(guild_id, channel_id)
        except ObjectDoesNotExist:
            return create_error_response("Channel Does not Exist",
                                         status=status.HTTP_404_NOT_FOUND)
        else:
            return create_success_response(guild,
                                           status=status.HTTP_200_OK)

    def put(self, request, guild_id, channel_id, format=None):
        channel = Channel.get_channel_by_id(guild_id, channel_id)

        if channel:
            data = dict(request.data)
            channel = channel.update_channel(data)
            return create_success_response(channel,
                                           status=status.HTTP_202_ACCEPTED)
        else:
            return create_error_response('Channel Does Not Exist',
                                         status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, guild_id, channel_id, format=None):
        channel = Channel.get_channel_by_id(guild_id, channel_id)

        if channel:
            # data = dict(request.data)
            # TODO Add a check to verify user is allowed to delete...
            # Possibly in object permissions...
            channel.delete()
            return create_success_response(guild,
                                           status=status.HTTP_200_OK)
        else:
            return create_error_response('Channel Does Not Exist',
                                         status=status.HTTP_404_NOT_FOUND)
