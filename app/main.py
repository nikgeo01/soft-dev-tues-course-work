from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.common.error_handlers import register_error_handlers
from app.database import engine
from app.doctors.router import router as doctors_router
from app.patients.router import router as patients_router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Doctor Visit Booking API",
        version="0.1.0",
        lifespan=lifespan,
    )
    register_error_handlers(app)
    app.include_router(auth_router)
    app.include_router(doctors_router)
    app.include_router(patients_router)

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
