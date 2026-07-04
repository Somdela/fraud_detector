import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from api.schemas import (
    SMSRequest, SMSResponse, HealthResponse,
    Verdict, FraudType, CommunicationInfo,
)
from api.predictor import FraudPredictor
from api import history, stats

VERSION = "1.0.0"
predictor: FraudPredictor | None = None
DASHBOARD_HTML = Path(__file__).parent / "dashboard.html"


@asynccontextmanager
async def lifespan(app: FastAPI):
    global predictor
    predictor = FraudPredictor()
    print("Modele charge. API prete.")
    yield


app = FastAPI(
    title="SMS Fraud Detector — Burkina Faso",
    description=(
        "API de detection des SMS frauduleux Mobile Money.\n\n"
        "**Deux couches d'analyse :**\n"
        "1. NLP (contenu du SMS)\n"
        "2. Comportementale (historique de communication sender-recipient)\n\n"
        "| Verdict | Action operateur |\n"
        "|---|---|\n"
        "| `fraud` | Bloquer |\n"
        "| `probable_fraud` | Bloquer + alerter |\n"
        "| `uncertain` | Quarantaine / verif manuelle |\n"
        "| `legitimate` | Livrer |\n"
    ),
    version=VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root():
    return HTMLResponse(content=DASHBOARD_HTML.read_text(encoding="utf-8"))


@app.get("/dashboard", response_class=HTMLResponse, tags=["Dashboard"])
def dashboard():
    """Tableau de bord de surveillance en temps réel."""
    return HTMLResponse(content=DASHBOARD_HTML.read_text(encoding="utf-8"))


@app.get("/stats", tags=["Dashboard"])
def get_stats():
    """Statistiques pour le tableau de bord (rafraîchies toutes les 3s)."""
    summary = stats.get_summary()
    db_stats = history.get_dashboard_stats()
    summary["known_pairs"]          = db_stats["known_pairs"]
    summary["legitimate_messages"]  = db_stats["legitimate_messages"]
    # Données brutes des verdicts pour le donut chart
    summary["fraud_types_raw"] = {
        "fraud":          sum(1 for r in summary["recent"] if r["verdict"] == "fraud"),
        "probable_fraud": sum(1 for r in summary["recent"] if r["verdict"] == "probable_fraud"),
    }
    return summary


@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
def health_check():
    return HealthResponse(
        status="ok",
        model_loaded=predictor is not None,
        version=VERSION,
    )


@app.post("/analyze", response_model=SMSResponse, tags=["Analyse"])
def analyze(request: SMSRequest):
    """
    Analyse un SMS et retourne un verdict.

    - Fournir **sender** + **recipient** active la couche comportementale.
    - Les SMS legitimes confirmes enrichissent automatiquement l'historique.
    """
    if predictor is None:
        raise HTTPException(status_code=503, detail="Modele non disponible.")

    t0 = time.perf_counter()

    # Couche 1 : NLP
    verdict, confidence, fraud_type, reason = predictor.predict(request.sms)

    # Couche 2 : comportementale
    comm_info = None
    if verdict == "uncertain" and request.sender and request.recipient:
        verdict, confidence, fraud_type, reason = predictor.apply_behavioral_layer(
            verdict, fraud_type, confidence, request.sender, request.recipient
        )
        comm_info = CommunicationInfo(**history.get_stats(request.sender, request.recipient))

    # Enregistre la communication si legitime
    if verdict == "legitimate" and request.sender and request.recipient:
        history.record_communication(request.sender, request.recipient)

    elapsed_ms = (time.perf_counter() - t0) * 1000

    # Enregistre pour le dashboard
    stats.record(verdict, fraud_type, request.sms, confidence)

    return SMSResponse(
        verdict=Verdict(verdict),
        confidence=confidence,
        fraud_type=FraudType(fraud_type),
        reason=reason,
        communication_info=comm_info,
        processing_time_ms=round(elapsed_ms, 2),
    )
