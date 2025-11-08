import logging
from datetime import datetime, timezone
from typing import Optional

from anyio import to_thread
from fastapi import HTTPException, status

from domain.team_builder_domain import (
    LineupFiltersModel,
    LineupMapModel,
    SaveLineupRequest,
    SavedLineupModel,
)
from repositories.team_builder_repository import TeamBuilderRepository


logger = logging.getLogger(__name__)

USERS_COLLECTION = "users"
LINEUP_SUBCOLLECTION = "lineups"
CURRENT_LINEUP_DOC = "current"


class TeamBuilderRepositoryFirebase(TeamBuilderRepository):
    """Firestore implementation for persisting a user's current lineup."""

    def __init__(self, db):
        self.db = db

    def _require_db(self):
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured",
            )

    def _doc_ref(self, user_id: str):
        return (
            self.db.collection(USERS_COLLECTION)
            .document(user_id)
            .collection(LINEUP_SUBCOLLECTION)
            .document(CURRENT_LINEUP_DOC)
        )

    async def get_current_lineup(self, user_id: str) -> Optional[SavedLineupModel]:
        self._require_db()
        doc_ref = self._doc_ref(user_id)

        doc_snapshot = await to_thread.run_sync(doc_ref.get)
        if not doc_snapshot.exists:
            return None

        data = doc_snapshot.to_dict() or {}
        try:
            lineup_map = LineupMapModel(lineup=data.get("lineup", {}))
            filters = LineupFiltersModel(**data.get("filters", {}))
            saved_at = data.get("saved_at") or doc_snapshot.create_time
            updated_at = data.get("updated_at") or doc_snapshot.update_time or saved_at
            return SavedLineupModel(
                id=doc_snapshot.id,
                name=data.get("name", "Lineup"),
                lineup=lineup_map,
                filters=filters,
                team_score=data.get("team_score"),
                team_budget=data.get("team_budget"),
                notes=data.get("notes"),
                is_current=data.get("is_current", True),
                saved_at=saved_at,
                updated_at=updated_at,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Failed to hydrate lineup document for user %s", user_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load saved lineup",
            ) from exc

    async def save_current_lineup(
        self, user_id: str, payload: SaveLineupRequest
    ) -> SavedLineupModel:
        self._require_db()
        doc_ref = self._doc_ref(user_id)

        now = datetime.now(timezone.utc)

        def _upsert():
            doc_snapshot = doc_ref.get()
            saved_at = (
                doc_snapshot.to_dict().get("saved_at")
                if doc_snapshot.exists and doc_snapshot.to_dict()
                else now
            )
            doc_ref.set(
                {
                    "name": payload.name,
                    "lineup": payload.lineup.model_dump(mode="json").get("lineup"),
                    "filters": payload.filters.model_dump(mode="json"),
                    "team_score": payload.team_score,
                    "team_budget": payload.team_budget,
                    "notes": payload.notes,
                    "is_current": True,
                    "saved_at": saved_at,
                    "updated_at": now,
                }
            )
            return saved_at

        saved_at = await to_thread.run_sync(_upsert)

        return SavedLineupModel(
            id=CURRENT_LINEUP_DOC,
            name=payload.name,
            lineup=payload.lineup,
            filters=payload.filters,
            team_score=payload.team_score,
            team_budget=payload.team_budget,
            notes=payload.notes,
            is_current=True,
            saved_at=saved_at,
            updated_at=now,
        )

    async def delete_current_lineup(self, user_id: str) -> None:
        self._require_db()
        doc_ref = self._doc_ref(user_id)

        await to_thread.run_sync(doc_ref.delete)
