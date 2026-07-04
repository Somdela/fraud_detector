"""
Historique des communications entre numéros.
Stocké en SQLite — aucune dépendance externe.

Logique :
  - Quand le verdict NLP est "uncertain", on vérifie si (sender → recipient)
    ont déjà communiqué. Si jamais → on escalade en "probable_fraud".
  - Chaque SMS légitime confirmé enrichit l'historique.
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "history.db")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS communications (
            sender      TEXT NOT NULL,
            recipient   TEXT NOT NULL,
            first_seen  TEXT NOT NULL,
            last_seen   TEXT NOT NULL,
            msg_count   INTEGER DEFAULT 1,
            PRIMARY KEY (sender, recipient)
        )
    """)
    conn.commit()
    return conn


def have_communicated(sender: str, recipient: str) -> bool:
    """Retourne True si sender a déjà envoyé au moins un message à recipient."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT msg_count FROM communications WHERE sender=? AND recipient=?",
            (sender, recipient)
        ).fetchone()
    return row is not None


def record_communication(sender: str, recipient: str):
    """Enregistre ou met à jour une communication légitime."""
    now = datetime.utcnow().isoformat()
    with _connect() as conn:
        conn.execute("""
            INSERT INTO communications (sender, recipient, first_seen, last_seen, msg_count)
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT(sender, recipient) DO UPDATE SET
                last_seen = excluded.last_seen,
                msg_count = msg_count + 1
        """, (sender, recipient, now, now))
        conn.commit()


def get_dashboard_stats() -> dict:
    """Statistiques globales pour le tableau de bord."""
    with _connect() as conn:
        total_pairs = conn.execute("SELECT COUNT(*) FROM communications").fetchone()[0]
        total_msgs  = conn.execute("SELECT COALESCE(SUM(msg_count), 0) FROM communications").fetchone()[0]
    return {
        "known_pairs": total_pairs,
        "legitimate_messages": total_msgs,
    }


def get_stats(sender: str, recipient: str) -> dict:
    """Retourne les stats de communication entre deux numéros."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT first_seen, last_seen, msg_count FROM communications WHERE sender=? AND recipient=?",
            (sender, recipient)
        ).fetchone()
    if row is None:
        return {"known": False, "msg_count": 0}
    return {
        "known": True,
        "first_seen": row[0],
        "last_seen": row[1],
        "msg_count": row[2],
    }
