from rest_framework.response import Response
from rest_framework import status


def create_error_response(msg, status=status.HTTP_404_NOT_FOUND):
    return Response({'details': msg},
                    status=status)


def create_success_response(rcon_data, status, many: bool = False):
    from .serializers import RconServerSerializer

    return Response(RconServerSerializer(rcon_data, many=many).data,
                    status=status)


def create_rcon_response(message, status):
    msg_list = message.split('\n')
    return Response(msg_list, status=status)
