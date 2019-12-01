import asyncio
import logging
import itertools
import struct

# Packet types
SERVERDATA_AUTH = 3
SERVERDATA_AUTH_RESPONSE = 2
SERVERDATA_EXECCOMMAND = 2
SERVERDATA_RESPONSE_VALUE = 0

__all__ = ['RCONPacket', 'RCONConnection']

rcon_log = logging.getLogger('rcon_lib')


class RCONPacket:
    def __init__(self, packet_id: int=0, packet_type: int=-1, body: str=''):
        self.packet_id = packet_id
        self.packet_type = packet_type
        self.body = body

    def __str__(self):
        """Return the body of the packet"""
        return self.body

    def size(self):
        """Return the size of the packet"""
        return len(self.body) + 10

    def pack(self):
        """Return the packed packet"""
        return struct.pack(f'<3i{len(self.body) + 2}s',
                           self.size(),
                           self.packet_id,
                           self.packet_type,
                           bytearray(self.body, 'utf-8'))


class RCONConnection:
    """Connection to an RCON server"""

    def __init__(self, host: str, port: int, password: str='', single_packet: bool=False, loop=None):
        """Create a New RCON Connection

        Parameters:
            host (str): The hostname or IP address of the server to connect to
            port (int): The port to connect to on the server
            password (str): The password to authenticate with the server
            single_packet (bool): True for servers who don't give 0 length SERVERDATA_RESPONSE_VALUE requests
        """

        self.host = host
        self.port = port
        self.password = password
        self.single_packet = single_packet
        self.packet_id = itertools.count(1)
        self.loop = loop or asyncio.get_event_loop()
        self.reader = None
        self.writer = None
        self.lock = asyncio.Lock()
        self.authenticated = False

    async def connect(self):
        """Returns -1 if connection times out
        Returns 1 if connection and auth are successful
        Returns 0 if auth fails"""
        try:
            rcon_log.debug(f'Connecting to {self.host}:{self.port}...')
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port, loop=self.loop)
        except TimeoutError as e:
            rcon_log.error(f'Timeout error: {e}')
            return -1
        else:
            rcon_log.debug('Connected. Attempting to Authenticate...')
            auth_packet = RCONPacket(next(self.packet_id), SERVERDATA_AUTH, self.password)
            with await self.lock:
                await self.send_packet(auth_packet)
                response = await self.read()
                if response.packet_type == SERVERDATA_AUTH_RESPONSE and response.packet_id != -1:
                    rcon_log.debug(f'Authorized {response.packet_type}:{response.packet_id}:{response.body}')
                    self.authenticated = True
                    return 1
                else:
                    rcon_log.debug(f'Not Authorized {response.packet_type}:{response.packet_id}:{response.body}')
                    self.authenticated = False
                    return 0

    async def _reconnect(self):
        self.writer = None
        self.reader = None
        connected = await self.connect()
        rcon_log.info(f'Connection completed with a return of {connected}')
        if connected != -1:
            rcon_log.info('Connected')
        else:
            rcon_log.warning('Connection Failed')
        return connected

    async def _reconnect_and_resend(self, packet):
        connected = await self._reconnect()
        if connected != -1:
            await asyncio.sleep(0.1)
            rcon_log.info(f'Re-sending packet {packet.packet_id}')
            await self.send_packet(packet)
            rcon_log.info(f'Packet Sent.')
            return connected
        else:
            return connected

    async def keep_alive(self):
        while True:
            await asyncio.sleep(60)
            ka_packet = RCONPacket(next(self.packet_id), SERVERDATA_EXECCOMMAND, '')
            try:
                with await self.lock:
                    await asyncio.wait_for(self.send_packet(ka_packet), 10, loop=self.loop)
                    await asyncio.wait_for(self.read(ka_packet), 10, loop=self.loop)
            except asyncio.TimeoutError:
                self.reader = None
                self.writer = None
                await self.connect()

    async def send_packet(self, packet):
        if packet.size() > 4096:
            rcon_log.error('Packet Size is larger than 4096 bytes. Cannot send packet.')
            raise RuntimeWarning('Packet Size is larger than 4096 bytes. Cannot send packet.')
        if self.writer is None:
            await self.connect()
        rcon_log.debug(f'Sending Packet {packet.packet_id}: {packet.pack() if packet.packet_type is not SERVERDATA_AUTH else "Censored for Password Security."}')
        self.writer.write(packet.pack())
        await self.writer.drain()
        rcon_log.debug(f'Packet {packet.packet_id} Sent.')

    async def read(self, request: RCONPacket=None, multi_packet=False) -> RCONPacket:
        rcon_log.debug(f'Waiting to receive response to packet {request.packet_id if request else None}')
        response = RCONPacket()
        try:
            if request:
                while response.packet_id != request.packet_id and response.packet_id < request.packet_id:
                    if multi_packet:
                        if request is None:
                            rcon_log.warning('A request packet is required to receive a multi packet response')
                            raise ValueError('A request packet is required to receive a multi packet response')
                        await asyncio.sleep(.01)
                        response = await self._receive_multi_packet()
                        rcon_log.debug(f'Received Multi-Packet response to packet {request.packet_id}:\n'
                                       f'{response.packet_type}:{response.packet_id}:{response.body}')
                    else:
                        response = await self.receive_packet()
                        rcon_log.debug(f'Received Single-Packet response to packet {request.packet_id}:\n'
                                       f'{response.packet_type}:{response.packet_id}:{response.body}')
            else:
                response = await self.receive_packet()
                rcon_log.debug(f'Received Single-Packet response:\n'
                               f'{response.packet_type}:{response.packet_id}:{response.body}')
        except struct.error as e:
            rcon_log.error(f'Struct Error: {e}')
            response = RCONPacket(body='Error receiving data from the server. Attempting to reconnect. '
                                       'Please try again in a little bit.')
            self.lock.release()
            await self._reconnect()
            await self.lock.acquire()
        except AttributeError as e:
            rcon_log.error(f'Attribute Error: {e}')
            response = RCONPacket(body='Error receiving data from the server. Attempting to reconnect. '
                                       'Please try again in a little bit.')
            self.lock.release()
            await self._reconnect()
            await self.lock.acquire()
        return response

    async def receive_packet(self):
        header = await self.reader.read(struct.calcsize('<3i'))
        (packet_size, packet_id, packet_type) = struct.unpack('<3i', header)
        body = await self.reader.read(packet_size - 8)
        return RCONPacket(packet_id, packet_type, body.decode('ascii'))

    async def _receive_multi_packet(self):
        header = await self.reader.read(struct.calcsize('<3i'))
        (packet_size, packet_id, packet_type) = struct.unpack('<3i', header)
        body = await self.reader.readuntil(separator=b'\x00\x00')
        return RCONPacket(packet_id, packet_type, body.decode('ascii'))
