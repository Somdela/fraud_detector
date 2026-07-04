"""
Script de test manuel de l'API SMS Fraud Detector.
Lance le serveur d'abord : python -m uvicorn api.main:app --port 8000
"""
import sys
import urllib.request
import urllib.error
import json

# Force UTF-8 sur les terminaux Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

API_URL = "http://localhost:8000"


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
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def afficher(label: str, result: dict):
    verdict = result["verdict"].upper()
    icons = {
        "FRAUD":          "[BLOQUE]",
        "PROBABLE_FRAUD": "[PROBABLE FRAUDE]",
        "UNCERTAIN":      "[INCERTAIN]",
        "LEGITIMATE":     "[LIVRE]",
    }
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
    print("=" * 55)

    # 1. Arnaque loterie évidente
    afficher(
        "1. Arnaque loterie",
        analyze(
            "Felicitations! Vous avez gagne 50000 FCFA. "
            "Appelez le +22670123456 pour reclamer votre prix.",
            sender="+22670123456",
            recipient="+22671000001",
        ),
    )

    # 2. Fausse urgence opérateur
    afficher(
        "2. Faux opérateur (urgence suspension)",
        analyze(
            "ORANGE MONEY: Votre compte sera suspendu dans 24h. "
            "Appelez immediatement le +22671999999.",
            sender="+22671999999",
            recipient="+22672000001",
        ),
    )

    # 3. Arnaque erreur de transfert
    afficher(
        "3. Erreur de transfert (arnaque classique)",
        analyze(
            "Bonjour, j'ai envoye 10000 FCFA sur votre numero par erreur. "
            "Merci de me rembourser au +22673111111.",
            sender="+22673111111",
            recipient="+22674000001",
        ),
    )

    # 4. Transfert légitime
    afficher(
        "4. Transfert légitime Orange Money",
        analyze(
            "Vous avez recu 15000 FCFA de Fatima. "
            "Nouveau solde: 32500 FCFA. Ref: BF987654321.",
            sender="ORANGE",
            recipient="+22675000001",
        ),
    )

    # 5. Notification légitime
    afficher(
        "5. Notification système légitime",
        analyze(
            "Retrait de 5000 FCFA effectue. Solde: 8200 FCFA. "
            "Agent: Moussa. Ref: BF112233445.",
            sender="MOOV",
            recipient="+22676000001",
        ),
    )

    # 6. SMS personnel neutre entre inconnus → probable_fraud (couche comportementale)
    afficher(
        "6. SMS neutre — numéros JAMAIS en contact → couche comportementale",
        analyze(
            "Salut, ca va? Je suis arrive a Bobo. On se voit demain?",
            sender="+22677000099",
            recipient="+22678000088",
        ),
    )

    # 7. D'abord on enregistre une communication légitime entre deux numéros
    analyze(
        "Vous avez recu 3000 FCFA de Ibrahim. Solde: 9500 FCFA. Ref: BF555666777.",
        sender="+22679111111",
        recipient="+22679222222",
    )
    # Même SMS neutre mais entre numéros qui se connaissent → uncertain
    afficher(
        "7. SMS neutre — numéros QUI SE CONNAISSENT → vérification humaine",
        analyze(
            "Salut, ca va? Je suis arrive a Bobo. On se voit demain?",
            sender="+22679111111",
            recipient="+22679222222",
        ),
    )

    print(f"\n{'='*55}")
    print("  Docs interactives : http://localhost:8000/docs")
    print(f"{'='*55}")
