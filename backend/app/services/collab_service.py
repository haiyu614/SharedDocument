from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from ..core.config import Settings


@dataclass
class CollaboratorState:
    user_id: int
    username: str
    cursor: dict | None = None


@dataclass
class DocumentSession:
    document_id: int
    version: int
    collaborators: Dict[str, CollaboratorState] = field(default_factory=dict)


class CollaborationService:
    """占位协作服务，后续可替换为 Redis 或专门协同引擎。"""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._sessions: Dict[int, DocumentSession] = {}

    async def dispose(self) -> None:
        return None

    def join_session(self, document_id: int, client_id: str, state: CollaboratorState) -> DocumentSession:
        session = self._sessions.setdefault(document_id, DocumentSession(document_id=document_id, version=0))
        session.collaborators[client_id] = state
        return session

    def leave_session(self, document_id: int, client_id: str) -> DocumentSession | None:
        session = self._sessions.get(document_id)
        if not session:
            return None
        session.collaborators.pop(client_id, None)
        if not session.collaborators:
            self._sessions.pop(document_id, None)
        return session

    def update_cursor(self, document_id: int, client_id: str, cursor: dict) -> dict | None:
        session = self._sessions.get(document_id)
        if not session:
            return None
        collaborator = session.collaborators.get(client_id)
        if not collaborator:
            return None
        collaborator.cursor = cursor
        return cursor

    def list_collaborators(self, document_id: int) -> List[CollaboratorState]:
        session = self._sessions.get(document_id)
        if not session:
            return []
        return list(session.collaborators.values())

