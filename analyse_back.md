# Analyse du Backend - Projet Extraction de CV

## Fonctionnement Global
Le backend est conçu pour traiter et analyser des CV au format PDF ou DOCX. Il s'articule autour de trois fonctionnalités principales :
1. La conversion de fichiers PDF en DOCX
2. L'extraction d'informations via des expressions régulières et NLP
3. Une API RESTful pour l'interaction avec le frontend

## Structure du Backend
```
backend/
├── api.py
└── extractors/
    ├── extracteur.py
    ├── pdf_to_docx.py
    ├── section_classifier.py
    └── spacy_extractor.py
```

## Analyse des Fichiers

### 1. api.py
**Rôle** : Point d'entrée principal de l'API, gère les requêtes HTTP et orchestre le traitement des CV.

**Fonctionnalités principales** :
- Configuration de Flask et CORS
- Gestion des uploads de fichiers
- Point d'entrée `/api/cv/analyze` pour l'analyse des CV
- Gestion des erreurs et des réponses

**Méthodes clés** :
- `allowed_file(filename)` : Vérifie si l'extension du fichier est autorisée
- `process_cv(file_path)` : Traite le CV et retourne les résultats structurés
- `analyze_cv()` : Point d'entrée API pour l'analyse des CV

### 2. extractors/extracteur.py
**Rôle** : Contient les fonctions d'extraction d'informations basées sur les expressions régulières.

**Méthodes principales** :
- `extraire_dates(texte)` : Extrait les dates dans différents formats (JJ/MM/AAAA, MM/AAAA, etc.)
- `extraire_email(texte)` : Extrait les adresses email via regex
- `extraire_telephone(texte)` : Extrait les numéros de téléphone français
- `extraire_adresse(texte)` : Extrait les adresses postales avec différents formats
- `dedupliquer(liste)` : Élimine les doublons tout en préservant l'ordre

### 3. extractors/section_classifier.py
**Rôle** : Classifie et structure les informations extraites du CV en sections logiques.

**Fonctionnalités principales** :
- Classification des formations et expériences
- Extraction et association des dates avec les organisations
- Détection des compétences et langues
- Construction du JSON final structuré

**Méthodes clés** :
- `extract_date_spans(text)` : Extrait les dates avec leur position dans le texte
- `find_org_positions(org, text)` : Trouve les positions d'une organisation dans le texte
- `find_closest_date_by_char(org, text, date_spans)` : Associe la date la plus proche à une organisation
- `classifier_formations_experiences(texte, entites, dates)` : Classifie les expériences et formations
- `extraire_competences_langues(texte)` : Extrait les compétences techniques et linguistiques
- `build_structured_json(...)` : Construit le JSON final avec toutes les informations structurées

**Constantes importantes** :
- `FORMATION_KEYWORDS` : Mots-clés pour identifier les formations
- `EXPERIENCE_KEYWORDS` : Mots-clés pour identifier les expériences
- `COMPETENCE_KEYWORDS` : Liste des compétences techniques à détecter
- `LANGUES_KEYWORDS` : Liste des langues à détecter

### 4. extractors/spacy_extractor.py
**Rôle** : Utilise spaCy pour l'extraction avancée d'entités nommées du texte.

**Fonctionnalités principales** :
- Utilisation du modèle français de spaCy (`fr_core_news_md`)
- Extraction d'entités nommées (noms, organisations, lieux, dates)
- Système de fallback avec expressions régulières

**Méthode principale** :
`extraire_entites(texte)` : Extrait les entités avec :
- Détection des noms (PER)
- Détection des organisations (ORG)
- Détection des lieux (LOC)
- Détection des dates (DATE)
- Fallback regex pour les organisations non détectées
- Nettoyage et déduplication des résultats

### 5. extractors/pdf_to_docx.py
**Rôle** : Gère la conversion des fichiers PDF en format DOCX.

**Fonctionnalités** :
- Conversion PDF vers DOCX avec préservation du texte
- Système de logging pour le suivi des opérations
- Gestion des erreurs

**Méthode principale** :
- `convert_pdf_to_docx(pdf_path, docx_path)` : Convertit un PDF en DOCX

## Points Forts

1. **Architecture Modulaire**
   - Séparation claire des responsabilités
   - Facilité de maintenance et d'extension
   - Code bien organisé en modules distincts

2. **Sécurité**
   - Validation des types de fichiers
   - Nettoyage des noms de fichiers
   - Suppression automatique des fichiers temporaires

3. **Robustesse**
   - Gestion des erreurs à plusieurs niveaux
   - Logging détaillé des opérations
   - Validation des entrées

4. **Performance**
   - Traitement en local
   - Dédoublonnage efficace des résultats
   - Optimisation des expressions régulières

5. **Flexibilité**
   - Support de plusieurs formats (PDF, DOCX)
   - Expressions régulières adaptables
   - API RESTful extensible

## Points Faibles

1. **Limitations Techniques**
   - Pas de support pour d'autres formats (images, autres formats de documents)
   - Extraction basée principalement sur les expressions régulières
   - Pas de mise en cache des résultats

2. **Gestion des Données**
   - Pas de système de persistance des données
   - Pas de gestion des sessions utilisateurs
   - Absence de base de données

3. **Validation et Tests**
   - Manque de tests unitaires
   - Pas de validation approfondie des données extraites
   - Absence de métriques de performance

4. **Documentation**
   - Documentation technique limitée
   - Absence de documentation API (Swagger/OpenAPI)
   - Manque d'exemples d'utilisation

5. **Évolutivité**
   - Pas de gestion des traitements asynchrones
   - Absence de queue de traitement pour les fichiers volumineux
   - Pas de mécanisme de rate limiting

## Recommandations d'Amélioration

1. **Court terme**
   - Ajouter des tests unitaires
   - Implémenter une documentation API
   - Ajouter une validation plus poussée des données extraites

2. **Moyen terme**
   - Améliorer l'utilisation de spaCy pour l'analyse NLP
   - Ajouter une base de données pour la persistance
   - Implémenter un système de cache

3. **Long terme**
   - Développer des modèles ML personnalisés pour l'extraction
   - Ajouter le support pour d'autres formats
   - Mettre en place un système de traitement asynchrone