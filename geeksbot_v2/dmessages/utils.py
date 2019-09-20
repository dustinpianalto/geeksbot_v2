from rest_framework.response import Response
from rest_framework import status


def create_error_response(msg, status=status.HTTP_404_NOT_FOUND):
    return Response({'details': msg},
                    status=status)


def create_success_response(message_data, status, many: bool = False):
    from .serializers import MessageSerializer

    return Response(MessageSerializer(message_data, many=many).data,
                    status=status)


def create_request_success_response(request_data, status, many: bool = False):
    from .serializers import AdminRequestSerializer

    return Response(AdminRequestSerializer(request_data, many=many).data,
                    status=status)


def create_comment_success_response(comment_data, status, many: bool = False):
    from .serializers import AdminCommentSerializer

    return Response(AdminCommentSerializer(comment_data, many=many).data,
                    status=status)
