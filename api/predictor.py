import os
import sys
from typing import Tuple, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from model.naive_bayes import NaiveBayesClassifier

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "model", "fraud_detector.pkl")

FRAUD_KEYWORDS: dict[str, list[str]] = {
    "lottery_scam":   ["gagné", "gagnant", "tirage", "prix", "réclamer", "félicitations", "sélectionné", "remporté"],
    "error_transfer": ["erreur", "trompé", "accidentellement", "rembourser", "retourner", "mauvaise manipulation"],
    "fake_operator":  ["suspendu", "suspension", "bloquer", "bloqué", "désactivé", "expire", "résilié", "activité suspecte"],
    "pin_request":    ["code pin", "pin", "code secret", "communiquez", "envoyez votre code"],
    "fake_promotion": ["doublez", "multipliez", "jackpot", "frais d'activation", "frais d'inscription", "investissement garanti"],
}

REASONS: dict[str, str] = {
    "lottery_scam":   "Promesse de gain + demande d'appel ou de frais — arnaque à la loterie classique.",
    "error_transfer": "Prétend à un transfert erroné pour obtenir un remboursement — technique courante.",
    "fake_operator":  "Imite un opérateur officiel avec urgence pour pousser à appeler un numéro suspect.",
    "pin_request":    "Demande un code PIN ou secret — aucun opérateur légitime ne fait jamais cela.",
    "fake_promotion": "Promet un gain disproportionné contre un paiement de frais — fraude à l'avance.",
    "unknown":        "Plusieurs indicateurs suspects détectés.",
}

FRAUD_THRESHOLD     = 0.97   # au-dessus : fraude certaine
UNCERTAIN_THRESHOLD = 0.55   # entre les deux : ambigu → couche comportementale


class FraudPredictor:
    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Modèle introuvable : {MODEL_PATH}\n"
                "Lancez d'abord : python model/train.py"
            )
        self._model: NaiveBayesClassifier = NaiveBayesClassifier.load(MODEL_PATH)

    def _detect_fraud_type(self, text: str) -> str:
        lower = text.lower()
        for fraud_type, keywords in FRAUD_KEYWORDS.items():
            if any(kw in lower for kw in keywords):
                return fraud_type
        return "unknown"

    def predict(self, text: str) -> Tuple[str, float, str, str]:
        """Couche 1 : analyse NLP du contenu du SMS."""
        proba       = self._model.predict_proba(text)
        fraud_proba = proba.get(1, 0.0)

        if fraud_proba >= FRAUD_THRESHOLD:
            fraud_type = self._detect_fraud_type(text)
            return "fraud", round(fraud_proba, 4), fraud_type, REASONS.get(fraud_type, REASONS["unknown"])

        if fraud_proba >= UNCERTAIN_THRESHOLD:
            fraud_type = self._detect_fraud_type(text)
            return "uncertain", round(fraud_proba, 4), fraud_type, "SMS ambigu — analyse comportementale en cours."

        return "legitimate", round(1.0 - fraud_proba, 4), "none", \
               "Structure conforme aux notifications Mobile Money officielles."

    def apply_behavioral_layer(
        self,
        verdict: str,
        fraud_type: str,
        confidence: float,
        sender: Optional[str],
        recipient: Optional[str],
    ) -> Tuple[str, float, str, str]:
        """
        Couche 2 : si verdict = uncertain ET sender/recipient fournis,
        on vérifie l'historique de communication.
        """
        if verdict != "uncertain" or not sender or not recipient:
            return verdict, confidence, fraud_type, ""

        from api.history import have_communicated
        known = have_communicated(sender, recipient)

        if not known:
            return (
                "probable_fraud",
                round(min(confidence + 0.15, 0.99), 4),
                fraud_type if fraud_type != "none" else "unknown",
                "SMS ambigu ET ces deux numéros n'ont jamais communiqué — risque élevé de fraude.",
            )
        else:
            return (
                "uncertain",
                confidence,
                fraud_type,
                "SMS ambigu mais ces numéros ont déjà communiqué — vérification manuelle recommandée.",
            )
