from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.appointments.router import router as appointments_router
from app.auth.router import router as auth_router
from app.common.error_handlers import register_error_handlers
from app.database import async_session, engine
from app.doctors.router import router as doctors_router
from app.patients.router import router as patients_router
from app.schedules.router import router as schedules_router
from app.schedules.service import apply_pending_permanent_changes


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    async with async_session() as session:
        await apply_pending_permanent_changes(session)
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
    app.include_router(appointments_router)
    app.include_router(doctors_router)
    app.include_router(patients_router)
    app.include_router(schedules_router)

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
