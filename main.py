"""
Agent IA - Rap Tunisien style Samara
Backend FastAPI compatible Groq (GRATUIT) et Anthropic
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from openai import OpenAI  # Groq utilise le SDK OpenAI
from dotenv import load_dotenv
import os
import json
import re
import random
from pathlib import Path

load_dotenv()

# ─── LEXIQUE ──────────────────────────────────────────────
_LEXIQUE_PATH = Path(__file__).parent / "lexique.json"
_LEXIQUE_RAW: dict = json.loads(_LEXIQUE_PATH.read_text(encoding="utf-8"))
# Aplatir toutes les catégories en une seule liste
_ALL_WORDS: list[dict] = [w for cat in _LEXIQUE_RAW.values() for w in cat]

def sample_lexique(n: int = 17) -> str:
    """Retourne n mots aléatoires du lexique formatés pour le prompt."""
    picks = random.sample(_ALL_WORDS, min(n, len(_ALL_WORDS)))
    lines = [f'  • {p["latin"]} ({p["mot"]}) — {p["sens"]}' for p in picks]
    return "\n".join(lines)

app = FastAPI(title="Rap Tunisien Agent", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── CONFIG ───────────────────────────────────────────────
# Groq : https://console.groq.com → API Keys → créer une clé gratuite
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "gsk_VOTRE_CLE_ICI")

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "llama-3.3-70b-versatile"  # Gratuit sur Groq, très bon en fr/darija
# Autres modèles gratuits Groq : "mixtral-8x7b-32768", "gemma2-9b-it"

# ─── PROMPTS ──────────────────────────────────────────────
SYSTEM_PROMPT = """Tu es un ghostwriter expert en rap tunisien, spécialisé dans le style de Samara.

STYLE SAMARA :
- Flow assertif, confiant, puissant, femme forte qui s'assume
- Références culturelles tunisiennes : Tunis, la médina, Carthage, la mer, la fierté nationale
- Langage direct, sans filtre, images visuelles fortes
- Argot darija courant : wAllah, barka, chkoun, ma3ndich, khouya, famma, barsha, mchit,
  mrigel, ndhom, kaml, 3aych, chwiya, sah, yezzi, nheb, 9albi, 3la bali, bdéla, mte3i,
  kif, 7achma, lezmek, fi bledi, ya m3allem, galbi, nbki, na3ref, t3ayecht, bech, heka,
  barra, rabbi, ya rabbi, zbala, fi rassi, chouf, winou
- Rimes riches : darija-darija, fr-fr, ou cross-langue si le son rime
- Chaque ligne dense en syllabes, fluide à rapper

FORMAT JSON OBLIGATOIRE (sans markdown, sans backticks) :
{"sections":[{"label":"Intro","lines":["ligne1","ligne2"]},{"label":"Couplet 1","lines":["ligne1","ligne2","ligne3","ligne4","ligne5","ligne6","ligne7","ligne8"]},{"label":"Refrain","lines":["ligne1","ligne2","ligne3","ligne4"]},{"label":"Couplet 2","lines":["ligne1","ligne2","ligne3","ligne4","ligne5","ligne6","ligne7","ligne8"]},{"label":"Outro","lines":["ligne1","ligne2"]}]}

