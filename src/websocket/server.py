import asyncio
import json
from websockets.server import serve


class WebSocketServer:
    def __init__(self):
        self._message = None
        self._connected_clients = set()
        self.server = None
        self._start()

    async def _handle_client(self, websocket):
        self._connected_clients.add(websocket)
        try:
            await websocket.send(self._message)
            async for _ in websocket:
                pass
        finally:
            self._connected_clients.remove(websocket)

    def message(self, new_message):
        self._message = new_message
        asyncio.get_event_loop().run_until_complete(self.broadcast_update())

    async def broadcast_update(self):
        if self._connected_clients:
            message = json.dumps(self._message)
            await asyncio.gather(
                *[client.send(message) for client in self._connected_clients]
            )

    def _start(self):
        self.server = serve(self._handle_client, "localhost", 8765)
        asyncio.get_event_loop().run_until_complete(self.server)
        asyncio.get_event_loop().run_forever()


class WebSocketMessage:
    def __init__(self, message_type, data):
        self.message_type = message_type
        self.data = data

    def __str__(self):
        return json.dumps({"type": self.message_type, "data": self.data})


class ItemsMessage(WebSocketMessage):
    def __init__(self, items):
        super().__init__("items", items)


class ConsoleMessage(WebSocketMessage):
    def __init__(self, console_data):
        super().__init__("console", console_data)


ws_server = WebSocketServer()
