"""
Compteurs en mémoire pour le tableau de bord.
Remis à zéro au redémarrage — suffisant pour un MVP.
"""
from collections import defaultdict
from datetime import datetime
from threading import Lock

_lock = Lock()

_counters = {
    "total": 0,
    "fraud": 0,
    "probable_fraud": 0,
    "uncertain": 0,
    "legitimate": 0,
}

_fraud_types = defaultdict(int)
_recent: list[dict] = []   # 50 dernières détections
MAX_RECENT = 50


def record(verdict: str, fraud_type: str, sms_preview: str, confidence: float):
    with _lock:
        _counters["total"] += 1
        if verdict in _counters:
            _counters[verdict] += 1

        if fraud_type not in ("none", "unknown"):
            _fraud_types[fraud_type] += 1

        entry = {
            "time": datetime.utcnow().strftime("%H:%M:%S"),
            "verdict": verdict,
            "fraud_type": fraud_type,
            "confidence": round(confidence * 100, 1),
            "preview": sms_preview[:60] + ("..." if len(sms_preview) > 60 else ""),
        }
        _recent.insert(0, entry)
        if len(_recent) > MAX_RECENT:
            _recent.pop()


def get_summary() -> dict:
    with _lock:
        total = _counters["total"] or 1  # évite division par zéro
        blocked = _counters["fraud"] + _counters["probable_fraud"]
        return {
            "total_analyzed": _counters["total"],
            "blocked":        blocked,
            "uncertain":      _counters["uncertain"],
            "legitimate":     _counters["legitimate"],
            "block_rate":     round(blocked / total * 100, 1),
            "fraud_types":    dict(_fraud_types),
            "recent":         list(_recent),
        }
