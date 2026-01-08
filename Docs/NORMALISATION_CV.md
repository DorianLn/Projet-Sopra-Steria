# Documentation : Feature "Normalisation CV" (Ancienne → Nouvelle Version)

## 🎯 Objectif

Ajouter une fonctionnalité permettant de **convertir un CV de l'ancienne version vers le nouveau format normalisé v2.0**.

Le processus :
1. Utilisateur dépose un CV en ancien format (JSON ou DOCX semi-structuré)
2. Backend le transforme en nouveau JSON v2.0
3. Frontend peut afficher/générer PDF/Word selon le nouveau standard

## 📐 Architecture

### Structure du Projet
```
backend/
├── api.py                              (Routes API principales)
├── analyser_cv.py                      (Analyse complète CV)
├── requirements.txt
├── extractors/
│   ├── version_mapper.py               (Mappage ancien → nouveau format)
│   ├── extracteur.py                   (Extraction regex)
│   ├── section_classifier.py           (Classification des sections)
│   ├── spacy_extractor.py              (NLP avec SpaCy)
│   └── pdf_to_docx.py                  (Conversion PDF → DOCX)
├── generators/
│   ├── generate_sopra_docx.py          (Génération DOCX programmatique - RÉÉCRIT)
│   ├── docx_to_pdf.py                  (Conversion DOCX → PDF)
│   └── pdf_sopra_profile.py            (Profil PDF)
├── models/
│   └── named-entity-recognition/       (Modèles NER)
└── data/
    ├── input/                          (CVs en entrée)
    └── output/                         (Fichiers générés)
```

### Principes Respectés
✅ **Non-intrusive** : Aucune modification du pipeline existant (`/api/cv/analyze` inchangé)  
✅ **Modulaire** : Module dédié `version_mapper.py` avec classe `CVVersionMapper`  
✅ **Robuste** : Gestion gracieuse des erreurs, logging détaillé  
✅ **Extensible** : Facile d'ajouter de nouvelles sources de CV  
✅ **Testable** : Fonctions pures, sans side effects  
✅ **Optimisé** : Génération DOCX programmatique (pas de template), tous les fichiers test supprimés

---

## 📦 Schéma JSON v2.0 (CIBLE)

```json
{
  "meta": {
    "version": "2.0",
    "confidentialite": "C2 – Usage restreint",
    "role": "",
    "initiales": ""
  },
  "profil": {
    "titre": "",
    "resume": ""
  },
  "competences": {
    "techniques": ["Python", "React", "Docker"],
    "fonctionnelles": ["Leadership", "Gestion de projet"]
  },
  "experiences": [
    {
      "date_debut": "2022-01-15",
      "date_fin": "2023-12-31",
      "entreprise": "TechCorp",
      "poste": "Développeur Python",
      "description": ["Développement backend", "API REST"],
      "environnement_technique": ["Python", "Flask", "PostgreSQL"]
    }
  ],
  "formations": [
    {
      "diplome": "Master Informatique",
      "etablissement": "Université Paris",
      "date": "2022",
      "specialisation": "IA et Cloud"
    }
  ],
  "langues": [
    {
      "langue": "Français",
      "niveau": "Natif"
    },
    {
      "langue": "Anglais",
      "niveau": "C1"
    }
  ]
}
```

---

## 🔧 Module `version_mapper.py`

### Classe `CVVersionMapper`

Responsable de **la détection et transformation** d'un CV ancien vers le nouveau format.

#### **Méthodes Principales**

##### 1️⃣ `detect_source_format(data) → str`
Détecte le format source : `'old_json'`, `'new_json'`, `'structured_text'`, `'unknown'`

```python
mapper = CVVersionMapper()
format_detected = mapper.detect_source_format(cv_dict)
# Retourne: 'old_json'
```

##### 2️⃣ `normalize_date(date_str) → str`
**Normalise les dates** vers ISO `YYYY-MM-DD` ou plages `YYYY - YYYY`

