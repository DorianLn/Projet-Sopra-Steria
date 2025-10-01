# Fonctionnement du Projet d'Extraction de CV

Ce document détaille le fonctionnement technique du système d'extraction d'informations à partir de CV.

## 1. Architecture du Projet

```
project/
├── analyser_cv.py         # Script principal
├── backend/
│   └── extractors/
│       └── extracteur.py  # Module d'extraction
├── data/
│   ├── input/            # Dossier des CVs source
│   └── output/           # Dossier des résultats
└── tests/
    └── test_simple.py    # Tests unitaires
```

## 2. Processus d'Extraction

### 2.1 Chargement du CV
- Lecture du fichier texte depuis le dossier `data/input/`
- Prétraitement du texte pour standardiser les formats

### 2.2 Extraction des Informations
Le système utilise plusieurs extracteurs spécialisés :

#### Extracteur de Dates
Reconnaît plusieurs formats de dates :
```python
# Format MM/AAAA (ex: 06/2016)
pattern = r'\b(0[1-9]|1[012])[-/]((?:19|20)\d{2})\b'

# Format AAAA-AAAA (ex: 2017-2019)
pattern = r'((?:19|20)\d{2})\s*[-–]\s*((?:19|20)\d{2})'

# Format Mois AAAA (ex: Mars 2026)
pattern = r'(?:Janvier|Février|...|Décembre)\s+((?:19|20)\d{2})'
```

#### Extracteur d'Emails
- Détecte les adresses email standards
- Gère les formats avec caractères spéciaux (+, .)

#### Extracteur de Téléphones
- Reconnaît les formats français
- Gère différentes séparations (espace, point, tiret)

#### Extracteur d'Adresses
- Identifie les adresses postales complètes
- Extrait les codes postaux et villes

## 3. Traitement des Données

### 3.1 Nettoyage
- Suppression des doublons
- Standardisation des formats
- Validation des données extraites

### 3.2 Structuration
Les données sont organisées en format JSON :
```json
{
  "dates": [
    "06/2016",
    "09/2016",
    "2017-2019"
  ],
  "emails": [
    "exemple@email.com"
  ],
  "telephones": [
    "07 65 43 21 09"
  ],
  "adresses": [
    "5 rue des Remparts, 69001 Lyon"
  ]
}
```

## 4. Validation et Tests

### 4.1 Tests Unitaires
- Test de chaque extracteur individuellement
- Vérification des formats de sortie
- Validation des cas particuliers

### 4.2 Tests d'Intégration
- Test du processus complet
- Validation sur des CVs réels
- Vérification de la cohérence des données

## 5. Points Techniques Importants

### 5.1 Expressions Régulières
- Utilisation intensive de regex pour l'extraction
- Patterns optimisés pour la précision
- Gestion des cas particuliers

### 5.2 Performance
- Traitement séquentiel des extracteurs
- Optimisation des regex
- Gestion efficace de la mémoire

### 5.3 Extensibilité
Le système est conçu pour être facilement extensible :
- Ajout de nouveaux extracteurs
- Modification des patterns existants
- Support de nouveaux formats

## 6. Limitations Actuelles

- Traitement uniquement des fichiers texte
- Sensible à la qualité du formatage du CV
- Certains formats de dates spécifiques peuvent être manqués

## 7. Évolutions Possibles

- Support des fichiers PDF et Word
- Amélioration de la reconnaissance d'adresses
- Ajout d'extraction de compétences
- Interface graphique pour la configuration
- Système de logging pour le debug

## 8. Utilisation

### 8.1 Exécution Simple
```bash
python analyser_cv.py
```

### 8.2 Exécution des Tests
```bash
python -m pytest tests/
```

### 8.3 Vérification des Résultats
Les résultats sont disponibles dans `data/output/` au format JSON.