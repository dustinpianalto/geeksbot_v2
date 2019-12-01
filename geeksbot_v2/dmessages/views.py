from time import sleep
from datetime import datetime

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status


from .models import Message
from .models import AdminComment
from .models import AdminRequest
from .models import GuildInfo
from geeksbot_v2.utils.api_utils import PaginatedAPIView
from .utils import create_error_response
from .utils import create_success_response
from .utils import create_request_success_response
from .utils import create_comment_success_response
from .serializers import AdminRequestSerializer
from .serializers import AdminCommentSerializer

# Create your views here.

# API Views


class MessagesAPI(PaginatedAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        messages = Message.objects.all()
        page = self.paginate_queryset(messages)
        if page:
            return create_success_response(page, status.HTTP_200_OK, many=True)
        return create_success_response(messages, status.HTTP_200_OK, many=True)

    def post(self, request, format=None):
        data = dict(request.data)
        return Message.add_new_message(data)


class MessageDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id, format=None):
        message = Message.get_message_by_id(id)
        if message:
            return create_success_response(message, status.HTTP_200_OK, many=False)
        else:
            return create_error_response("Message Does Not Exist",
                                         status=status.HTTP_404_NOT_FOUND)

    def put(self, request, id, format=None):
        data = dict(request.data)
        message = Message.get_message_by_id(id)
        if message:
            return message.update_message(data)
        else:
            return create_error_response('Message Does Not Exist',
                                         status=status.HTTP_404_NOT_FOUND)


class WaitForMessageAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id, timeout: int = 3, format=None):
        message = Message.get_message_by_id(id)
        try_count = 0
        while not message:
            sleep(0.1)
            try_count += 1
            if try_count > timeout * 10:
                return create_error_response("Timeout reached before message is available.",
                                             statu=status.HTTP_404_NOT_FOUND)
            message = Message.get_message_by_id(id)
        return create_success_response(message, status=status.HTTP_200_OK)


class RequestsAPI(PaginatedAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, guild_id, format=None):
        requests = AdminRequest.get_open_requests_by_guild(guild_id)
        page = self.paginate_queryset(requests)
        if page is not None:
            return create_request_success_response(page, status.HTTP_200_OK, many=True)
        if requests:
            return create_request_success_response(requests, status.HTTP_200_OK, many=True)
        return create_error_response("No requests found")

    def post(self, request, guild_id, format=None):
        data = dict(request.data)
        return AdminRequest.add_new_request(guild_id, data)


class UserRequestsAPI(PaginatedAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, guild_id, author_id, format=None):
        requests = AdminRequest.get_open_requests_by_guild_author(guild_id, author_id)
        page = self.paginate_queryset(requests)
        if page is not None:
            return create_request_success_response(page, status.HTTP_200_OK, many=True)
        if requests:
            return create_request_success_response(requests, status.HTTP_200_OK, many=True)
        return create_error_response("No requests found")


class RequestDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, req, guild_id, request_id, format=None):
        req = AdminRequest.get_open_request_by_id(guild_id, request_id)
        if req:
            comments = AdminComment.get_comments_by_request(req)
            if comments:
                data = AdminRequestSerializer(req).data
                data['comments'] = AdminCommentSerializer(comments, many=True).data
                return Response(data, status.HTTP_200_OK)
            else:
                return create_request_success_response(req, status.HTTP_200_OK, many=False)
        else:
            return create_error_response("That Request Does Not Exist",
                                         status=status.HTTP_404_NOT_FOUND)

    def put(self, request, guild_id, request_id, format=None):
        req = AdminRequest.get_open_request_by_id(guild_id, request_id)
        if req:
            data = dict(request.data)
            return req.update_request(data)
        return create_error_response("That Request Does Not Exist",
                                     status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, guild_id, request_id, format=None):
        data = dict(request.data)
        request = AdminRequest.get_open_request_by_id(guild_id, request_id)
        data['completed'] = True
        data['completed_at'] = datetime.utcnow()
        return request.update_request(data)


class CommentsAPI(PaginatedAPIView):
    permissions_classes = [IsAuthenticated]

    def get(self, request, guild_id, request_id, format=None):
        comments = AdminComment.get_comments_by_request(request_id)
        if comments:
            return create_comment_success_response(comments, status=status.HTTP_200_OK, many=True)
        return create_error_response("No Comments found")

    def post(self, request, guild_id, request_id, format=None):
        data = dict(request.data)
        return AdminComment.add_new_comment(data, guild_id, request_id)


class CommentsCountAPI(PaginatedAPIView):
    permissions_classes = [IsAuthenticated]

    def get(self, request, guild_id, request_id, format=None):
        comments = AdminComment.get_comments_by_request(request_id)
        if comments:
            return Response(len(comments), status=status.HTTP_200_OK)
        return Response(0, status.HTTP_200_OK)


class CommentDetailAPI(APIView):
    permissions_classes = [IsAuthenticated]

    def get(self, request, request_id, comment_id, format=None):
        comment = AdminComment.get_comment_by_id(comment_id)
        if comment:
            if comment.request.id != request_id:
                return create_error_response("That comment is not for this request",
                                             status=status.HTTP_400_BAD_REQUEST)
            return create_comment_success_response(comment, status.HTTP_200_OK, many=False)
        else:
            return create_error_response("Comment Does Not Exist",
                                         status=status.HTTP_404_NOT_FOUND)
