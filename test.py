"""
Test rapide de l'agent — lance ce fichier pour vérifier que tout marche
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    r = requests.get(f"{BASE_URL}/health")
    print("✅ Health:", r.json())

def test_generate():
    payload = {
        "theme": "la confiance en soi et les jaloux",
        "format": "couplet",
        "langue": "mix80",
        "scheme": "AABB"
    }
    print("\n🎤 Génération en cours...\n")
    r = requests.post(f"{BASE_URL}/generate", json=payload)
    data = r.json()

    print(f"Modèle : {data['model_used']}")
    print(f"Tokens utilisés : {data['tokens_used']}\n")
    print("─" * 40)

    for section in data["sections"]:
        print(f"\n[{section['label']}]")
        for line in section["lines"]:
            print(f"  {line}")

    print("\n─" * 40)

if __name__ == "__main__":
    test_health()
    test_generate()
