from typing import Dict, List, Optional
from uuid import UUID

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[UUID, List[WebSocket]] = {}
        self.admin_connections: List[WebSocket] = []

    async def connect(self, team_id: UUID, websocket: WebSocket):
        await websocket.accept()
        self.register(team_id, websocket)

    def register(self, team_id: UUID, websocket: WebSocket):
        """Register a connection without accepting (assumes already accepted)"""
        self.active_connections.setdefault(team_id, []).append(websocket)

    def register_admin(self, websocket: WebSocket):
        """Register a global admin connection"""
        self.admin_connections.append(websocket)

    def disconnect(self, team_id: UUID, websocket: WebSocket):
        # Use simple get, then remove. guarding against non-existence
        connections = self.active_connections.get(team_id)
        if connections and websocket in connections:
            connections.remove(websocket)
            # Cleanup Refactor: Remove key if empty (Pro Standard)
            if not connections:
                del self.active_connections[team_id]

    def disconnect_admin(self, websocket: WebSocket):
        if websocket in self.admin_connections:
            self.admin_connections.remove(websocket)

    async def broadcast(self, team_id: UUID, message: str):
        team_count = 0
        admin_count = 0

        # 1. Send to Team Members
        if team_id in self.active_connections:
            # Iterate copy to allow modification if needed
            for connection in list(self.active_connections[team_id]):
                try:
                    await connection.send_text(message)
                    team_count += 1
                except Exception as e:
                    print(f"❌ Failed to send to team member: {e}")
                    self.disconnect(team_id, connection)

        # 2. Send to Global Admins
        for connection in list(self.admin_connections):
            try:
                await connection.send_text(message)
                admin_count += 1
            except Exception as e:
                print(f"❌ Failed to send to admin: {e}")
                self.disconnect_admin(connection)

        print(
            f"📤 Broadcast sent to {team_count} team members + {admin_count} admins for team {team_id}"
        )

    async def broadcast_to_all(self, message: str):
        """Broadcast to ALL connected users (team members + admins)"""
        total_count = 0

        # 1. Send to ALL team members across all teams
        for team_id, connections in list(self.active_connections.items()):
            for connection in list(connections):
                try:
                    await connection.send_text(message)
                    total_count += 1
                except Exception as e:
                    print(f"❌ Failed to send to team member: {e}")
                    self.disconnect(team_id, connection)

        # 2. Send to Global Admins
        for connection in list(self.admin_connections):
            try:
                await connection.send_text(message)
                total_count += 1
            except Exception as e:
                print(f"❌ Failed to send to admin: {e}")
                self.disconnect_admin(connection)

        print(f"📤 Broadcast sent to {total_count} total users")


connection_manager = ConnectionManager()
