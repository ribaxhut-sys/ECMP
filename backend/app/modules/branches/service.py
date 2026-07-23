"""Branch application service (no FastAPI imports)."""

from __future__ import annotations

from app.modules.branches.repository import BranchRepository
from app.modules.branches.schemas import BranchResponse


class BranchService:
    def __init__(self, repository: BranchRepository) -> None:
        self._repo = repository

    def list(
        self,
        *,
        page: int,
        page_size: int,
        q: str | None = None,
    ) -> tuple[list[BranchResponse], int]:
        rows, total = self._repo.list_page(page=page, page_size=page_size, q=q)
        return [BranchResponse.model_validate(row) for row in rows], total
