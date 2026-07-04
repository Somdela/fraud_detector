"""
Génère des clés API sécurisées pour chaque opérateur.
Usage : python generate_keys.py orange moov gouvernement
"""
import secrets
import sys
import os

def generate_key() -> str:
    return secrets.token_urlsafe(32)

if __name__ == "__main__":
    operators = sys.argv[1:] if len(sys.argv) > 1 else ["orange", "moov", "admin"]

    print("=" * 60)
    print("  CLES API GENEREES — CONFIDENTIEL")
    print("=" * 60)

    keys = []
    for op in operators:
        key = generate_key()
        keys.append(key)
        print(f"\n  Operateur : {op}")
        print(f"  Cle       : {key}")

    print("\n" + "=" * 60)
    print("  Ajoutez cette ligne dans votre fichier .env :")
    print("=" * 60)
    print(f"\n  API_KEYS={','.join(keys)}\n")

    # Écrire dans .env si le fichier n'existe pas encore
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        with open(env_path, "w") as f:
            f.write(f"API_KEYS={','.join(keys)}\n")
        print(f"  Fichier .env cree automatiquement : {env_path}")
    else:
        print(f"  .env existe deja — ajoutez API_KEYS manuellement.")
