from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.errors import AppError, app_error_handler
from app.errors import install_error_handlers
from app.routers import admin, auth, companies, deals, documents, me, pricing, quotes, risk
from app.routers import (
    ai as demo_ai,
    assets as demo_assets,
    billing as demo_billing,
    contracts as demo_contracts,
    dashboards as demo_dashboards,
    demo as demo_control,
    offers as demo_offers,
    refi as demo_refi,
)
from app.services.pdf import write_demo_pdfs

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
write_demo_pdfs(STATIC_DIR)


@asynccontextmanager
async def lifespan(app: FastAPI):
    write_demo_pdfs(STATIC_DIR)
    yield


app = FastAPI(title="LeaseAI API", version="0.2.0", lifespan=lifespan)
app.add_exception_handler(AppError, app_error_handler)
install_error_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# main backend (real DB-backed)
app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(deals.router)
app.include_router(documents.router)
app.include_router(me.router)
app.include_router(pricing.router)
app.include_router(quotes.router)
app.include_router(risk.router)

# demo extras (in-memory state; refi → financier → contract → activation → billing → CFO → AI)
app.include_router(demo_refi.router)
app.include_router(demo_offers.router)
app.include_router(demo_contracts.router)
app.include_router(demo_assets.router)
app.include_router(demo_billing.router)
app.include_router(demo_dashboards.router)
app.include_router(demo_ai.router)
app.include_router(demo_control.router)


@app.get("/")
def root() -> dict:
    return {
        "service": "LeaseAI API",
        "version": "0.2.0",
        "demo_mode": settings.demo_mode,
        "docs": "/docs",
        "health": "/health",
        "openapi": "/openapi.json",
        "demo_users": "/demo/users",
        "auth_hint": (
            "Real endpoints (deals, companies, quotes, documents, pricing, risk, admin, me, auth) "
            "require Supabase Bearer token. Demo extras (refi, offers, contracts, assets, billing, "
            "dashboards, ai, demo) accept X-Demo-Email: <role>@leaseai.demo header in demo mode."
        ),
    }


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/health/info")
def health_info() -> dict:
    return {"status": "ok", "demo_mode": settings.demo_mode, "version": "0.2.0"}
