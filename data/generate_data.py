import random
import csv
import os

BF_PREFIXES = ['70', '71', '72', '73', '74', '75', '76', '77', '78', '79',
               '60', '61', '62', '63', '64', '65', '66', '67', '68', '69']

NAMES = ['Moussa', 'Fatima', 'Ibrahim', 'Aminata', 'Oumarou', 'Mariam',
         'Hamidou', 'Salimata', 'Adama', 'Aissata', 'Boubacar', 'Rasmata',
         'Issaka', 'Fatoumata', 'Souleymane', 'Rokia', 'Seydou', 'Bintou',
         'Yacouba', 'Kadiatou', 'Drissa', 'Marcelline', 'Wendpanga', 'Awa']

MERCHANTS = ['TOTAL Ouagadougou', 'PHARMACIE du Peuple', 'SUPERMARCHE Score',
             'BOUTIQUE Wend-Yam', 'RESTAURANT La Terrasse', 'STATION Shell',
             'LIBRAIRIE Jeunesse', 'BOULANGERIE Moderne', 'QUINCAILLERIE du Centre']

AMOUNTS = [500, 1000, 2000, 5000, 10000, 25000, 50000, 100000, 200000]
FEES    = [500, 1000, 2000]


def _phone():
    return f"+226{random.choice(BF_PREFIXES)}{random.randint(100000, 999999)}"

def _amount():
    return random.choice(AMOUNTS)

def _name():
    return random.choice(NAMES)

def _ref():
    return f"BF{random.randint(100000000, 999999999)}"

def _date():
    return f"{random.randint(1,28):02d}/{random.randint(1,12):02d}/2026"

def _time():
    return f"{random.randint(8,18):02d}:{random.randint(0,59):02d}"

def _merchant():
    return random.choice(MERCHANTS)


# ── FRAUDES ────────────────────────────────────────────────────────────────────

def fraud_lottery():
    a = _amount()
    templates = [
        f"Félicitations! Vous avez été sélectionné(e) et avez gagné {a} FCFA. Appelez le {_phone()} pour réclamer votre prix.",
        f"ORANGE MONEY TIRAGE: Vous êtes le gagnant de {a} FCFA! Contactez notre agent au {_phone()} dans les 24h.",
        f"Bonne nouvelle! Votre numéro a été tiré au sort. Prix: {a} FCFA. Appelez maintenant le {_phone()}.",
        f"Moov Burkina vous informe que vous avez gagné {a} FCFA lors de notre loterie. Appelez le {_phone()} pour réclamer.",
        f"[PROMOTION] Votre numéro a remporté {a} FCFA! Pour recevoir, envoyez {random.choice(FEES)} FCFA de frais au {_phone()}.",
        f"Vous avez gagné un prix de {a} FCFA. Envoyez {random.choice(FEES)} FCFA pour les frais d'activation au {_phone()}.",
        f"TIRAGE ORANGE BURKINA: Numéro gagnant. Votre récompense: {a} FCFA. Appelez le {_phone()} MAINTENANT.",
        f"Cher client, votre numéro figure parmi les {random.randint(3,10)} gagnants du jour. Prix: {a} FCFA. Appelez {_phone()}.",
    ]
    return random.choice(templates), "lottery_scam"


def fraud_error_transfer():
    a = _amount()
    templates = [
        f"Bonjour, j'ai envoyé {a} FCFA sur votre numéro par erreur. Merci de me rembourser au {_phone()}. Merci.",
        f"Bonsoir, je me suis trompé de numéro en envoyant {a} FCFA. Pouvez-vous me renvoyer cet argent au {_phone()}? Urgent.",
        f"Excusez-moi, j'ai fait une erreur de transfert de {a} FCFA sur votre compte. Merci de retourner l'argent au {_phone()}.",
        f"Cher client, une erreur de transfert de {a} FCFA a été effectuée vers votre numéro. Renvoyez au {_phone()} SVP.",
        f"Monsieur/Madame, j'ai accidentellement envoyé {a} FCFA sur votre numéro. Je vous en supplie de me rembourser au {_phone()}.",
        f"Désolé, mauvaise manipulation. {a} FCFA envoyés par erreur. Merci de renvoyer au {_phone()}. C'est urgent.",
    ]
    return random.choice(templates), "error_transfer"


def fraud_fake_operator():
    templates = [
        f"ORANGE MONEY: Votre compte sera suspendu dans 24h. Appelez immédiatement le {_phone()} pour le débloquer.",
        f"[MOOV MONEY] Activité suspecte détectée sur votre compte. Composez le {_phone()} pour sécuriser votre argent.",
        f"ALERTE ORANGE: Votre compte Mobile Money sera désactivé. Contactez le service client au {_phone()} d'urgence.",
        f"IMPORTANT: Votre compte ORANGE MONEY expire aujourd'hui. Appelez le {_phone()} pour renouveler votre accès.",
        f"[SECURITY] Tentative d'accès non autorisé sur votre compte. Appelez le {_phone()} immédiatement pour bloquer.",
        f"MOOV MONEY: Mise à jour obligatoire de votre compte. Contactez le {_phone()} avant minuit pour éviter la suspension.",
        f"Orange Burkina: Votre numéro sera résilié faute de vérification. Appelez le {_phone()} pour confirmer votre identité.",
    ]
    return random.choice(templates), "fake_operator"


