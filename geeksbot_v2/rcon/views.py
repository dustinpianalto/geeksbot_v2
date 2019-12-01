import asyncio

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .rcon_lib import arcon

from .models import RconServer
from .utils import create_error_response, create_success_response, create_rcon_response
from geeksbot_v2.utils.api_utils import PaginatedAPIView
from .serializers import RconServerSerializer

# Create your views here.

# API Views


class RCONServersAPI(PaginatedAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, guild_id, format=None):
        servers = RconServer.get_guild_servers(guild_id)
        page = self.paginate_queryset(servers)
        if page:
            return create_success_response(page, status.HTTP_200_OK, many=True)
        return create_success_response(servers, status.HTTP_200_OK, many=True)

    def post(self, request, guild_id, format=None):
        data = dict(request.data)
        data['guild'] = guild_id
        return RconServer.add_new_server(data)


class RCONServerDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, guild_id, name, format=None):
        server = RconServer.get_server(guild_id, name)
        if server:
            return create_success_response(server, status.HTTP_200_OK, many=False)
        else:
            return create_error_response("RCON Server Does Not Exist",
                                         status=status.HTTP_404_NOT_FOUND)

    def put(self, request, guild_id, name, format=None):
        data = dict(request.data)
        server = RconServer.get_server(guild_id, name)
        if server:
            return server.update_server(data)
        else:
            return create_error_response('RCON Server Does Not Exist',
                                         status=status.HTTP_404_NOT_FOUND)


class ListPlayers(PaginatedAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, guild_id, name, format=None):
        server: RconServer = RconServer.get_server(guild_id, name)
        if server:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop = asyncio.get_event_loop()
            ark = arcon.ARKServer(host=server.ip, port=server.port, password=server.password, loop=loop)
            connected = loop.run_until_complete(ark.connect())
            if connected == 1:
                resp = loop.run_until_complete(ark.listplayers())
                if resp == 'No Players Connected':
                    return create_rcon_response(resp, status=status.HTTP_204_NO_CONTENT)
                else:
                    return create_rcon_response(resp, status=status.HTTP_200_OK)
            else:
                return create_error_response('Connection failure',
                                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return create_error_response('RCON Server Does Not Exist',
                                     status=status.HTTP_404_NOT_FOUND)
