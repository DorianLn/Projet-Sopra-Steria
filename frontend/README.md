# Frontend - CV Extract Pro Projet Sopra Steria

Ce dépôt contient la partie **frontend** de l’application, développée avec **React**, **Vite** et **TailwindCSS**.  
Il s’agit d'une interface utilisateur pour l'extraction et la génération de CV standardisés.

---

## 🚀 Stack Technique

- ⚛️ **React 19**
- ⚡ **Vite** (serveur de développement rapide + build optimisé avec Rollup)
- 🎨 **TailwindCSS** (design responsive & customisable)
- 🛣 **React Router DOM** (navigation multi-pages)

---

## 📦 Installation & Lancement

### 1. Cloner le projet
```bash
git clone https://github.com/DorianLn/Projet-Sopra-Steria.git
cd Projet-Sopra-Steria/frontend

### 2. Installer les dépendances
npm install

### 3. Lancer le serveur de développement
npm run dev


➡️ L’application sera disponible sur http://localhost:5173

### 4. Build pour la production
npm run build

### 5. Prévisualiser le build
npm run preview

### 📂 Structure du projet
    frontend/
    ├── public/             # Fichiers statiques
    ├── src/
    │   ├── assets/         # Images, icônes, etc.
    │   ├── components/     # Composants réutilisables (Navbar, Footer...)
            ├── Navbar.jsx  
    │   ├── pages/          # Pages principales (Home, About, Contact...)
            ├── Home.jsx 
    │   ├── App.jsx         # Point d’entrée de l’app
    │   ├── main.jsx        # Initialisation React
    │   └── index.css       # Fichier global Tailwind
    ├── index.html      
    ├── package.json
    ├── tailwind.config.js  # Configuration Tailwind
    ├── postcss.config.cjs
    ├── vite.config.js      # Configuration Vite
    └── README.md

### 🎨 Style & Thème
Police : Manrope via Google Fonts
Mode clair/sombre avec @custom-variant dark
Couleur primaire :rgb(221, 83, 52)

### 📌 Scripts utiles
npm run dev → Lancer en mode développement
npm run build → Construire pour production
npm run preview → Tester le build localement

### ✨ Contributeurs
👩‍💻 Safae 
👨‍💻 Nehade
👨‍💻 Clément