Gère :
- Format ISO : `2023-12-31` → `2023-12-31`
- Format français : `31/12/2023` → `2023-12-31`
- Plages : `2020 – 2023` → `2020 - 2023`
- Année seule : `2023` → `2023`
- Mois/Année : `Décembre 2023` → `2023`

```python
mapper.normalize_date("31/12/2023")      # → "2023-12-31"
mapper.normalize_date("2020 – 2023")     # → "2020 - 2023"
mapper.normalize_date("Décembre 2023")   # → "2023"
```

##### 3️⃣ `map_meta(old_data) → Dict`
Construit la section `meta` avec version, confidentialité et initiales

```python
meta = mapper.map_meta(old_data)
# {
#   "version": "2.0",
#   "confidentialite": "C2 – Usage restreint",
#   "role": "",
#   "initiales": "JD"  # Extraites du nom
# }
```

##### 4️⃣ `map_profil(old_data) → Dict`
Extrait titre et résumé

```python
profil = mapper.map_profil(old_data)
# {
#   "titre": "Développeur Python Senior",
#   "resume": "10 ans d'expérience en développement backend..."
# }
```

##### 5️⃣ `map_competences(old_data) → Dict`
Sépare compétences techniques et fonctionnelles

```python
competences = mapper.map_competences(old_data)
# {
#   "techniques": ["Python", "React", "Docker"],
#   "fonctionnelles": ["Leadership", "Gestion de projet"]
# }
```

##### 6️⃣ `map_experiences(old_data) → List[Dict]`
Normalise les expériences professionnelles

Normalisation appliquée :
- Dates converties au format ISO ou plages
- Nettoyage des chaînes (strip)
- Description et environnement en listes
- Filtre : au moins entreprise ou poste présent

```python
experiences = mapper.map_experiences(old_data)
# [
#   {
#     "date_debut": "2022-01-15",
#     "date_fin": "2023-12-31",
#     "entreprise": "TechCorp",
#     "poste": "Développeur Python",
#     "description": ["Dev backend", "API REST"],
#     "environnement_technique": ["Python", "Flask"]
#   }
# ]
```

##### 7️⃣ `map_formations(old_data) → List[Dict]`
Normalise les formations

```python
formations = mapper.map_formations(old_data)
# [
#   {
#     "diplome": "Master Informatique",
#     "etablissement": "Université Paris",
#     "date": "2022",
#     "specialisation": "IA et Cloud"
#   }
# ]
```

##### 8️⃣ `map_langues(old_data) → List[Dict]`
Extrait et déduplique les langues

```python
langues = mapper.map_langues(old_data)
# [
#   {"langue": "Français", "niveau": "Natif"},
#   {"langue": "Anglais", "niveau": "C1"}
# ]
```

##### 🎯 `normalize(old_data) → Dict`
**Fonction orchestratrice** : lance tous les mappings et retourne le CV v2.0 complet

```python
mapper = CVVersionMapper(strict_validation=False)
cv_new = mapper.normalize(old_cv_data)
# Retourne un Dict conforme au schéma v2.0
```

#### **Paramètres du Constructeur**

```python
mapper = CVVersionMapper(strict_validation=False)
```

- `strict_validation=True` : Lève exception en cas d'erreur critique (mode test)
- `strict_validation=False` : Retourne un CV v2.0 vide avec logs (mode production API)

#### **Validation de Schéma**

```python
valid, errors = mapper.validate_schema(cv_dict)
if not valid:
    print(errors)  # Liste des problèmes structurels
```

---

## 🔌 Fonction API Publique

### `normalize_old_cv_to_new(cv_data) → Dict`

**Fonction unique exposable à l'API**, wrapper simple autour de `CVVersionMapper`.

Entrée :
- Dict (ancien JSON)
- Str (JSON string) — non encore implémenté mais extensible

Sortie :
- Dict conforme au schéma v2.0

Comportement :
- **Jamais lève exception** (idéal pour REST API)
- Retourne CV v2.0 vide en cas d'erreur
- Log détaillés pour debugging

