"""
Script de test manuel de l'API SMS Fraud Detector.

Usage :
  1. Lance le serveur : python -m uvicorn api.main:app --port 8000
  2. Lance les tests  : python test_api.py
"""
import sys
import os
import urllib.request
import json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

API_URL = "http://localhost:8000"


def _load_api_key() -> str:
    """Lit la première clé API depuis le fichier .env local."""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        for line in open(env_path, encoding="utf-8"):
            line = line.strip()
            if line.startswith("API_KEYS="):
                first_key = line.split("=", 1)[1].split(",")[0].strip()
                if first_key:
                    return first_key
    raise RuntimeError(
        "Aucune cle API trouvee dans .env\n"
        "Lance d'abord : python generate_keys.py"
    )


API_KEY = _load_api_key()


def analyze(sms: str, sender: str = None, recipient: str = None) -> dict:
    payload = {"sms": sms}
    if sender:
        payload["sender"] = sender
    if recipient:
        payload["recipient"] = recipient

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{API_URL}/analyze",
        data=data,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": API_KEY,
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def afficher(label: str, result: dict):
    icons = {
        "FRAUD":          "[BLOQUE]",
        "PROBABLE_FRAUD": "[PROBABLE FRAUDE]",
        "UNCERTAIN":      "[INCERTAIN]",
        "LEGITIMATE":     "[LIVRE]",
    }
    verdict = result["verdict"].upper()
    print(f"\n{'-'*55}")
    print(f"  {label}")
    print(f"{'-'*55}")
    print(f"  Verdict    : {icons.get(verdict, verdict)}")
    print(f"  Confiance  : {result['confidence']*100:.1f}%")
    print(f"  Type       : {result['fraud_type']}")
    print(f"  Raison     : {result['reason']}")
    print(f"  Latence    : {result['processing_time_ms']} ms")
    if result.get("communication_info"):
        ci = result["communication_info"]
        print(f"  Historique : {'Oui' if ci['known'] else 'Non'} ({ci['msg_count']} message(s))")


if __name__ == "__main__":
    print("=" * 55)
    print("  TEST API - SMS FRAUD DETECTOR BURKINA FASO")
    print(f"  Cle utilisee : {API_KEY[:12]}...")
    print("=" * 55)

    afficher("1. Arnaque loterie",
        analyze("Felicitations! Vous avez gagne 50000 FCFA. Appelez +22670123456.",
                sender="+22670000001", recipient="+22671000001"))

    afficher("2. Faux operateur (urgence suspension)",
        analyze("ORANGE MONEY: Votre compte sera suspendu dans 24h. Appelez +22671999999.",
                sender="+22671999999", recipient="+22672000001"))

    afficher("3. Erreur de transfert (arnaque classique)",
        analyze("Bonjour, j'ai envoye 10000 FCFA sur votre numero par erreur. Remboursez au +22673111111.",
                sender="+22673111111", recipient="+22674000001"))

    afficher("4. Transfert legitime Orange Money",
        analyze("Vous avez recu 15000 FCFA de Fatima. Nouveau solde: 32500 FCFA. Ref: BF987654321.",
                sender="ORANGE", recipient="+22675000001"))

    afficher("5. Notification systeme legitime",
        analyze("Retrait de 5000 FCFA effectue. Solde: 8200 FCFA. Agent: Moussa. Ref: BF112233445.",
                sender="MOOV", recipient="+22676000001"))

    afficher("6. SMS neutre - numeros JAMAIS en contact → couche comportementale",
        analyze("Salut, ca va? Je suis arrive a Bobo. On se voit demain?",
                sender="+22677000099", recipient="+22678000088"))

    # D'abord enregistrer une communication legitime entre deux numeros
    analyze("Vous avez recu 3000 FCFA de Ibrahim. Solde: 9500 FCFA. Ref: BF555666777.",
            sender="+22679111111", recipient="+22679222222")

    afficher("7. SMS neutre - numeros QUI SE CONNAISSENT → verification humaine",
        analyze("Salut, ca va? Je suis arrive a Bobo. On se voit demain?",
                sender="+22679111111", recipient="+22679222222"))

    print(f"\n{'='*55}")
    print("  Dashboard : http://localhost:8000/dashboard?key=" + API_KEY[:12] + "...")
    print("  Docs      : http://localhost:8000/docs")
    print(f"{'='*55}")
