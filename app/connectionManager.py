from typing import Dict, List, Optional
from uuid import UUID

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[UUID, List[WebSocket]] = {}

    async def connect(self, team_id: UUID, websocket: WebSocket):
        await websocket.accept()
        # Linear logic: setdefault creates list if missing, then appends
        self.active_connections.setdefault(team_id, []).append(websocket)

    def disconnect(self, team_id: UUID, websocket: WebSocket):
        # Use simple get, then remove. guarding against non-existence
        connections = self.active_connections.get(team_id)
        if connections and websocket in connections:
            connections.remove(websocket)
            # Cleanup Refactor: Remove key if empty (Pro Standard)
            if not connections:
                del self.active_connections[team_id]

    async def broadcast(self, team_id: UUID, message: str):
        # Guard clause (Complexity 1)
        if team_id not in self.active_connections:
            return

        # Iterate copy to allow modification if needed
        # Robustness: existing connections list might change if disconnect happens concurrently
        # making a shallow copy for iteration is safer: list(self.active_connections[team_id])
        for connection in list(self.active_connections[team_id]):
            try:
                await connection.send_text(message)
            except Exception:
                # Remove dead connection immediately
                self.disconnect(team_id, connection)


connection_manager = ConnectionManager()
