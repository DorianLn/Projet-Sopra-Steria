# Frontend - CV Extract Pro - Sopra Steria

Ce dépôt contient la partie **frontend** de l’application, développée avec **React**, **Vite** et **TailwindCSS**.  

L’application propose une interface intuitive permettant d’extraire automatiquement les informations d’un CV et de générer des documents standardisés professionnels.

## Stack Technique

        ⚛️ **React 19** — Composants modernes & réactifs

        ⚡ **Vite** — Serveur de développement ultra-rapide + build optimisé (Rollup)

        🎨 **TailwindCSS** — Design responsive & entièrement personnalisable

        🛣 **React Router DOM** — Navigation multi-pages fluide

        🌗 **Dark / Light Mode** — Gestion du thème avec persistance locale (localStorage)

## Installation & Lancement

### 1. Cloner le projet
```bash
        git clone https://github.com/DorianLn/Projet-Sopra-Steria.git

        cd Projet-Sopra-Steria/frontend

### 2. Installer les dépendances
        npm install

### 3. Lancer le serveur de développement
        npm run dev

 ***************************************************************
| ==> L’application sera disponible sur http://localhost:5173   |
 ***************************************************************
### 4. Build pour la production
        npm run build

### 5. Prévisualiser le build
        npm run preview

#### Structure du projet
        frontend/
        ├── images/
        │   ├── preview1.png
        │   ├── preview2.png
        │   ├── preview3.png
        │   └── preview4.png
        ├── public/                 # Fichiers statiques
        ├── src/
        │   ├── assets/             # Images, logos, icônes...
        │   ├── components/         # Composants réutilisables
        │   │   ├── Navbar.jsx
        │   │   └── HeroSection.jsx
        │   ├── pages/              # Pages principales
        │   │   └── Home.jsx
        │   ├── App.jsx             # Définition des routes
        │   ├── main.jsx            # Point d’entrée React
        │   └── index.css           # Styles globaux & thème
        ├── index.html              # Page principale
        ├── package.json
        ├── tailwind.config.js      # Config Tailwind
        ├── postcss.config.cjs
        ├── vite.config.js          # Config Vite
        └── README.md

##### Style & Thème
        Police principale : Raleway
        Police secondaire : Manrope (pour les titres et chiffres)
        Mode : Clair 🌞 / Sombre 🌙 activable depuis la Navbar
        Couleur primaire : rgb(221, 83, 52) (#DD5334)
        Dégradés utilisés : linear-gradient(90deg, #880015, #FF5614)
        Le design suit la charte visuelle Sopra Steria, combinant minimalisme et professionnalisme.

###### Fonctionnalités principales

        🎨 Interface responsive : optimisée pour desktop & mobile
        🌗 Dark/Light Mode : persistant avec localStorage
        ⚡ Performance : chargement rapide via Vite
        🧭 Navigation fluide : gérée avec React Router

####### Scripts utiles
 -------------------------------------------------------------------------------
|        Commandes              |                Description                    |
 -------------------------------------------------------------------------------
|       npm run dev	        |       Lancer le serveur en mode développement |
|       npm run build	        |       Construire le projet pour la production |
|       npm run preview	        |       Tester le build localement              |
--------------------------------------------------------------------------------

######## Contributeurs

👩‍💻 Safae
👨‍💻 Nehade
👨‍💻 Clément
👨‍💻 Julien 
👨‍💻 Dorian 
👨‍💻 Thomas 
----------------------------------------------------------------------------------------------------------------
# À propos du projet

CV Extract Pro est développé dans le cadre du projet Sopra Steria, visant à automatiser la gestion et la normalisation des CV pour les processus de recrutement.
Cette partie frontend met l’accent sur l’expérience utilisateur, la rapidité et la clarté visuelle.
----------------------------------------------------------------------------------------------------------------

# Améliorations futures

🔹 Connexion au backend Python :
Intégration d’une API REST pour communiquer avec le moteur d’extraction et de génération de CV (FastAPI ou Django).
🔹 Optimisation du Dark Mode :
Amélioration des contrastes et de la lisibilité en mode sombre.

# Aperçu de l’application

        Voici un aperçu de l’interface CV Extract Pro :

        Navbar : navigation fluide, dark/light mode activable
        Hero Section : titre, sous-titre, boutons d’action et statistiques
        Design responsive : optimisé pour desktop & mobile

![Preview 1](./images/preview1.png)
![Preview 2](./images/preview2.png)
![Preview 3](./images/preview3.png)
![Preview 4](./images/preview4.png)