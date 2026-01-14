# 🎯 Projet Sopra Steria - Analyse et Génération Automatique de CV

## 📋 Description

Application complète d'analyse et de génération automatique de CV développée en partenariat avec **Sopra Steria**.

### ✨ Fonctionnalités

- 📄 **Import de CV** : Support PDF et DOCX
- 🔍 **Extraction intelligente** : NLP (spaCy) + règles heuristiques
- 📊 **Analyse structurée** : Nom, contact, expériences, formations, compétences, langues
- 📝 **Génération automatique** : Documents DOCX et PDF au format Sopra Steria
- 🔒 **100% local** : Aucune donnée envoyée à des services externes

---

## 🏗️ Architecture

```
Projet-Sopra-Steria/
├── backend/                    # API Flask + Extraction NLP
│   ├── api.py                  # Point d'entrée API REST
│   ├── extractors/             # Modules d'extraction
│   │   ├── spacy_extractor.py  # NER spaCy entraîné
│   │   ├── extracteur.py       # Extraction regex
│   │   ├── heuristic_rules.py  # Règles heuristiques
│   │   └── section_classifier.py
│   ├── generators/             # Génération documents
│   │   ├── generate_sopra_docx.py
│   │   └── pdf_sopra_profile.py
│   ├── models/                 # Modèles spaCy entraînés
│   │   ├── cv_ner/             # NER personnalisé
│   │   └── cv_pipeline/        # Pipeline complet
│   └── training/               # Scripts d'entraînement
│
├── frontend/                   # Interface React + Vite
│   └── src/
│
└── Docs/                       # Documentation technique
```

---

## 🚀 Lancement rapide

### Prérequis

- **Python 3.10+** → https://python.org
- **Node.js 18+** → https://nodejs.org

### Démarrer l'application

```bash
python launcher.py
```

Ou double-cliquez sur `start.bat`

Le script installe automatiquement toutes les dépendances (venv Python, npm, modèle spaCy) lors du premier lancement.

### Configurer le domaine personnalisé (optionnel)

Pour accéder à l'application via `http://cv.soprasteria.com:5173` :

1. Clic droit sur `setup_domain.bat` → **Exécuter en tant qu'administrateur**
2. Relancez `python launcher.py`

Sans cette configuration, l'application reste accessible sur `http://localhost:5173`.

---

## 🔌 API Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/api/cv/analyze` | Analyser un CV (PDF/DOCX) |
| `GET` | `/api/cv/docx/<filename>` | Télécharger le DOCX généré |
| `GET` | `/api/cv/pdf/<filename>` | Télécharger le PDF généré |
| `POST` | `/api/cv/convert` | Convertir DOCX en PDF |

### Exemple

```bash
curl -X POST -F "file=@mon_cv.pdf" http://localhost:5000/api/cv/analyze
```

---

## 🧠 Pipeline de traitement

```
Upload CV (PDF/DOCX)
       ↓
Conversion PDF → DOCX (si nécessaire)
       ↓
┌─────────────────────────────────────┐
│           EXTRACTION                │
│  • Regex (email, téléphone, dates)  │
│  • spaCy NER (noms, organisations)  │
│  • Règles heuristiques (sections)   │
└─────────────────────────────────────┘
       ↓
JSON Structuré
       ↓
   ┌───┴───┐
   ↓       ↓
 DOCX     PDF
Sopra    Sopra
```

---

## 🧪 Tests

```bash
cd backend

# Lancer tous les tests
pytest

# Tests spécifiques
pytest test_integration.py -v
pytest test_nom_prenom.py -v
```

---

## 📚 Documentation

- [README Backend](Docs/README_BACK.md)
- [README Frontend](Docs/README_FRONT.md)
- [Fonctionnement du Projet](Docs/fonctionnement_du_projet.md)

---

## 🔧 Réentraîner les modèles

Les modèles spaCy personnalisés sont dans `backend/models/`. Pour les réentraîner :

```bash
cd backend
python train_cv_pipeline.py
```

---

## 👥 Contributeurs

- Safae Berrichi
- Dorian Lo Negro
- Thomas Gaugeais
- Julien Thepaut
- Nehade El Mokhtari
- Clément

---

## 📜 Licence

Projet réalisé dans le cadre d'un partenariat pédagogique avec **Sopra Steria**.  
Tous droits réservés.