def fraud_pin_request():
    templates = [
        f"Orange Money Service: Veuillez confirmer votre identité en envoyant votre code PIN au {_phone()} pour valider votre compte.",
        f"VERIFICATION MOOV: Envoyez votre code secret au {_phone()} pour débloquer le transfert international.",
        f"Agent Orange Money ici. Pour traiter votre demande, nous avons besoin de votre PIN. Envoyez-le au {_phone()}.",
        f"[ORANGE BURKINA] Pour recevoir votre bonus de {_amount()} FCFA, communiquez votre code PIN au {_phone()}.",
        f"Vérification requise. Envoyez votre code PIN Mobile Money au {_phone()} pour continuer.",
        f"Sécurisation de compte: Nous avons besoin de votre code secret pour protéger votre argent. Envoyez au {_phone()}.",
    ]
    return random.choice(templates), "pin_request"


def fraud_fake_promotion():
    a = _amount()
    f = random.choice(FEES)
    templates = [
        f"PROMO ORANGE: Les {random.randint(10,100)} premiers clients reçoivent {a} FCFA gratuit! Envoyez {f} FCFA d'inscription au {_phone()}.",
        f"MOOV MONEY fête ses {random.randint(5,20)} ans! Recevez {a} FCFA. Frais d'activation: {f} FCFA à envoyer au {_phone()}.",
        f"Offre spéciale! Doublez votre solde. Envoyez {f} FCFA au {_phone()} et recevez {a} FCFA sur votre compte.",
        f"JACKPOT MOBILE: Envoyez seulement {f} FCFA au {_phone()} et gagnez {a} FCFA immédiatement!",
        f"Investissement garanti! Envoyez {f} FCFA au {_phone()} et recevez {a} FCFA dans les 2 heures.",
    ]
    return random.choice(templates), "fake_promotion"


# ── LÉGITIMES ──────────────────────────────────────────────────────────────────

def legit_received():
    a = _amount()
    b = a + random.randint(1000, 50000)
    templates = [
        f"Vous avez reçu {a} FCFA de {_name()}. Nouveau solde: {b} FCFA. Ref: {_ref()}. Le {_date()} a {_time()}.",
        f"ORANGE MONEY: Transfert reçu de {a} FCFA. Expediteur: {_name()}. Solde: {b} FCFA. Ref: {_ref()}.",
        f"Transaction recue: +{a} FCFA de {_name()} ({_phone()}). Solde actuel: {b} FCFA.",
        f"MOOV MONEY: Vous avez recu {a} FCFA de {_name()}. Votre solde est maintenant de {b} FCFA. ID: {_ref()}.",
    ]
    return random.choice(templates), "legitimate"


def legit_sent():
    a = _amount()
    b = random.randint(1000, 50000)
    templates = [
        f"Transfert de {a} FCFA a {_name()} ({_phone()}) effectue. Solde: {b} FCFA. Ref: {_ref()}.",
        f"ORANGE MONEY: {a} FCFA envoyes a {_name()}. Frais: {int(a*0.01)} FCFA. Nouveau solde: {b} FCFA.",
        f"Votre transfert de {a} FCFA a {_phone()} a ete effectue avec succes. Solde restant: {b} FCFA.",
        f"MOOV MONEY: Envoi de {a} FCFA a {_name()} confirme. Solde: {b} FCFA. Ref: {_ref()}.",
    ]
    return random.choice(templates), "legitimate"


def legit_balance():
    b = random.randint(500, 200000)
    templates = [
        f"Votre solde Orange Money est de {b} FCFA au {_date()} a {_time()}.",
        f"MOOV MONEY - Consultation solde: {b} FCFA disponibles sur votre compte.",
        f"Solde disponible: {b} FCFA. Derniere operation le {_date()}. Composez *144# pour plus d'options.",
        f"Orange Money: Solde {b} FCFA. Pour toute operation composez le *144#.",
    ]
    return random.choice(templates), "legitimate"


def legit_topup():
    a = random.choice([500, 1000, 2000, 5000, 10000])
    b = a + random.randint(500, 20000)
    templates = [
        f"Recharge de {a} FCFA creditee sur votre compte. Nouveau solde: {b} FCFA. Merci d'utiliser Orange Money.",
        f"MOOV MONEY: Votre compte a ete rechargé de {a} FCFA. Solde: {b} FCFA.",
        f"Credit de {a} FCFA effectue. Solde Orange Money: {b} FCFA. Ref: {_ref()}.",
    ]
    return random.choice(templates), "legitimate"


