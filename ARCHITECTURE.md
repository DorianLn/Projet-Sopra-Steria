# 🏗️ ARCHITECTURE MISTRAL - Schéma complet

## Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                   VOTRE APPLICATION SOPRA                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Frontend (React)                                             │
│      ↓                                                        │
│  API Flask (api.py) ← Intégrée avec Mistral ✨               │
│      ↓                                                        │
│  ┌──────────────────────────────────────┐                   │
│  │  Analyse Mistral                     │                   │
│  │  (mistral_analyzer.py)               │                   │
│  └──────────────────────────────────────┘                   │
│      ↓                                                        │
│  Ollama (Serveur local)                                      │
│      ↓                                                        │
│  Mistral 7B (Modèle)                                         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Architecture détaillée

```
┌──────────────────────────────────────────────────────────┐
│                    APPLICATION SOPRA                      │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  Frontend (src/)                                           │
│  ├── App.jsx                                              │
│  ├── pages/                                               │
│  └── components/                                          │
│          ↓                                                │
│  API Flask (backend/api.py)                               │
│  ├── /api/cv/analyze          [Analyse classique]        │
│  ├── /api/mistral/analyze     [Analyse Mistral] ⭐        │
│  ├── /api/mistral/status      [Vérif. status]            │
│  ├── /api/mistral/health      [Health check]             │
│  └── Routes (routes/)                                    │
│      └── mistral_routes.py                               │
│          ↓                                                │
│  Extractors (backend/extractors/)                        │
│  ├── mistral_analyzer.py      [Module Mistral] ⭐        │
│  ├── spacy_extractor.py                                  │
│  ├── pdf_to_docx.py                                      │
│  └── ...                                                 │
│          ↓                                                │
│  ┌─────────────────────────────────────┐                │
│  │   MISTRAL 7B INSTRUCT (LOCAL)       │ ⭐⭐⭐         │
│  │                                     │                │
│  │  HTTP Requests (urllib)             │                │
│  │  ↓                                  │                │
│  │  Ollama Service (localhost:11434)   │                │
│  │  ↓                                  │                │
│  │  Mistral 7B Model                   │                │
│  │  ↓                                  │                │
│  │  JSON Parsing                       │                │
│  │  ↓                                  │                │
│  │  Structured Output                  │                │
│  └─────────────────────────────────────┘                │
│                                                            │
│  Data (backend/data/)                                      │
│  ├── input/      [CVs importés]                            │
│  └── output/     [Résultats JSON]                          │
│                                                            │
└──────────────────────────────────────────────────────────┘
```

---

## Flux de données (Sequence Diagram)

```
User             Frontend          API Flask         Mistral         Ollama
│                    │                 │                │               │
├─ Télécharge CV ───→│                 │                │               │
│                    │                 │                │               │
│                    │─ Envoie texte ─→│                │               │
│                    │                 │                │               │
│                    │                 │─ Appel HTTP ──→│               │
│                    │                 │                │               │
│                    │                 │                │─ API Call ───→│
│                    │                 │                │               │
│                    │                 │                │← JSON Gen ────│
│                    │                 │                │               │
│                    │                 │← Parse JSON ───│               │
│                    │                 │                │               │
│                    │← Résultat JSON ─│                │               │
│                    │                 │                │               │
│← Affiche résultat ─│                 │                │               │
│                    │                 │                │               │
```

---

## Composants principaux

### 1. Module Mistral (`mistral_analyzer.py`)

```
┌─────────────────────────────────────┐
│   MistralCVAnalyzer                 │
├─────────────────────────────────────┤
│                                     │
│  Methods:                           │
│  • __init__(ollama_host)            │
│  • analyze_cv(text)        [Main]   │
│  • is_ollama_running()              │
│  • is_mistral_available()           │
│  • _call_ollama(prompt)             │
│  • _build_prompt(cv_text)           │
│  • _parse_json_response(text)       │
│                                     │
│  Error Handling:                    │
│  • Retries (3x)                     │
│  • Timeout handling                 │
│  • JSON parsing errors              │
│  • Connection errors                │
│                                     │
└─────────────────────────────────────┘
```

### 2. Routes Flask (`mistral_routes.py`)

```
┌─────────────────────────────────────┐
│   Mistral Routes Blueprint          │
├─────────────────────────────────────┤
│                                     │
│  GET /api/mistral/status            │
│  ├─ Returns: setup status           │
│  └─ Code: 200/503                   │
│                                     │
│  POST /api/mistral/analyze          │
│  ├─ Input: {"cv_text": "..."}       │
│  ├─ Returns: Structured JSON        │
│  └─ Code: 200/400/503               │
│                                     │
│  GET /api/mistral/health            │
│  ├─ Returns: health status          │
│  └─ Code: 200/503                   │
│                                     │
└─────────────────────────────────────┘
```

### 3. Communication HTTP

