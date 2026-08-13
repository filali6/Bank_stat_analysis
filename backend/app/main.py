from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.feature_engineering_routes import router as feature_engineering_router
from app.api.categorization_routes import router as categorization_router
from app.api.enrichment_routes import router as enrichment_router
from app.api.lifestyle_intelligence_routes import router as lifestyle_intelligence_router
from app.api.decision_routes import router as decision_router
from app.api.study_routes import router as study_router
from app.db.database import init_db
from app.core.config import settings

app = FastAPI(title="Transaction Enrichment API", version="0.1.0")
init_db()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(enrichment_router)
app.include_router(categorization_router)
app.include_router(feature_engineering_router)
app.include_router(lifestyle_intelligence_router)
app.include_router(decision_router)
app.include_router(study_router)


@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "ok"}