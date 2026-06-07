# Agent IA — Rap Tunisien style Samara
Backend FastAPI · Groq (gratuit) · Darija + Français

---

## 1. Obtenir la clé Groq GRATUITE

1. Va sur https://console.groq.com
2. Crée un compte (gratuit, pas de CB requise)
3. Clique sur **API Keys** → **Create API Key**
4. Copie ta clé (commence par `gsk_...`)

---

## 2. Installation

```bash
# Cloner / télécharger le projet, puis :
cd rap_agent

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate      # Mac/Linux
# venv\Scripts\activate       # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer la clé API
cp .env.example .env
# Ouvre .env et remplace gsk_VOTRE_CLE_GROQ_ICI par ta vraie clé
```

---

## 3. Lancement

```bash
# Avec la clé en variable d'environnement
export GROQ_API_KEY=gsk_ta_cle_ici   # Mac/Linux
# set GROQ_API_KEY=gsk_ta_cle_ici    # Windows

python main.py
# → API disponible sur http://localhost:8000
# → Docs interactives sur http://localhost:8000/docs
```

---

## 4. Test

```bash
# Dans un autre terminal :
python test.py
```

---

## 5. Utilisation (exemples curl)

```bash
# Générer un morceau complet
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "la rue et les rêves",
    "format": "morceau",
    "langue": "mix80",
    "scheme": "AABB"
  }'

# Générer un refrain seulement
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "la fierté tunisienne",
    "format": "refrain",
    "langue": "full",
    "scheme": "AAAA"
  }'
```

---

## 6. Paramètres

| Paramètre | Options | Description |
|-----------|---------|-------------|
| `theme`   | texte libre | Sujet du morceau |
| `format`  | `morceau` / `couplet` / `refrain` | Structure générée |
| `langue`  | `mix60` / `mix80` / `full` / `fr` | Ratio darija/français |
| `scheme`  | `AABB` / `ABAB` / `ABBA` / `AAAA` | Schéma de rimes |

---

## 7. Passer à Anthropic (optionnel)

Remplace dans `main.py` :
```python
# Avant (Groq)
client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
MODEL = "llama-3.3-70b-versatile"

# Après (Anthropic)
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-20250514"
# + adapter l'appel API (voir doc Anthropic)
```

---

## 8. Déployer gratuitement sur Replit

1. Va sur https://replit.com → Nouveau projet Python
2. Upload les fichiers `main.py` et `requirements.txt`
3. Dans Secrets, ajoute `GROQ_API_KEY = gsk_ta_cle`
4. Lance avec `uvicorn main:app --host 0.0.0.0 --port 8000`
5. Ton URL publique : `https://ton-projet.ton-user.repl.co`

---

## Limites Groq gratuites

| Modèle | Requêtes/min | Tokens/min | Tokens/jour |
|--------|-------------|------------|-------------|
| llama-3.3-70b | 30 | 6 000 | 100 000 |

Pour un usage perso rap, c'est largement suffisant (environ 300-400 morceaux/jour).
