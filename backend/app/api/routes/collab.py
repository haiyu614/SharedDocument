from __future__ import annotations

import json
from typing import Dict
from uuid import uuid4

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from ...deps import get_auth_service, get_collaboration_service
from ...services.auth_service import AuthService
from ...services.collab_service import CollaborationService, CollaboratorState


router = APIRouter()


class WebSocketConnectionManager:
    def __init__(self) -> None:
        self._connections: Dict[int, Dict[str, WebSocket]] = {}

    async def connect(self, document_id: int, client_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.setdefault(document_id, {})[client_id] = websocket

    def disconnect(self, document_id: int, client_id: str) -> None:
        self._connections.get(document_id, {}).pop(client_id, None)
        if self._connections.get(document_id) == {}:
            self._connections.pop(document_id, None)

    async def broadcast(self, document_id: int, message: dict, *, exclude: str | None = None) -> None:
        data = json.dumps(message)
        for client_id, connection in self._connections.get(document_id, {}).items():
            if exclude and client_id == exclude:
                continue
            await connection.send_text(data)


manager = WebSocketConnectionManager()


@router.websocket("/ws/{document_id}")
async def document_collaboration(
    websocket: WebSocket,
    document_id: int,
    collab_service: CollaborationService = Depends(get_collaboration_service),
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    token = websocket.query_params.get("token")
    user = None
    if token:
        user = await auth_service.get_current_user(token)

    client_id = websocket.query_params.get("clientId") or uuid4().hex
    username = user.username if user else "guest"
    collaborator_state = CollaboratorState(user_id=user.id if user else 0, username=username)

    await manager.connect(document_id, client_id, websocket)
    collab_service.join_session(document_id, client_id, collaborator_state)
    await manager.broadcast(
        document_id,
        {"type": "user_joined", "clientId": client_id, "username": username},
        exclude=client_id,
    )

    try:
        while True:
            payload = await websocket.receive_json()
            message_type = payload.get("type")

            if message_type == "cursor_update":
                cursor_payload = payload.get("cursor") or {}
                collab_service.update_cursor(document_id, client_id, cursor_payload)
                await manager.broadcast(
                    document_id,
                    {"type": "cursor_update", "clientId": client_id, "cursor": cursor_payload},
                    exclude=client_id,
                )
            elif message_type == "edit_operation":
                await manager.broadcast(
                    document_id,
                    {"type": "edit_operation", "clientId": client_id, "operations": payload.get("operations")},
                    exclude=client_id,
                )
            elif message_type == "heartbeat":
                await websocket.send_json({"type": "heartbeat_ack"})
            else:
                await websocket.send_json({"type": "error", "message": "未知消息类型"})
    except WebSocketDisconnect:
        collab_service.leave_session(document_id, client_id)
        manager.disconnect(document_id, client_id)
        await manager.broadcast(
            document_id,
            {"type": "user_left", "clientId": client_id},
        )

