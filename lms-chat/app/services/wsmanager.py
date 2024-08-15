from fastapi import WebSocket

class ConnectionManager:
    def __init__(self) -> None:
        self.connections = dict()
        self.notifications = dict()

    async def connect(self, ws: WebSocket, conversation_id: str, user_id: int):
        await ws.accept()
        if conversation_id not in self.connections:
            self.connections[conversation_id] = []
        self.connections[conversation_id].append((ws, user_id))
        ws.send_json({"type": "connect"})

    def disconnect(self, ws: WebSocket, conversation_id: str):
        ws.send_json({"type": "disconnect"})
        self.connections[conversation_id] = [(w, u) for w, u in self.connections[conversation_id] if w != ws]

    async def broadcast(self, conversation_id: str, message: dict):
        for ws, _ in self.connections[conversation_id]:
            await ws.send_json(message)
    
    async def broadcast_except(self, conversation_id: str, message: dict, user_id: int, members: list):
        remaining = members.copy()
        for ws, u in self.connections[conversation_id]:
            if u != user_id:
                await ws.send_json(message)
            remaining.remove(u)
        for member in remaining:
            if member in self.notifications:
                await self.notify(member, message)
        

    async def broadcast_read_receipt(self, conversation_id: str, message_id: int, user_id: int):
        message = {
            "type": "read_receipt",
            "message_id": message_id,
            "read_by": user_id
        }
        await self.broadcast(conversation_id, message)
    
    async def noti_connect(self, ws: WebSocket, user_id: int):
        await ws.accept()
        self.notifications[user_id] = ws

    def noti_disconnect(self, user_id: int):
        del self.notifications[user_id]
    
    async def notify(self, user_id: int, message: dict):
        await self.notifications[user_id].send_json(message)

connection_manager = ConnectionManager()