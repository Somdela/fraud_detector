"""
Authentification par clé API.

Les clés valides sont lues depuis la variable d'environnement API_KEYS
(liste séparée par des virgules).

Exemple .env :
  API_KEYS=abc123,def456,ghi789

Chaque opérateur reçoit sa propre clé.
"""
import os
from pathlib import Path
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

# Charge le .env si API_KEYS n'est pas déjà dans l'environnement
def _load_dotenv():
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists() and not os.environ.get("API_KEYS"):
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

_load_dotenv()

_header_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)


def _load_keys() -> set[str]:
    raw = os.environ.get("API_KEYS", "")
    return {k.strip() for k in raw.split(",") if k.strip()}


def require_api_key(api_key: str = Security(_header_scheme)) -> str:
    """
    Dépendance FastAPI — à injecter sur chaque endpoint protégé.
    Lève HTTP 401 si la clé est absente ou invalide.
    """
    valid_keys = _load_keys()

    if not valid_keys:
        # Aucune clé configurée → on bloque tout accès par sécurité
        raise HTTPException(
            status_code=503,
            detail="API non configurée : aucune clé API définie (variable API_KEYS manquante)."
        )

    if not api_key or api_key not in valid_keys:
        raise HTTPException(
            status_code=401,
            detail="Clé API invalide ou absente. Ajoutez le header : X-API-Key: <votre-clé>",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return api_key
