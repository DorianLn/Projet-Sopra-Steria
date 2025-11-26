# Documentation du Workflow d'Intégration Continue (CI)

Ce document explique le fonctionnement du workflow d'intégration continue (CI) défini dans le fichier `.github/workflows/ci.yml`.

## Vue d'ensemble

Le workflow est conçu pour un monorepo contenant un backend en Python et un frontend en React. Il automatise les tests et le build pour chaque partie du projet indépendamment, afin d'optimiser l'utilisation des ressources.

## Déclenchement du Workflow

Le workflow se déclenche automatiquement à chaque `push` sur la branche `main`.

## Tâches (Jobs)

Le workflow est composé de trois tâches principales : `filter`, `backend-ci`, et `frontend-ci`.

### 1. Tâche `filter`

Cette tâche est la première à s'exécuter. Son unique rôle est de détecter les changements dans les répertoires `backend/` et `frontend/`. Elle utilise l'action `dorny/paths-filter` pour vérifier si des fichiers ont été modifiés dans l'un ou l'autre de ces dossiers. Le résultat de ce filtre est ensuite utilisé pour décider si les tâches `backend-ci` et `frontend-ci` doivent s'exécuter.

### 2. Tâche `backend-ci`

Cette tâche s'occupe de l'intégration continue pour la partie backend du projet.

*   **Condition d'exécution** : Elle ne s'exécute que si la tâche `filter` a détecté des changements dans le répertoire `backend/`.
*   **Environnement** : Elle s'exécute sur une machine virtuelle `ubuntu-latest` avec Python `3.11`.
*   **Répertoire de travail** : Toutes les commandes sont exécutées depuis le répertoire `backend/`.
*   **Étapes** :
    1.  **Checkout** : Récupération du code source du dépôt.
    2.  **Mise en place de Python** : Installation de la version `3.11` de Python.
    3.  **Installation de pip** : Installation de la version `23.3.1` de `pip`.
    4.  **Installation des dépendances** : Installation des paquets Python listés dans le fichier `requirements.txt`.
    5.  **Téléchargement du modèle Spacy** : Téléchargement du modèle linguistique `fr_core_news_sm` nécessaire à la bibliothèque Spacy.
    6.  **Lancement des tests** : Exécution de la suite de tests avec `pytest`.

### 3. Tâche `frontend-ci`

Cette tâche gère l'intégration continue pour la partie frontend du projet.

*   **Condition d'exécution** : Elle ne s'exécute que si la tâche `filter` a détecté des changements dans le répertoire `frontend/`.
*   **Environnement** : Elle s'exécute sur une machine virtuelle `ubuntu-latest` avec Node.js `20`.
*   **Répertoire de travail** : Toutes les commandes sont exécutées depuis le répertoire `frontend/`.
*   **Étapes** :
    1.  **Checkout** : Récupération du code source du dépôt.
    2.  **Mise en place de Node.js** : Installation de la version `20` de Node.js.
    3.  **Installation des dépendances** : Installation des paquets JavaScript avec `npm install`.
    4.  **Linter** : Exécution de `npm run lint` pour analyser le code et détecter les erreurs de style.
    5.  **Build de production** : Création d'une version optimisée pour la production de l'application avec `npm run build`.

Ce workflow garantit que seul le code concerné par les modifications est testé et/ou buildé, ce qui économise du temps et des ressources de calcul.