def legit_merchant():
    a = _amount()
    b = random.randint(500, 50000)
    templates = [
        f"Paiement de {a} FCFA effectue chez {_merchant()}. Solde: {b} FCFA. Ref: {_ref()}.",
        f"ORANGE MONEY: Achat de {a} FCFA chez {_merchant()} confirme. Nouveau solde: {b} FCFA.",
        f"Transaction marchande: -{a} FCFA ({_merchant()}). Solde restant: {b} FCFA.",
    ]
    return random.choice(templates), "legitimate"


def legit_withdrawal():
    a = _amount()
    b = random.randint(500, 50000)
    templates = [
        f"Retrait de {a} FCFA effectue. Solde: {b} FCFA. Agent: {_name()}. Ref: {_ref()}.",
        f"ORANGE MONEY: Retrait de {a} FCFA confirme. Nouveau solde: {b} FCFA. Ref: {_ref()}.",
        f"MOOV MONEY: Vous avez retire {a} FCFA. Solde disponible: {b} FCFA.",
    ]
    return random.choice(templates), "legitimate"


def legit_notification():
    templates = [
        "Orange Money: Votre compte est actif. Pour toute assistance, appelez le 14 44 (gratuit).",
        "MOOV MONEY: Nouveau service disponible! Payez vos factures SONABEL et ONEA via *555#.",
        "Orange Burkina: Profitez de notre offre speciale data. Composez le *144# pour en savoir plus.",
        "Rappel: Securisez votre compte Orange Money. Ne communiquez jamais votre PIN a personne.",
        "MOOV MONEY vous rappelle: Aucun agent ne vous demandera votre code secret. Signalez toute fraude au 14 45.",
        f"Orange Money: Votre virement vers {_name()} du {_date()} a ete confirme par le beneficiaire.",
        "Orange Burkina: Votre mot de passe a ete modifie avec succes. Si ce n'est pas vous, appelez le 14 44.",
    ]
    return random.choice(templates), "legitimate"


# ── AMBIGUS (mixed signals — label=1 mais confiance faible) ───────────────────

def ambiguous_sms():
    """
    SMS qui ont des signaux mixtes : pas clairement frauduleux,
    pas clairement legitimes. Labelisés fraude car potentiellement dangereux,
    mais créent la zone 'uncertain' dans le modèle.
    """
    templates = [
        f"Bonjour, appelez-moi au {_phone()} pour une information importante vous concernant.",
        f"Votre demande a ete traitee. Contactez le {_phone()} pour confirmation.",
        f"Message urgent de votre operateur. Rappel au {_phone()} necessaire.",
        f"Un agent vous contactera bientot. Pour accelerer, appelez le {_phone()}.",
        f"Votre dossier est en attente. Appelez le {_phone()} pour finaliser.",
        f"Information importante: votre numero {_phone()} a ete enregistre. Confirmez.",
        f"Bonjour, votre demande de service est approuvee. Contactez le {_phone()}.",
        f"Notification: une action est requise sur votre compte. Details au {_phone()}.",
        f"Cher client, votre situation necessite une verification. Appelez {_phone()}.",
        f"Service client: un remboursement de {_amount()} FCFA vous attend. Contactez {_phone()}.",
        f"Vous etes eligible a une offre speciale. Renseignements au {_phone()}.",
        f"Un virement en attente de validation. Confirmez en appelant le {_phone()}.",
    ]
    return random.choice(templates), "ambiguous_fraud"


# ── GENERATION ─────────────────────────────────────────────────────────────────

FRAUD_GENERATORS = [
    fraud_lottery,
    fraud_error_transfer,
    fraud_fake_operator,
    fraud_pin_request,
    fraud_fake_promotion,
    ambiguous_sms,
]

LEGIT_GENERATORS = [
    legit_received,
    legit_sent,
    legit_balance,
    legit_topup,
    legit_merchant,
    legit_withdrawal,
    legit_notification,
]


def generate(n_fraud=700, n_legit=700, seed=42):
    random.seed(seed)
    rows = []

    for _ in range(n_fraud):
        gen = random.choice(FRAUD_GENERATORS)
        text, fraud_type = gen()
        rows.append({"text": text, "label": 1, "fraud_type": fraud_type})

    for _ in range(n_legit):
        gen = random.choice(LEGIT_GENERATORS)
        text, fraud_type = gen()
        rows.append({"text": text, "label": 0, "fraud_type": fraud_type})

    random.shuffle(rows)
    return rows


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    dataset = generate()
    out = "data/dataset.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "label", "fraud_type"])
        writer.writeheader()
        writer.writerows(dataset)

    fraud  = sum(1 for r in dataset if r["label"] == 1)
    legit  = sum(1 for r in dataset if r["label"] == 0)
    print(f"Dataset genere : {len(dataset)} exemples ({fraud} fraudes / {legit} legitimes)")
    print(f"Fichier : {out}")
