## 📋 Description
Le but de ce projet est de développer un outil d'automatisation développé dans le cadre d'un projet étudiant en partenariat avec Sopra Steria. Le projet vise à simplifier et standardiser le traitement des CV au format Word (.docx).

L'application permet d'extraire automatiquement les informations pertinentes depuis des CV non structurés et de générer des documents standardisés, tout en respectant les contraintes de confidentialité des données.

### Points clés
- Traitement 100% en local (pas de cloud, pas d'API externe)
- Protection des données sensibles
- Interface utilisateur intuitive
- Automatisation du processus de bout en bout

## ✨ Fonctionnalités

### Disponibles prochainement
- [ ] Lecture de CV au format .docx
- [ ] Extraction des informations de base :
  - Informations personnelles (nom, email, téléphone)
  - Parcours académique
  - Expériences professionnelles
  - Dates clés
- [ ] Génération de documents Word structurés
- [ ] Traitement par lots (multiple CV)
- [ ] Export des données vers Excel
- [ ] Interface utilisateur React

### Évolutions futures
- [ ] Amélioration de l'extraction via spaCy
- [ ] Support d'autres formats de CV
- [ ] Personnalisation des templates de sortie
- [ ] Statistiques et analyses des données extraites

## 🛠️ Technologies

### Backend
- Python 3.x
- python-docx (manipulation Word)
- spaCy (NLP)
- regex (expressions régulières)
- pandas (manipulation de données)
- openpyxl (export Excel)

### Frontend
- React
- Material-UI (à confirmer)

## 📥 Installation

1. Cloner le repository
```bash
git clone https://github.com/DorianLn/Projet-Sopra-Steria.git
cd Projet-Sopra-Steria
```

2. Créer un environnement virtuel Python
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Installer les dépendances
```bash
pip install -r requirements.txt
```

4. Installer les dépendances React
```bash
cd frontend
npm install
```

## 🚀 Utilisation

Instructions à venir une fois le développement commencé.

## 📅 Roadmap

### Phase 1 : PoC (Septembre - Octobre)
- [ ] Setup du projet
- [ ] Implémentation de la lecture basique de CV
- [ ] Extraction simple par regex
- [ ] Génération de documents Word

### Phase 2 : Amélioration (Octobre - Novembre)
- [ ] Intégration de spaCy
- [ ] Amélioration des algorithmes d'extraction
- [ ] Tests et validation

### Phase 3 : Industrialisation (Novembre - Décembre)
- [ ] Traitement par lots
- [ ] Export Excel
- [ ] Tests de performance
- [ ] Documentation

### Phase 4 : Interface et Finalisation (Décembre - Janvier)
- [ ] Développement frontend React
- [ ] Tests utilisateurs
- [ ] Corrections et optimisations
- [ ] Préparation soutenance

## 👥 Contributeurs

Liste des contributeurs à venir.

## 📜 Licence

Ce projet est développé dans le cadre d'un partenariat éducatif avec Sopra Steria. Tous droits réservés.