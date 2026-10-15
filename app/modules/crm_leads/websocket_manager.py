import json
from typing import Dict, List
from fastapi import WebSocket


class CRMConnectionManager:
    """Manages real-time WebSocket connections for Admin & Sales dashboards."""
    def __init__(self):
        self.active_admin_connections: List[WebSocket] = []
        self.user_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int, is_admin: bool = False):
        await websocket.accept()
        if is_admin:
            self.active_admin_connections.append(websocket)
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int, is_admin: bool = False):
        if is_admin and websocket in self.active_admin_connections:
            self.active_admin_connections.remove(websocket)
        
        if user_id in self.user_connections and websocket in self.user_connections[user_id]:
            self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

    async def broadcast_to_admins(self, payload: dict):
        """Sends instant popup & sound alerts to all logged-in Admins."""
        message = json.dumps(payload)
        for connection in list(self.active_admin_connections):
            try:
                await connection.send_text(message)
            except Exception:
                self.active_admin_connections.remove(connection)

    async def send_to_user(self, user_id: int, payload: dict):
        """Sends targeted alerts to a specific Sales Executive's screen."""
        if user_id in self.user_connections:
            message = json.dumps(payload)
            for connection in list(self.user_connections[user_id]):
                try:
                    await connection.send_text(message)
                except Exception:
                    self.user_connections[user_id].remove(connection)

    async def broadcast_announcement(self, payload: dict):
        """Broadcasts global alerts to all active dashboards."""
        message = json.dumps(payload)
        all_sockets = set(self.active_admin_connections)
        for user_sockets in self.user_connections.values():
            all_sockets.update(user_sockets)
        for socket in all_sockets:
            try:
                await socket.send_text(message)
            except Exception:
                pass


crm_ws_manager = CRMConnectionManager()