# coding: utf-8

import asyncio
import json

import websockets

import IA
import GlobalParameters as gp
URI = gp.ADRESSE + str(gp.PORT)


class IAClient:

    def __init__(self, name, active):
        self.my_socket = None
        self.keep_connection = True
        self.my_ia = IA.IA(IA.random_ia)
        self.name = name
        self.nid = None
        self.id_in_game = None
        self.last_turn = None
        self.active = active

    async def connect(self, uri=URI):
        self.my_socket = await websockets.connect(uri)
        await self.send_message({"name": self.name, "active": self.active})
        data = await self.receive_message()
        self.nid = data["nid"]
        while self.keep_connection:
            await asyncio.sleep(0)

    def make_connection_to_server(self):
        asyncio.ensure_future(self.connect())

    async def receive_message(self):
        data = await self.my_socket.recv()
        # print("receive")
        # print(data)
        return json.loads(data)

    async def receive_msg(self):
        data = await self.receive_message()
        if data["step"] == "connect":
            self.init_connect(data)
        elif data["step"] == "init_game":
            self.init_game(data)
        elif data["step"] == "game":
            if data["actual_player"] == self.id_in_game:
                await self.play(data)
        elif data["step"] == "suggest":
            if data["actual_player"] == self.id_in_game:
                await self.suggest(data)
        elif data["step"] == "finished":
            self.finished(data)
        else:
            print("Error message receive : step unknown")
            
    def finished(self,data):
        self.last_turn = None
        self.id_in_game = None
        if not self.active:
            self.keep_connection = False

    def init_game(self, data):
        self.keep_connection = True
        self.id_in_game = data["id_in_game"]
        print("Succesfull game connection id_in_game:", str(self.id_in_game))

    def init_connect(self, data):
        self.nid = data["pid"]
        print("Succesfull server connection id:", str(self.nid))

    async def play(self, data):
        dec = self.my_ia.play(data)
        self.last_turn = data["turn"]
        await self.send_message({"action": ["choose", dec.pop("choose")]})
        for (key, value) in dec.items():
            await self.send_message({"action": [key, value]})
        await self.send_message({"action": ["valid"]})
        return data

    async def suggest(self, data):
        dec = self.my_ia.play(data)
        self.last_turn = data["turn"]
        await self.send_message({"action": ["choose", dec.pop("choose")]})
        for (key, value) in dec.items():
            await self.send_message({"action": [key, value]})

    async def send_message(self, data):
        # print("send")
        # print(data)
        await self.my_socket.send(json.dumps(data))


async def run(name="IA", active=False):
    my_client = IAClient(name, active)
    my_client.make_connection_to_server()
    while my_client.my_socket is None:
        await asyncio.sleep(0)
    while my_client.keep_connection:
        await my_client.receive_msg()
        await asyncio.sleep(0)

#
# asyncio.get_event_loop().run_until_complete(main())
