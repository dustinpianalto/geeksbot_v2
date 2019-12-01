from . import rcon
import asyncio
from typing import Union
import logging

arcon_log = logging.getLogger('arcon_lib')


class ARKServer(rcon.RCONConnection):
    def __init__(self, *args, monitor_chat: bool=False, server_chat_channel: int=None,
                 server_messages_channel: int=None, **kwargs):
        self.monitor_chat = monitor_chat
        self.server_chat_channel = server_chat_channel
        self.server_messages_channel = server_messages_channel
        super().__init__(*args, **kwargs)

    async def run_command(self, command: str, multi_packet: bool=False, reconnect_counter: int=0) \
            -> Union[rcon.RCONPacket, str]:
        arcon_log.debug(f'Command requested: {command}')
        if self.authenticated:
            packet = rcon.RCONPacket(next(self.packet_id), rcon.SERVERDATA_EXECCOMMAND, command)
            with await self.lock:
                try:
                    arcon_log.debug(f'Sending packet {packet.packet_id}')
                    await self.send_packet(packet)
                    arcon_log.debug(f'Packet Sent.')
                except ConnectionResetError:
                    arcon_log.info(f'Connection to {self.host}:{self.port} lost, Reconnecting...')
                    self.lock.release()
                    await self._reconnect_and_resend(packet)
                    await self.lock.acquire()
                finally:
                    arcon_log.debug(f'Waiting for response to packet {packet.packet_id}')
                    try:
                        response = await self.read(packet, multi_packet=multi_packet)
                    except asyncio.TimeoutError as e:
                        if reconnect_counter > 5:
                            return 'Reached max reconnects. Closing connection.'
                        arcon_log.warning(f'No response received: {e}\nAttempting to reconnect #{reconnect_counter}')
                        self.lock.release()
                        await self._reconnect()
                        await self.lock.acquire()
                        response = await self.run_command(command=command, multi_packet=multi_packet,
                                                          reconnect_counter=reconnect_counter + 1)
                    arcon_log.debug(f'Response Received:\n{response.packet_type}:{response.packet_id}:{response.body}')
            response.body = response.body.strip('\x00\x00').strip()
            return response
        else:
            return 'Server is not Authenticated. Please let the Admin know of this issue.'

    async def getchat(self) -> str:
        response = await self.run_command(command='getchat', multi_packet=True)
        return response.body if isinstance(response, rcon.RCONPacket) else response

    async def saveworld(self) -> str:
        response = await self.run_command(command='saveworld')
        return response.body if isinstance(response, rcon.RCONPacket) else response

    async def serverchat(self, message: str) -> str:
        response = await self.run_command(command=f'serverchat {message}')
        return response.body if isinstance(response, rcon.RCONPacket) else response

    async def broadcast(self, message: str) -> str:
        response = await self.run_command(command=f'broadcast {message}')
        return response.body if isinstance(response, rcon.RCONPacket) else response

    async def listplayers(self) -> str:
        response = await self.run_command(command=f'listplayers')
        return response.body if isinstance(response, rcon.RCONPacket) else response

    async def whitelist(self, steam_id: str) -> str:
        response = await self.run_command(command=f'AllowPlayerToJoinNoCheck {steam_id}')
        return response.body if isinstance(response, rcon.RCONPacket) else response

    async def ban_player(self, steam_id: int) -> str:
        response = await self.run_command(command=f'BanPlayer {steam_id}')
        return response.body if isinstance(response, rcon.RCONPacket) else response

    async def unban_player(self, steam_id: int) -> str:
        response = await self.run_command(command=f'UnbanPlayer {steam_id}')
        return response.body if isinstance(response, rcon.RCONPacket) else response

    async def kick_player(self, steam_id: int) -> str:
        response = await self.run_command(command=f'KickPlayer {steam_id}')
        return response.body if isinstance(response, rcon.RCONPacket) else response

    async def stop_server(self) -> int:
        saved = await self.saveworld()
        if saved == 'World Saved':
            await self.serverchat(saved)
            await asyncio.sleep(10)
            response = await self.run_command(command='DoExit')
            if response.body == 'Exiting...':
                return 0
            else:
                return 2
        else:
            return 1

    async def get_logs(self):
        response = await self.run_command(command=f'GetGameLog', multi_packet=True)
        return response.body if isinstance(response, rcon.RCONPacket) else response

    async def server_chat_to_steam_id(self, steam_id: int, message: str) -> str:
        response = await self.run_command(command=f'ServerChatTo {steam_id} {message}')
        return response.body if isinstance(response, rcon.RCONPacket) else response

    async def server_chat_to_player_name(self, player_name: str, message: str) -> str:
        response = await self.run_command(command=f'ServerChatToPlayer "{player_name}" {message}')
        return response.body if isinstance(response, rcon.RCONPacket) else response

    async def set_time_of_day(self, hour: int, minute: int=00, seconds: int=00) -> str:
        response = await self.run_command(command=f'SetTimeOfDay {hour}:{minute}:{seconds}')
        return response.body if isinstance(response, rcon.RCONPacket) else response

    async def destroy_wild_dinos(self):
        response = await self.run_command(command='DestroyWildDinos')
        return response.body if isinstance(response, rcon.RCONPacket) else response
