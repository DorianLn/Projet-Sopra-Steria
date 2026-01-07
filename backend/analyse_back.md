# **Analyse du Backend – Projet Sopra Extraction & Génération Automatique de CV**

##  Fonctionnement Global

Le backend gère un pipeline complet d’analyse et de génération de CV :

1. **Upload d’un CV (PDF/DOCX)**
2. **Conversion PDF → DOCX (si nécessaire)**
3. **Extraction des informations**

   * Regex (emails, dates, téléphones, adresses)
   * spaCy (personnes, organisations)
   * classifier maison (sections : formations, expériences…)
4. **Construction d’un JSON structuré**
5. **Génération automatique d’un CV PDF au format Sopra Steria**
6. **Téléchargement au format PDF ou DOCX**
7. **Conversion d’un DOCX modifié → PDF**

---

##  Structure Actuelle du Backend

```
   backend/
   │── api.py
   │── requirements.txt
   │
   ├── data/
   │   ├── input/
   │   └── output/
   │
   ├── extractors/
   │   ├── extracteur.py
   │   ├── pdf_to_docx.py
   │   ├── section_classifier.py
   │   └── spacy_extractor.py
   │
   ├── generators/
   │   ├── generate_sopra_docx.py
   │   ├── pdf_sopra_profile.py
   │   └── docx_to_pdf.py
   │
   └── analyser_cv.py
```

---

#  Analyse des Modules

---

## 1️ **api.py**

==> *Le cœur du backend, gère toute la logique API.*

### **Rôle**

* Réception du fichier depuis React
* Conversion PDF → DOCX
* Extraction + classification + structuration JSON
* Génération du PDF Sopra
* Routes de téléchargement DOCX & PDF
* Conversion DOCX → PDF

### **Routes principales**

| Route                     | Méthode | Description                                |
| ------------------------- | ------- | ------------------------------------------ |
| `/api/cv/analyze`         | POST    | Analyse un CV et génère un PDF automatique |
| `/api/cv/docx/<filename>` | GET     | Re-crée un DOCX à partir du JSON           |
| `/api/cv/convert`         | POST    | Convertit un DOCX envoyé → PDF             |
| `/api/cv/pdf/<filename>`  | GET     | Télécharge un PDF existant ou le régénère  |

### **Forces**

* Compatible PDF & DOCX
* Nettoyage automatique des fichiers temporaires
* Sécurisé (secure_filename, extensions filtrées)
* Utilise une structure de dossier propre : `data/input` / `data/output`

---

## 2️ **extractors/extracteur.py**

==> *Module d’extraction basé sur regex.*

### Fonctions

* `extraire_dates(texte)`
* `extraire_email(texte)`
* `extraire_telephone(texte)`
* `extraire_adresse(texte)`
* `dedupliquer(liste)`

### Points clés

* Nettoyage automatique
* Normalisation (dates, téléphones)
* Extraction multi-format

---

## 3️ **extractors/pdf_to_docx.py**

==> *Convertit les PDF en DOCX pour normaliser le pipeline.*

### Détails

* Utilise `docx2pdf` ou `pdfplumber`
* Gestion des erreurs robustes
* Retourne False en cas d'échec (sécurise l’API)

---

## 4️ **extractors/spacy_extractor.py**

### Utilisation spaCy

* Extraction intelligente :
  * PERSON
  * ORG
* Nettoyage des entités
* Support complet pour le modèle `fr_core_news_md`

---

## 5️ **extractors/section_classifier.py**

==> *Le module qui reconstruit un CV complet au format JSON structuré.*

### Tâches :

* Répartition automatique des lignes dans :

  * expériences
  * formations
  * compétences
  * langues
  * projets
  * certifications
  * adresse & contact

* Fusion regex + NLP + règles métier

---

## 6️ **generators/generate_sopra_docx.py**

==> *Génère un CV DOCX stylé Sopra.*

### Points forts :

* Templates préconfigurés
* Mise en page professionnelle
* Support unicode et caractères français

---

## 7️ **generators/pdf_sopra_profile.py**

==> *Génère un PDF clean directement depuis JSON.*

* Couleurs Sopra Steria
* Layout moderne
* Sections normalisées

---

## 8️ **generators/docx_to_pdf.py**

==> *Prend un DOCX modifié par l’utilisateur et génère un PDF propre.*

* Utilise Word (COM) → ⚠️ nécessite `pythoncom.CoInitialize()`
* Compatible Windows uniquement

---

#  Pipeline complet (backend)

```
   Upload React
         ↓
   POST /api/cv/analyze
         ↓
   convert_pdf_to_docx()
         ↓
   lire_cv_docx()
         ↓
   extraire_infos_cv()
         ↓
   build_structured_json()
         ↓
   Sauvegarde JSON → data/output
         ↓
   Génération PDF Sopra
         ↓
   Retour JSON + pdf_filename
```

---

#  Points forts du backend

### Très complet

Extraction + NLP + structuration + génération PDF + DOCX + reconversion

### Architecture professionnelle

Modules propres, faciles à maintenir

###  Pipelines robustes

Suppression fichiers temporaires, gestion erreurs, try/except

### Format JSON standardisé

Pratique pour n’importe quel frontend

---

# ⚠️ Points faibles

###  Dépendance Windows COM

La conversion DOCX → PDF via Word ne fonctionne que sur Windows.

###  spaCy chargé à chaque requête

→ peut être optimisé via un chargement global

###  Aucune base de données

→ impossible de stocker des CV analysés automatiquement

###  Pas d’API Swagger

→ documentation moins accessible

---

#  Améliorations recommandées

## Court terme

* Ajouter un logging professionnel
* Ajouter Swagger (Flask-Smorest ou flask-restx)
* Charger spaCy une seule fois au lancement

## Moyen terme

* Stockage MongoDB ou PostgreSQL des CV traités
* Système de cache (évite des traitements répétitifs)
* Prévention des erreurs Word COM (via fallback libreoffice)

## Long terme

* Extraction via modèles ML (HuggingFace)
* Interface d’entraînement maison
* Traitement asynchrone (Celery + Redis)

---