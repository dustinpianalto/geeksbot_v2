from rest_framework.response import Response
from rest_framework import status


def create_error_response(msg, status=status.HTTP_404_NOT_FOUND):
    return Response({'details': msg},
                    status=status)


def create_success_response(user_data, status, many: bool = False):
    from .serializers import UserSerializer

    return Response(UserSerializer(user_data, many=many).data,
                    status=status)


def create_log_success_response(log_data, status, many: bool = False):
    from .serializers import UserLogSerializer

    return Response(UserLogSerializer(log_data, many=many).data,
                    status=status)


required_fields = [
    'id',
    'username',
    'discriminator',
    'guild',
    'animated',
    'avatar',
    'bot',
]


def verify_user_data(data):
    return all([field in data.keys() for field in required_fields])