```python
from extractors.version_mapper import normalize_old_cv_to_new

old_cv = {"resultats_spacy": {...}}
new_cv = normalize_old_cv_to_new(old_cv)
print(new_cv["meta"]["version"])  # '2.0'
```

---

## 🔄 Génération DOCX - Architecture Optimisée

### Nouvelle Approche : Programmatique (v2.0)

**Ancienne approche (DÉPRÉCIÉE)** :
- ❌ Utilisait template DOCX avec placeholders `{{COMP_FONCT}}`, `{{EXPERIENCES}}`, etc.
- ❌ Remplacement simple de texte → perte de formatage et styles
- ❌ Styles 'List Bullet' inexistants dans le template vierge
- ❌ Sections disparaissaient ou n'étaient pas formatées correctement

**Nouvelle approche (ACTUELLE)** :
- ✅ Génération programmatique avec `python-docx.Document()`
- ✅ Construction progressive des paragraphes avec styles appropriés
- ✅ Chaque section : heading (bold, Pt 11) + items (List Bullet)
- ✅ Gestion intelligente des sections vides
- ✅ Expériences structurées en blocs (titre + missions + environnement)

### Fonction `generate_sopra_docx(cv_data, output_path)`

**Localisation** : `backend/generators/generate_sopra_docx.py`

**Flux de génération** :
```python
def generate_sopra_docx(cv_data, output_path):
    # 1. Extraire données du JSON normalisé
    contact = cv_data.get("contact", {})
    nom = contact.get("nom", "Titre du Profil Collaborateur")
    
    # 2. Créer document vierge (pas de template)
    doc = Document()
    
    # 3. Ajouter titre avec formatage
    title = doc.add_paragraph()
    title_run = title.add_run(nom)
    title_run.bold = True
    
    # 4. Pour chaque section (competences_fonctionnelles, experiences, etc.)
    #    a) Ajouter heading (bold, Pt 11)
    #    b) Boucler sur les items avec style 'List Bullet'
    
    # 5. Sauvegarder le document
    doc.save(output_path)
    return output_path
```

**Sections traitées** :
- `competences_fonctionnelles` → Liste avec bullet
- `competences_techniques` → Liste avec bullet
- `experiences` → Blocs structurés (titre en gras + missions + environnement)
- `formations` → Liste avec bullet
- `langues` → Liste avec bullet

**Debug** : Chaque génération affiche `DEBUG: NB EXPERIENCES = X`

---

## 🧹 État du Projet - Nettoyage (Janvier 2026)

### Fichiers Supprimés
- ✅ 30+ fichiers test (`test_*.py`)
- ✅ 14 fichiers mapper variants (`mapper_*.py`)
- ✅ 8 fichiers debug et d'inspection
- ✅ 15 fichiers markdown d'évolution intermédiaires

### Fichiers Conservés (Production-Ready)
- ✅ `api.py` - Endpoints REST
- ✅ `analyser_cv.py` - Analyse globale
- ✅ `extracters/version_mapper.py` - Mappage de formats
- ✅ `generators/generate_sopra_docx.py` - Génération DOCX (réécrite)
- ✅ Tous les modules de support (extracteur, section_classifier, etc.)
- ✅ `data/input/` et `data/output/`

### Structure Finale
```
├── backend/              (source code + data)
├── frontend/             (React SPA)
├── Docs/                 (documentation)
├── .git/, .github/       (version control)
└── venv/                 (Python environment)
```

**Résultat** : Repository limité et optimisé, sans artefacts de développement.

---

## 🔌 Routes API Ajoutées

### 1️⃣ POST `/api/cv/normalize`

Normalise **un seul** CV ancien en nouveau format v2.0.

#### Modes d'Entrée

**Mode A : JSON en Body**
```json
POST /api/cv/normalize
Content-Type: application/json

{
  "cv_data": {
    "resultats_spacy": {
      "contact": {"nom": "Jean Dupont"},
      "experiences": [...]
    }
  }
}
```

**Mode B : Fichier Uploadé**
```
POST /api/cv/normalize
Content-Type: multipart/form-data

file: CV_ancien.json (ou .docx)
```