```
Client Request:
┌─────────────────────────────────┐
│ POST /api/mistral/analyze       │
│ Content-Type: application/json  │
│                                 │
│ {                               │
│   "cv_text": "Jean Dupont..."   │
│ }                               │
└─────────────────────────────────┘
            ↓
MistralCVAnalyzer.analyze_cv()
            ↓
HTTP POST to Ollama:
┌─────────────────────────────────┐
│ POST http://localhost:11434/    │
│        api/generate             │
│                                 │
│ {                               │
│   "model": "mistral",           │
│   "prompt": "Analyse ce CV...", │
│   "stream": false,              │
│   "temperature": 0.3            │
│ }                               │
└─────────────────────────────────┘
            ↓
Mistral Model Processing
            ↓
Response from Ollama:
┌─────────────────────────────────┐
│ 200 OK                          │
│                                 │
│ {                               │
│   "response": "{ JSON... }"      │
│ }                               │
└─────────────────────────────────┘
            ↓
Parse & Structure JSON
            ↓
Client Response:
┌─────────────────────────────────┐
│ 200 OK                          │
│ Content-Type: application/json  │
│                                 │
│ {                               │
│   "success": true,              │
│   "data": {                     │
│     "identite": {...},          │
│     "contact": {...},           │
│     ...                         │
│   }                             │
│ }                               │
└─────────────────────────────────┘
```

---

## Dossier Structure

```
backend/
│
├── extractors/
│   ├── mistral_analyzer.py      ⭐ [400+ lines] Module principal
│   ├── spacy_extractor.py
│   ├── huggingface_extractor.py
│   ├── section_classifier.py
│   └── __pycache__/
│
├── routes/
│   ├── __init__.py
│   └── mistral_routes.py        ⭐ [80 lines] Routes Flask
│
├── generators/
│   ├── generate_sopra_docx.py
│   ├── pdf_sopra_profile.py
│   └── docx_to_pdf.py
│
├── data/
│   ├── input/
│   └── output/                  ← Résultats JSON sauvegardés
│
├── models/
│   └── named-entity-recognition/
│
├── api.py                       [Flask Main]
├── setup_ollama.py              ⭐ [250 lines] Setup auto
├── startup.py                   ⭐ [350 lines] Startup script
├── maintenance.py               ⭐ [400 lines] Menu maintenance
├── examples_mistral.py          ⭐ [350 lines] 7 exemples
├── test_mistral.py              ⭐ [300 lines] Tests
├── mistral_menu.bat             ⭐ Menu Windows
├── .env.mistral                 ⭐ Configuration
├── INTEGRATION_MISTRAL.md       ⭐ Guide intégration API
└── requirements.txt
│
docs/
├── MISTRAL_GUIDE.md             ⭐ [400+ lines] Guide complet
└── ... (autres docs)
│
(root)/
├── MISTRAL_README.md            ⭐ README principal
├── MISTRAL_QUICKSTART.md        ⭐ [200 lines] Quick start
├── MISTRAL_SUMMARY.md           ⭐ Résumé technique
├── INTEGRATION_CHECKLIST.md     ⭐ Checklist d'intégration
└── ARCHITECTURE.md              ← Ce fichier

⭐ = Fichiers créés/modifiés pour Mistral
```

---

## Flux de requête complète

```
1. USER ACTION
   └─ Utilisateur importe un CV

2. FRONTEND (React)
   └─ App.jsx → Envoie le texte à l'API

3. API FLASK
   └─ POST /api/mistral/analyze
      ├─ Reçoit le JSON avec cv_text
      ├─ Valide l'input
      └─ Appelle mistral_analyze_cv()

4. MISTRAL ANALYZER
   ├─ is_ollama_running()? ✓
   ├─ is_mistral_available()? ✓
   ├─ _build_prompt(cv_text)
   │  └─ Construit le prompt avec instructions
   └─ _call_ollama(prompt)
      └─ HTTP POST à localhost:11434

5. OLLAMA SERVICE
   ├─ Reçoit la requête
   ├─ Charge le modèle Mistral 7B
   ├─ Exécute l'inférence
   ├─ Génère le JSON
   └─ Retourne la réponse

6. MISTRAL ANALYZER (retour)
   ├─ Reçoit la réponse Ollama
   ├─ _parse_json_response()
   │  └─ Extrait et parse le JSON
   ├─ Valide la structure
   └─ Retourne le résultat

7. API FLASK (retour)
   ├─ Reçoit le résultat
   ├─ Crée la réponse JSON
   └─ Envoie au client

8. FRONTEND (affichage)
   └─ Affiche les résultats à l'utilisateur
```

---

## Gestion d'erreurs

```
┌─ Connection Error ─┐
│                   │
├─ Ollama not running
│  └─ Return None + Log error
│
├─ Mistral not available
│  └─ Return None + Log error
│
├─ HTTP Timeout
│  └─ Retry (max 3 times)
│     └─ If still fails, Return None
│
├─ JSON Parse Error
│  └─ Retry (max 3 times)
│     └─ If still fails, Return None
│
└─ Other Exceptions
   └─ Log + Return None
```

