from rest_framework.response import Response
from rest_framework import status


def create_error_response(msg, status=status.HTTP_404_NOT_FOUND):
    return Response({'details': msg},
                    status=status)


def create_success_response(guild_data, status, many: bool = False):
    from .serializers import GuildSerializer

    return Response(GuildSerializer(guild_data, many=many).data,
                    status=status)


def create_role_success_response(role_data, status, many: bool = False):
    from .serializers import RoleSerializer

    return Response(RoleSerializer(role_data, many=many).data,
                    status=status)
