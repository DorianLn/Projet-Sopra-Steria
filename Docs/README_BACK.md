```md
#  Backend – Analyse et Génération Automatique de CV

##  Description

Ce backend a été développé dans le cadre d’un projet étudiant en partenariat avec **Sopra Steria**.  
Son objectif est d’automatiser le traitement de CV non structurés (PDF ou DOCX) afin de :

- simplifier l’analyse des informations d’un candidat,
- standardiser la présentation de ces données,
- générer automatiquement des documents professionnels (DOCX & PDF),
- tout en respectant les contraintes de **confidentialité** (traitement 100 % local).

L’application analyse un CV grâce à un pipeline avancé mêlant expressions régulières, NLP (spaCy) et classification heuristique.

---

##  Fonctionnalités

### ✔ Fonctionnalités principales (déjà implémentées)

-  Import de CV **PDF** ou **DOCX**
-  Conversion **PDF → DOCX**
-  Extraction d’informations :
  - Nom complet
  - Email
  - Numéro de téléphone
  - Adresse postale
  - Dates clés
  - Expériences professionnelles
  - Formations
  - Compétences
  - Certifications
  - Langues
  - Projets
-  Analyse NLP via **spaCy** (NER + classification texte)
-  Génération automatique :
    - d’un fichier **DOCX standardisé**
    - d’un fichier **PDF branding Sopra Steria**
-  API RESTful complète consommée par le frontend
-  Gestion automatique des fichiers temporaires
-  Traitement 100% local (aucune donnée envoyée à un service externe)

---

###  Évolutions futures

- [ ] OCR pour les PDF scannés
- [ ] Modèle ML pour classifier les sections du CV
- [ ] Templates DOCX personnalisables par collaborateur
- [ ] Historique des analyses
- [ ] Swagger/OpenAPI pour documenter l’API
- [ ] Multilingue (anglais → français)

---

##  Technologies
-----------------------------------------------------------------------------------
| Domaine                    | Outils                                              |
|----------------------------|-----------------------------------------------------|
| **Framework**              | Flask, Flask-CORS                                   |
| **Extraction**             | Regex, spaCy (fr_core_news_md)                      |
| **Manipulation documents** | python-docx, docxtpl, PyPDF2                        |
| **Conversion**             | docx2pdf (Windows), win32com automation             |
| **Génération PDF**         | ReportLab                                           |
| **Analyse date & texte**   | dateparser, rapidfuzz                               |
------------------------------------------------------------------------------------
---

##  Architecture du backend

```

  backend/
  │
  ├── api.py                       # Entrée principale API Flask
  ├── requirements.txt
  │
  ├── data/
  │   ├── input/                   # Fichiers uploadés
  │   └── output/                  # JSON, DOCX, PDF générés
  │
  ├── extractors/
  │   ├── extracteur.py            # Regex : email, téléphone, dates, adresse
  │   ├── pdf_to_docx.py           # Conversion PDF → DOCX
  │   ├── spacy_extractor.py       # NER + NLP
  │   └── section_classifier.py    # Classification formation/expérience
  │
  ├── generators/
  │   ├── generate_sopra_docx.py   # Génération du DOCX structuré
  │   ├── pdf_sopra_profile.py     # Génération du PDF Sopra Steria
  │   └── docx_to_pdf.py           # Conversion DOCX → PDF
  │  
  │  
  │── training/
  │   ├── generate_training_data.py  # génère GENERATED_NER_DATA
  │   ├──training_data.py            # définit NER_TRAINING_DATA + TEXTCAT_TRAINING_DATA
  │   ├──train_ner.py                # entraîne uniquement le NER
  │   ├──train_textcat.py            # entraîne uniquement le TextCat
  │   └──train_pipeline.py           # entraîne NER + TextCat ensemble
  │  
  │  
  └── analyser_cv.py  etc             # Script offline pour tests locaux


##  Installation

### 1. Cloner le projet

```bash
git clone https://github.com/DorianLn/Projet-Sopra-Steria.git
cd Projet-Sopra-Steria/backend
````

### 2. Créer l’environnement Python

```bash
python -m venv venv
venv\Scripts\activate      # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
pip install spacy pymupdf python-docx
```

### 4. Installer spaCy + modèle français

```bash
python -m spacy download fr_core_news_md
```

---

## ▶ Lancer le serveur

```bash
python api.py
```

L’API démarre sur :
==> **[http://localhost:5000](http://localhost:5000)**

---

##  Endpoints API

###  1. Analyse d’un CV

**POST** `/api/cv/analyze`

**Body** : FormData

```
file: <PDF ou DOCX>
```

**Réponse :**

```json
    {
      "contact": {...},
      "formations": [...],
      "experiences": [...],
      "competences": [...],
      "json_filename": "CV_Victor_Hugo.json",
      "pdf_filename": "CV_Victor_Hugo.pdf"
    }
```

---

###  2. Télécharger le DOCX généré

**GET** `/api/cv/docx/<filename>`

---

###  3. Convertir un DOCX importé en PDF

**POST** `/api/cv/convert`

---

###  4. Télécharger un PDF généré

**GET** `/api/cv/pdf/<filename>`

---

##  Pipeline de traitement

```
    Upload CV
      ↓
    Conversion PDF → DOCX (si besoin)
      ↓
    Lecture texte (python-docx)
      ↓
    Extraction regex
      ↓
    Analyse NLP (spaCy)
      ↓
    Classification heuristique (section_classifier)
      ↓
    Construction du JSON structuré
      ↓
    Génération DOCX + Génération PDF
      ↓
    Réponse API
```

---

##  Roadmap

### Phase 1 : Extraction (complétée)

* ✔ Conversion PDF → DOCX
* ✔ Extraction regex
* ✔ Première version NLP

### Phase 2 : Génération (complétée)

* ✔ DOCX structuré
* ✔ PDF branding Sopra Steria

### Phase 3 : API & Frontend (en cours)

* ✔ API analyse CV
* ✔ Export DOCX/PDF
* ✔ Connexion frontend

### Phase 4 : Améliorations

*  Optimisation extraction
*  OCR pour PDF scannés
*  Templates multiples

---

## 👥 Contributeurs

* Safae Berrichi
* Dorian Lo Negro
* Thomas Gaugeais
* Julien Thepaut
* Nehade El Mokhtari
* Clément

---

## 📜 Licence

Projet réalisé dans le cadre d’un partenariat pédagogique avec **Sopra Steria**.Tous droits réservés.

```