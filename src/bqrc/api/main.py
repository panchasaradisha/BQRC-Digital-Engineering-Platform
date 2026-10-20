
"""FastAPI application for the BQRC Digital Engineering Platform."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from bqrc.api.nv import router as nv_router


class HealthResponse(BaseModel):
    """Response schema for the backend health endpoint."""

    status: str
    service: str
    version: str


app = FastAPI(
    title="BQRC Digital Engineering Platform API",
    description="Scientific simulation and engineering analysis API for BQRC-01.",
    version="0.1.0",
)

app.include_router(nv_router)


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Report whether the BQRC API application is running."""
    return HealthResponse(
        status="ok",
        service="bqrc-api",
        version=app.version,
    )
