from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.core.config import settings
from app.core.errors import AppError, app_error_handler
from app.errors import install_error_handlers
from app.routers import admin, auth, companies, deals, documents, me, offers, pricing, quotes, refi, risk

app = FastAPI(title="LeaseAI API", version="0.2.0")
app.add_exception_handler(AppError, app_error_handler)
install_error_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(deals.router)
app.include_router(documents.router)
app.include_router(me.router)
app.include_router(offers.router)
app.include_router(pricing.router)
app.include_router(quotes.router)
app.include_router(refi.router)
app.include_router(risk.router)


@app.get("/")
def root() -> dict:
    return {
        "service": "LeaseAI API",
        "version": "0.2.0",
        "docs": "/docs",
        "health": "/health",
        "openapi": "/openapi.json",
    }


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
