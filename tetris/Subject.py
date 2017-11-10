#coding : utf-8
import Server
import asyncio
import websockets
import GlobalParameters as gp

class Subject:
    def __init__(self,gid):
        self.gid=gid
        self.observers={"players": [],"viewers": []}
        self.server = Server.server

    def bind_player(self,player) :
            self.observers["players"].append(player)

    def unbind_player(self,player) :
            self.observers["players"].remove(player)

    def bind_viewer(self,viewer) :
            self.observers["viewers"].append(viewer)

    def unbind_viewer(self,viewer) :
            self.observers["viewers"].remove(viewer)

    async def notify_all_observers(self) :
        await self.notify_view()
        await self.notify_player()

    async def notify_player(self) :
        mess = self.get_etat()
        for ws in self.observers["players"] :
            await self.server.send_message(ws[1],mess)
            pass

    async def notify_view(self) :
        mess = self.get_etat()
        for ws in self.observers["viewers"] :
            await self.server.send_message(ws[1],mess)

    async def set_action(self,command,value) :
        pass

    def get_etat(self) :
        pass
