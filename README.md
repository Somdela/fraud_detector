# SMS Fraud Detector — Burkina Faso

API de détection des SMS frauduleux Mobile Money (Orange Money / Moov Money).

## Problème résolu

Des milliers de burkinabè perdent leur argent chaque mois via des arnaques SMS :
loteries fictives, faux transferts, usurpation d'opérateurs, demandes de code PIN.

Cette API permet aux opérateurs de filtrer automatiquement ces SMS **avant livraison**.

---

## Architecture

```
[SMS entrant] → POST /analyze → [Couche 1 : NLP]
                                       |
                          fraud / legitimate / uncertain
                                       |
                          [Couche 2 : Historique]  ← si uncertain
                           (sender × recipient déjà connus ?)
                                       |
                    probable_fraud / uncertain (vérif humaine)
```

| Verdict | Action recommandée |
|---|---|
| `fraud` | Bloquer |
| `probable_fraud` | Bloquer + alerter |
| `uncertain` | Quarantaine / vérification manuelle |
| `legitimate` | Livrer |

---

## Démarrage rapide

### Prérequis
- Python 3.10+

### Installation locale

```bash
git clone https://github.com/Somdela/fraud_detector.git
cd fraud_detector

pip install -r requirements.txt

# Générer les données synthétiques et entraîner le modèle
python data/generate_data.py
python model/train.py

# Générer les clés API
python generate_keys.py orange moov admin

# Lancer l'API
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Vérifier que tout fonctionne

```bash
python test_api.py
```

---

## Utilisation de l'API

### Authentification

Chaque requête doit inclure le header `X-API-Key` :

```
X-API-Key: votre-cle-api
```

### Analyser un SMS

```http
POST /analyze
Content-Type: application/json
X-API-Key: votre-cle-api

{
  "sms": "Félicitations! Vous avez gagné 50000 FCFA. Appelez le +22670123456.",
  "sender": "+22670123456",
  "recipient": "+22671987654"
}
```

**Réponse :**

```json
{
  "verdict": "fraud",
  "confidence": 1.0,
  "fraud_type": "lottery_scam",
  "reason": "Promesse de gain + demande d'appel ou de frais — arnaque à la loterie classique.",
  "communication_info": null,
  "processing_time_ms": 0.35
}
```

### Exemples par langage

**Python**
```python
import urllib.request, json

def verifier_sms(sms, api_key, sender=None, recipient=None):
    payload = {"sms": sms, "sender": sender, "recipient": recipient}
    req = urllib.request.Request(
        "https://TON-URL.railway.app/analyze",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "X-API-Key": api_key},
        method="POST"
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())
```

**curl**
```bash
curl -X POST https://TON-URL.railway.app/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: votre-cle-api" \
  -d '{"sms": "Vous avez recu 5000 FCFA. Ref: BF123.", "sender": "+22670111222"}'
```

**JavaScript**
```javascript
const r = await fetch("https://TON-URL.railway.app/analyze", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-API-Key": "votre-cle-api"
  },
  body: JSON.stringify({ sms: "Ton SMS ici..." })
});
const data = await r.json();
```

---

## Endpoints

| Méthode | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/health` | Non | État du serveur |
| `POST` | `/analyze` | Oui | Analyser un SMS |
| `GET` | `/dashboard` | Non | Tableau de bord (clé via `?key=`) |
| `GET` | `/stats` | Oui | Données du tableau de bord |
| `GET` | `/docs` | Non | Documentation interactive |

---

## Tableau de bord

Accessible sur `/dashboard?key=votre-cle-api` — se rafraîchit toutes les 3 secondes.

Affiche : total analysé, taux de blocage, types de fraude, 50 dernières détections.

**Données affichées :** uniquement des métadonnées (verdict, type, confiance, longueur du SMS). Le contenu des SMS n'est jamais stocké ni affiché.

---

## Gestion des clés API

```bash
# Générer des clés pour de nouveaux opérateurs
python generate_keys.py orange moov gouvernement

# Révoquer un accès : supprimer sa clé de API_KEYS dans .env puis redémarrer
```

---

## Déploiement sur Railway

1. Fork ce repo sur GitHub
2. Connecte-toi sur [railway.app](https://railway.app)
3. **New Project** → **Deploy from GitHub repo** → sélectionne `fraud_detector`
4. Dans **Variables**, ajoute :
   ```
   API_KEYS=cle-orange,cle-moov,cle-admin
   ```
5. Railway détecte le `Dockerfile` et déploie automatiquement

---

## Types de fraude détectés

| Type | Description |
|---|---|
| `lottery_scam` | Fausse loterie, promesse de gain |
| `error_transfer` | Prétendue erreur de transfert |
| `fake_operator` | Usurpation d'Orange Money / Moov |
| `pin_request` | Demande de code PIN ou secret |
| `fake_promotion` | Fausse promotion avec frais d'activation |

---

## Limites connues

- Le modèle est entraîné sur des données **synthétiques**. Les performances seront améliorées avec de vrais SMS collectés en production.
- L'historique de communication est stocké en mémoire SQLite locale — il se réinitialise au redémarrage du serveur. Pour la persistance, connecter une base PostgreSQL.
- Aucune limite de débit (rate limiting) n'est implémentée pour l'instant.

---

## Licence

Projet open-source. Contributions bienvenues.
