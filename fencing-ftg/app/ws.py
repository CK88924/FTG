from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .game.service import GameService
from .game.models import ActionType
import json
import asyncio

router = APIRouter()
game_service = GameService()

# Global connection manager (Simple version for P1 vs P2)
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        if len(self.active_connections) >= 2:
            await websocket.close(code=1000, reason="Room full")
            return False
        self.active_connections.append(websocket)
        return True

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    connected = await manager.connect(websocket)
    if not connected:
        return

    player_id = len(manager.active_connections) - 1 # 0 or 1
    
    # Start game loop if 2 players connected (or just start for testing)
    # For prototype, we start loop immediately if not running
    if not game_service.running:
        asyncio.create_task(game_service.game_loop(update_callback))

    try:
        while True:
            data = await websocket.receive_text()
            # Parse input from client
            # Format: {"action": "STEP_FORWARD"}
            try:
                msg = json.loads(data)
                action_str = msg.get("action")
                if action_str == "SET_MODE":
                    mode_val = msg.get("value")
                    if mode_val:
                        game_service.set_mode(mode_val)
                elif action_str == "RESTART":
                    game_service.restart_game()
                elif action_str and action_str in ActionType.__members__:
                    game_service.set_player_action(player_id, ActionType[action_str])
            except:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        game_service.stop()

async def update_callback(game_state):
    # Convert Pydantic model to dict for JSON serialization
    await manager.broadcast(game_state.model_dump(mode="json"))
