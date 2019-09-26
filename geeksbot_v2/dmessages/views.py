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


class RequestsAPI(PaginatedAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, guild, format=None):
        requests = AdminRequest.get_open_requests_by_guild(guild)
        page = self.paginate_queryset(requests)
        if page is not None:
            return create_request_success_response(page, status.HTTP_200_OK, many=True)

        return create_request_success_response(requests, status.HTTP_200_OK, many=True)

    def post(self, request, format=None):
        data = dict(request.data)
        return AdminRequest.add_new_request(data)


class RequestDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, req, id, format=None):
        req = AdminRequest.get_request_by_id(id)
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

    def put(self, request, id, format=None):
        req = AdminRequest.get_request_by_id(id)
        if req:
            data = dict(request.data)
            return req.update_request(data)
        return create_error_response("That Request Does Not Exist",
                                     status=status.HTTP_404_NOT_FOUND)


class CommentsAPI(PaginatedAPIView):
    permissions_classes = [IsAuthenticated]

    def post(self, request, request_id, format=None):
        data = dict(request.data)
        return AdminComment.add_new_comment(data, request_id)


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