---

## Performance Architecture

```
Mistral 7B Instruct Performance:

Input (CV text)
    ↓
[Tokenization]
    ↓ (~100-500 tokens)
[Model Processing]
    ├─ CPU: 30-60s per CV
    ├─ GPU: 5-15s per CV
    └─ First request: +5-10s (warm-up)
    ↓
[Token Generation]
    ├─ Temperature: 0.3 (déterministe)
    ├─ Max tokens: auto
    └─ Output: ~200-1000 tokens
    ↓
[JSON Parsing & Validation]
    ↓
Output (Structured JSON)
    ↓
Cache/Database (optionnel)
```

---

## Diagramme des composants

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                          │
│                  (Frontend React)                        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              API LAYER (Flask)                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Routes (Flask Blueprints)                      │   │
│  │  ├─ /api/mistral/analyze   (POST)               │   │
│  │  ├─ /api/mistral/status    (GET)                │   │
│  │  └─ /api/mistral/health    (GET)                │   │
│  └──────┬──────────────────────────────────────────┘   │
└─────────┼──────────────────────────────────────────────┘
          │
┌─────────▼──────────────────────────────────────────────┐
│         BUSINESS LOGIC LAYER                            │
│  ┌─────────────────────────────────────────────────┐   │
│  │  MistralCVAnalyzer                              │   │
│  │  ├─ analyze_cv(text)                            │   │
│  │  ├─ is_ollama_running()                         │   │
│  │  ├─ is_mistral_available()                      │   │
│  │  └─ _call_ollama(prompt)                        │   │
│  └──────┬──────────────────────────────────────────┘   │
└─────────┼──────────────────────────────────────────────┘
          │
┌─────────▼──────────────────────────────────────────────┐
│         NETWORK LAYER (HTTP)                            │
│  ┌─────────────────────────────────────────────────┐   │
│  │  urllib.request                                 │   │
│  │  JSON Serialization/Deserialization             │   │
│  └──────┬──────────────────────────────────────────┘   │
└─────────┼──────────────────────────────────────────────┘
          │
┌─────────▼──────────────────────────────────────────────┐
│         OLLAMA SERVICE LAYER                            │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Ollama Server (localhost:11434)                │   │
│  │  ├─ Model Management                           │   │
│  │  ├─ Generation API                             │   │
│  │  └─ Model Caching                              │   │
│  └──────┬──────────────────────────────────────────┘   │
└─────────┼──────────────────────────────────────────────┘
          │
┌─────────▼──────────────────────────────────────────────┐
│         ML MODEL LAYER                                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Mistral 7B Instruct                            │   │
│  │  ├─ Tokenization                                │   │
│  │  ├─ Attention Mechanisms                        │   │
│  │  ├─ Token Generation                            │   │
│  │  └─ Output Processing                           │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## Points d'intégration

### 1. Avec votre analyse classique (Spacy/Regex)
```
CV Input
  ├─ Mistral Analysis ────┐
  │  └─ JSON output       ├─ Merge/Compare ─ Final JSON
  └─ Classical Analysis ──┘
```

### 2. Avec votre base de données
```
Mistral Analysis Output
  ├─ Validate
  ├─ Save to DB
  └─ Return to Client
```

### 3. Avec votre pipeline PDF/DOCX
```
PDF/DOCX
  ├─ Extract Text
  ├─ Send to Mistral
  ├─ Get JSON
  └─ Generate Output (DOCX/PDF)
```

---

## Sécurité & Isolation

```
Internet ──╳────── No External APIs

Client
  ↓
  (HTTPS possible)
  ↓
Firewall
  ↓
API Server (localhost:5000)
  ↓
Ollama (localhost:11434)
  ↓
Mistral Model (LOCAL)
  ↓
No data leaves machine ✓
```

---

## Scalabilité (optionnel)

### Horizontal Scaling
```
Load Balancer
    ↓
┌───┴─────┬──────────┐
│         │          │
API 1   API 2      API 3
  │       │          │
  └───┬───┴─────┬────┘
      │         │
   Ollama 1  Ollama 2  (Multiple Ollama instances)
      │         │
      └─────┬───┘
      Shared Storage (optionnel)
```

### Caching Strategy
```
User Request
  ↓
Check Cache
  ├─ Hit → Return cached result
  └─ Miss → Call Mistral
           └─ Cache result
           └─ Return
```

---

## Monitoring & Logging

```
API Request
    ↓
Logging (INFO/DEBUG/ERROR)
    ↓
Mistral Processing
    ↓
Logging (duration, tokens, status)
    ↓
Response
    ↓
Log Result (success/failure)
    ↓
Monitoring Dashboard (optionnel)
```

---

**🏗️ Architecture complète et modulaire!**

Tous les composants sont découplés et peuvent être:
- Testés indépendamment
- Déployés séparément
- Remplacés sans impacter les autres
- Scalés horizontalement si nécessaire