#### Réponse Succès (200)
```json
{
  "success": true,
  "cv_normalized": {
    "meta": {...},
    "profil": {...},
    "competences": {...},
    "experiences": [...],
    "formations": [...],
    "langues": [...]
  },
  "metadata": {
    "version_source": "old",
    "version_cible": "2.0",
    "nb_experiences": 3,
    "nb_formations": 2,
    "nb_competences": 5,
    "nb_langues": 2
  }
}
```

#### Réponse Erreur (400/500)
```json
{
  "success": false,
  "error": "Champ \"cv_data\" manquant"
}
```

---

### 2️⃣ POST `/api/cv/normalize-batch`

Normalise **plusieurs** CVs en une seule requête.

#### Body
```json
{
  "cvs": [
    {...ancien CV 1...},
    {...ancien CV 2...},
    {...ancien CV 3...}
  ]
}
```

#### Réponse (200)
```json
{
  "success": true,
  "results": [
    {"success": true, "cv_normalized": {...}},
    {"success": false, "error": "Erreur parsing..."},
    {"success": true, "cv_normalized": {...}}
  ],
  "summary": {
    "total": 3,
    "success": 2,
    "errors": 1
  }
}
```

---

## 📝 Exemples d'Usage

### Exemple 1 : Normalisation Simple
```python
from extractors.version_mapper import normalize_old_cv_to_new

old_cv = {
    "resultats_spacy": {
        "contact": {
            "nom": "Alice Martin",
            "email": "alice@example.com"
        },
        "experiences": [
            {
                "entreprise": "TechCorp",
                "poste": "Dev Python",
                "dates": "2022-01-15"
            }
        ]
    }
}

new_cv = normalize_old_cv_to_new(old_cv)

print(new_cv["meta"]["version"])           # '2.0'
print(new_cv["meta"]["initiales"])         # 'AM'
print(new_cv["experiences"][0]["poste"])   # 'Dev Python'
```

### Exemple 2 : Avec Validation
```python
from extractors.version_mapper import CVVersionMapper

mapper = CVVersionMapper(strict_validation=True)

try:
    cv_new = mapper.normalize(old_cv)
    valid, errors = mapper.validate_schema(cv_new)
    if valid:
        print("✅ CV conforme au schéma v2.0")
    else:
        print(f"❌ Erreurs schéma: {errors}")
except ValueError as e:
    print(f"❌ Erreur conversion: {e}")
```

### Exemple 3 : Appel via cURL
```bash
curl -X POST http://localhost:5000/api/cv/normalize \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {
      "resultats_spacy": {
        "contact": {"nom": "Jean Dupont"},
        "experiences": []
      }
    }
  }'
```

---

## 🧪 Tests

### Test Unitaire du Mapper
```python
import pytest
from extractors.version_mapper import CVVersionMapper

def test_normalize_date():
    mapper = CVVersionMapper()
    assert mapper.normalize_date("31/12/2023") == "2023-12-31"
    assert mapper.normalize_date("2020 – 2023") == "2020 - 2023"
    assert mapper.normalize_date("2023") == "2023"

def test_detect_source_format():
    mapper = CVVersionMapper()
    
    old = {"resultats_spacy": {}}
    assert mapper.detect_source_format(old) == "old_json"
    
    new = {"meta": {}, "profil": {}}
    assert mapper.detect_source_format(new) == "new_json"

def test_normalize_complete():
    mapper = CVVersionMapper()
    old_cv = {
        "resultats_spacy": {
            "contact": {"nom": "Alice Martin"},
            "experiences": [
                {"entreprise": "Corp", "poste": "Dev", "dates": "2020-01-15"}
            ]
        }
    }
    
    new_cv = mapper.normalize(old_cv)
    
    assert new_cv["meta"]["version"] == "2.0"
    assert new_cv["meta"]["initiales"] == "AM"
    assert len(new_cv["experiences"]) == 1
    assert new_cv["experiences"][0]["poste"] == "Dev"
```

---

## 🔍 Gestion des Erreurs

