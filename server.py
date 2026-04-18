import json
from fastapi import FastAPI, WebSocket
from typing import List

app = FastAPI()

connected_clients: List[WebSocket] = []
locations = {}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            user = json.loads(data)

            user_id = user["user_id"]
            locations[user_id] = user

            # broadcast to all clients
            for client in connected_clients:
                await client.send_text(json.dumps(locations))

    except:
        connected_clients.remove(websocket)