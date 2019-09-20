from rest_framework.response import Response
from rest_framework import status


def create_error_response(msg, status=status.HTTP_404_NOT_FOUND):
    return Response({'details': msg},
                    status=status)


def create_success_response(channel_data, status, many: bool = False):
    from .serializers import ChannelSerializer

    return Response(ChannelSerializer(channel_data, many=many).data,
                    status=status)