Labels autorisés : Intro, Couplet 1, Couplet 2, Refrain, Outro, Couplet, Bridge
"""

LANGUE_DESC = {
    "mix60": "Mélange darija tunisien (60%) et français (40%), alternance naturelle.",
    "mix80": "Majoritairement darija tunisien (80%), quelques mots français intercalés.",
    "full":  "Entièrement en darija tunisien. Emprunts courants ok (okay, style, game).",
    "fr":    "Majorité français (70%) avec insertions de darija pour l'authenticité.",
}

FORMAT_DESC = {
    "morceau": "Morceau complet : Intro (4 lignes) + Couplet 1 (8 lignes) + Refrain (4 lignes) + Couplet 2 (8 lignes) + Outro (2 lignes).",
    "couplet": "Un seul couplet de 8 lignes. Pas d'intro ni refrain.",
    "refrain": "Un refrain seul de 4 lignes, très accrocheur, simple à mémoriser.",
}

SCHEME_DESC = {
    "AABB": "Rimes couplées : lignes 1+2 riment, lignes 3+4 riment.",
    "ABAB": "Rimes alternées : ligne 1 rime avec 3, ligne 2 rime avec 4.",
    "ABBA": "Rimes embrassées : ligne 1 rime avec 4, ligne 2 rime avec 3.",
    "AAAA": "Toutes les lignes sur le même son. Ultra percutant.",
}

# ─── MODÈLES ──────────────────────────────────────────────
class RapRequest(BaseModel):
    theme: str = "la confiance en soi et les jaloux"
    format: str = "morceau"   # morceau | couplet | refrain
    langue: str = "mix80"     # mix60 | mix80 | full | fr
    scheme: str = "AABB"      # AABB | ABAB | ABBA | AAAA

class RapResponse(BaseModel):
    sections: list
    raw_text: str
    model_used: str
    tokens_used: int

# ─── ROUTES ───────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def root():
    return """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8"/>
  <title>Rap Tunisien Agent</title>
  <style>
    body{font-family:sans-serif;max-width:700px;margin:40px auto;padding:0 20px;background:#111;color:#eee}
    h1{color:#f90;margin-bottom:4px}
    p{color:#aaa;margin-top:0}
    label{display:block;margin-top:14px;font-size:.85rem;color:#ccc}
    select,input{width:100%;padding:8px;margin-top:4px;background:#222;color:#eee;border:1px solid #444;border-radius:6px;font-size:.95rem}
    button{margin-top:20px;width:100%;padding:12px;background:#f90;color:#111;border:none;border-radius:8px;font-size:1rem;font-weight:bold;cursor:pointer}
    button:hover{background:#ffa}
    #result{margin-top:28px;white-space:pre-wrap}
    .section{background:#1a1a1a;border-left:3px solid #f90;padding:12px 16px;margin-bottom:14px;border-radius:0 8px 8px 0}
    .section h3{margin:0 0 8px;color:#f90;font-size:.9rem;text-transform:uppercase;letter-spacing:.08em}
    .line{padding:3px 0;line-height:1.5}
    .error{color:#f66;background:#2a1111;padding:12px;border-radius:8px}
    #spinner{display:none;margin-top:16px;color:#f90;text-align:center}
  </style>
</head>
<body>
  <h1>🎤 Rap Tunisien Agent</h1>
  <p>Style Samara — powered by Groq (llama-3.3-70b)</p>

  <label>Thème
    <input id="theme" value="la confiance en soi et les jaloux"/>
  </label>

  <label>Format
    <select id="format">
      <option value="morceau">Morceau complet (Intro + 2 couplets + Refrain + Outro)</option>
      <option value="couplet">Couplet seul (8 lignes)</option>
      <option value="refrain">Refrain seul (4 lignes)</option>
    </select>
  </label>

  <label>Langue
    <select id="langue">
      <option value="mix80">Darija 80% + Français 20%</option>
      <option value="mix60">Darija 60% + Français 40%</option>
      <option value="full">Full darija</option>
      <option value="fr">Français 70% + Darija 30%</option>
    </select>
  </label>

  <label>Schéma de rimes
    <select id="scheme">
      <option value="AABB">AABB — rimes couplées</option>
      <option value="ABAB">ABAB — rimes alternées</option>
      <option value="ABBA">ABBA — rimes embrassées</option>
      <option value="AAAA">AAAA — même son partout</option>
    </select>
  </label>

  <button onclick="generate()">Générer les paroles</button>
  <div id="spinner">⏳ Génération en cours...</div>
  <div id="result"></div>

  <script>
    async function generate() {
      const btn = document.querySelector('button');
      const spinner = document.getElementById('spinner');
      const result = document.getElementById('result');
      btn.disabled = true;
      spinner.style.display = 'block';
      result.innerHTML = '';
      try {
        const r = await fetch('/generate', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            theme:  document.getElementById('theme').value,
            format: document.getElementById('format').value,
            langue: document.getElementById('langue').value,
            scheme: document.getElementById('scheme').value,
          })
        });
        const data = await r.json();
        if (!r.ok) { result.innerHTML = `<div class="error">${JSON.stringify(data)}</div>`; return; }
        let html = `<small style="color:#666">Modèle : ${data.model_used} — ${data.tokens_used} tokens</small>`;
        for (const s of data.sections) {
          html += `<div class="section"><h3>${s.label}</h3>`;
          for (const l of s.lines) html += `<div class="line">${l}</div>`;
          html += '</div>';
        }
        result.innerHTML = html;
      } catch(e) {
        result.innerHTML = `<div class="error">Erreur : ${e.message}</div>`;
      } finally {
        btn.disabled = false;
        spinner.style.display = 'none';
      }
    }
  </script>
</body>
</html>"""

@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL, "provider": "Groq (gratuit)"}

@app.post("/generate", response_model=RapResponse)
def generate(req: RapRequest):
    langue_txt = LANGUE_DESC.get(req.langue, LANGUE_DESC["mix80"])
    format_txt = FORMAT_DESC.get(req.format, FORMAT_DESC["morceau"])
    scheme_txt = SCHEME_DESC.get(req.scheme, SCHEME_DESC["AABB"])

    vocab_injection = sample_lexique(17)

    user_message = f"""Génère des paroles rap tunisien style Samara.

Thème : "{req.theme}"
Format : {format_txt}
Langue : {langue_txt}
Schéma de rimes : {req.scheme} — {scheme_txt}

VOCABULAIRE TUNISIEN À INTÉGRER OBLIGATOIREMENT (utilise AU MOINS 12 de ces 17 mots/expressions, répartis dans toutes les sections) :
{vocab_injection}

Ces mots sont authentiquement tunisiens — ne les remplace pas par des équivalents algériens ou marocains.
Rappel : réponds UNIQUEMENT en JSON valide, sans aucun texte avant ou après."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_message}
            ],
            max_tokens=1500,
            temperature=0.85,
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Erreur Groq : {str(e)}")

    raw = response.choices[0].message.content or ""
    tokens = response.usage.total_tokens if response.usage else 0

    # Nettoyage JSON
    clean = re.sub(r"```json|```", "", raw).strip()

    try:
        parsed = json.loads(clean)
        sections = parsed.get("sections", [])
    except json.JSONDecodeError:
        # Fallback : retourner le texte brut dans une section unique
        sections = [{"label": "Paroles", "lines": raw.split("\n")}]

    return RapResponse(
        sections=sections,
        raw_text=raw,
        model_used=MODEL,
        tokens_used=tokens,
    )

# ─── LANCEMENT ────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