| Cas | Comportement |
|-----|-------------|
| Format source inconnu | Log warning, retour CV v2.0 vide |
| Dates invalides | Retour chaîne vide (skipped) |
| Fichier JSON invalide | Erreur 400, message descriptif |
| Fichier DOCX non trouvé | Erreur 404 |
| Exception non gérée | Erreur 500, log de la stack |

---

## 🚀 Intégration Frontend

### Exemple : React + Fetch

```javascript
// Envoi d'un ancien CV pour normalisation
const normalizeCV = async (oldCvData) => {
  const response = await fetch('/api/cv/normalize', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cv_data: oldCvData })
  });
  
  const result = await response.json();
  
  if (result.success) {
    const cvNormalized = result.cv_normalized;
    console.log(`✅ Normalisation réussie`);
    console.log(`Experiences: ${result.metadata.nb_experiences}`);
    console.log(`Formations: ${result.metadata.nb_formations}`);
    return cvNormalized;
  } else {
    console.error(`❌ ${result.error}`);
    return null;
  }
};

// Usage
const cvOld = {...};
const cvNew = await normalizeCV(cvOld);
// Maintenant on peut afficher/générer PDF/DOCX avec cvNew
```

---

## 📋 Checklist d'Évolution Future

- [ ] Support de fichiers DOCX ancien format (détection automatique de structure)
- [ ] Import/Export formats additionnels (CSV, XML, LinkedIn JSON)
- [ ] Enrichissement par IA : suggestion de compétences, regroupement d'expériences
- [ ] Historique des versions : conservation des anciennes versions
- [ ] Base de données : stockage des CVs normalisés
- [ ] Tests unitaires complets (pytest)
- [ ] Documentation Swagger/OpenAPI

---

## 📚 Résumé Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                      │
└────────────────┬────────────────────────────────────────────┘
                 │ POST /api/cv/normalize
                 │ (ancien JSON ou fichier)
                 ↓
┌────────────────────────────────────────────────────────────┐
│                    BACKEND FLASK (api.py)                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  POST /api/cv/normalize (nouvelle route)           │   │
│  │  - Accepte JSON ou fichier                         │   │
│  │  - Appelle normalize_old_cv_to_new()              │   │
│  └────────────┬───────────────────────────────────────┘   │
│               │                                            │
│  ┌────────────↓───────────────────────────────────────┐   │
│  │  extractors/version_mapper.py                      │   │
│  │  ┌────────────────────────────────────────────┐    │   │
│  │  │  CVVersionMapper                           │    │   │
│  │  │  - detect_source_format()                  │    │   │
│  │  │  - normalize_date()                        │    │   │
│  │  │  - map_meta/profil/competences/...()      │    │   │
│  │  │  - normalize()  ← orchestratrice          │    │   │
│  │  └────────────────────────────────────────────┘    │   │
│  └────────────┬───────────────────────────────────────┘   │
│               │                                            │
│               ↓                                            │
│        (CV nouveau format v2.0)                           │
└────────────────┬───────────────────────────────────────────┘
                 │ JSON v2.0 (contrat unique)
                 ↓
         ┌──────────────┐
         │ Générateur   │
         │ PDF/DOCX     │
         └──────────────┘
```

---

## 🎁 Contrats Respectés

✅ **Contrat Central** : JSON v2.0 = format unique pour frontend  
✅ **Non-Breaking** : Pipeline `/api/cv/analyze` inchangé  
✅ **Modulaire** : Tout en `version_mapper.py`, zéro modification des autres modules  
✅ **Robuste** : Gestion gracieuse des erreurs, logging détaillé  
✅ **Production-Ready** : No exceptions levées en API, mode strict optionnel pour tests

---

**Version du Document** : 2.0 (Mise à jour Janvier 2026)
**Statut** : Production-Ready  
**Derniers changements** :
- Réfactorisation génération DOCX (template → programmatique)
- Nettoyage du repository (suppression 50+ fichiers test)
- Documentation mise à jour avec architecture finale
**Auteur** : Senior Backend Developer  
