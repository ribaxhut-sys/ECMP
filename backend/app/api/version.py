"""Release provenance endpoint (R6-01).

Values come from build-time / runtime environment variables — never hardcoded
commit SHAs. Defaults of \"unknown\" mean the image was not built via the RC
release pipeline.
"""

from __future__ import annotations

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.core.config import get_settings

router = APIRouter(tags=["operations"])


class VersionResponse(BaseModel):
    version: str = Field(description="Application semantic version (APP_VERSION)")
    git_commit: str = Field(description="Git commit SHA baked at image build time")
    branch: str = Field(description="Git branch baked at image build time")
    build_time: str = Field(description="UTC build timestamp (ISO-8601) baked at image build")
    environment: str = Field(description="Runtime ENVIRONMENT setting")
    git_tree_state: str = Field(
        description="clean|dirty|unknown — whether the build tree matched HEAD"
    )


@router.get(
    "/version",
    response_model=VersionResponse,
    status_code=status.HTTP_200_OK,
    summary="Release artifact provenance",
)
def version() -> VersionResponse:
    """Return build provenance for Git ↔ Image ↔ Container verification."""
    settings = get_settings()
    return VersionResponse(
        version=settings.app_version,
        git_commit=settings.git_commit,
        branch=settings.git_branch,
        build_time=settings.build_time,
        environment=settings.environment,
        git_tree_state=settings.git_tree_state,
    )
