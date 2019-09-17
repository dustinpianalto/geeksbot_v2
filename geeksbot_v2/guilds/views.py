import os

from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from geeksbot_v2.utils.api_utils import PaginatedAPIView
from .models import Guild
from .serializers import GuildSerializer

# Create your views here.

# API Views


class GuildsAPI(PaginatedAPIView):
    def get(self, request, format=None):
        users = Guild.objects.all()
        page = self.paginate_queryset(users)
        if page is not None:
            serialized_users = GuildSerializer(users, many=True)
            return self.get_paginated_response(serialized_users.data)

        serialized_users = GuildSerializer(users, many=True)
        return Response(serialized_users.data)

    def post(self, request, format=None):
        data = dict(request.data)
        print(data)
        id = data.get('id')
        default_channel = data.get('default_channel')
        if not (id and default_channel):
            return Response({'msg': 'id and default_channel are required'}, status=status.HTTP_400_BAD_REQUEST)

        admin_chat = data.get('admin_chat')
        new_patron_message = data.get('new_patron_message')
        default_prefix = os.environ['DISCORD_DEFAULT_PREFIX']
        prefixes = data.get('prefixes', [default_prefix, ])
        print(prefixes)

        guild = Guild(
            id=id[0] if isinstance(id, list) else id,
            default_channel=default_channel[0] if isinstance(default_channel, list) else default_channel,
            prefixes=prefixes,
            admin_chat=admin_chat[0] if isinstance(admin_chat, list) else admin_chat,
            new_patron_message=new_patron_message[0] if isinstance(new_patron_message, list) else new_patron_message
        )
        guild.save()

        return Response(GuildSerializer(guild).data, status=status.HTTP_201_CREATED)
