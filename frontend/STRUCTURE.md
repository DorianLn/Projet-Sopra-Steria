# 📁 Structure du Frontend

Cette documentation décrit l'organisation du code frontend de l'application CV Generator.

## 🗂️ Architecture des dossiers

```
frontend/
├── public/                     # Fichiers statiques publics
│   ├── logo.png               # Logo principal de l'app
│   └── vite.svg               # Logo Vite
├── src/
│   ├── assets/                # Ressources statiques
│   │   ├── images/           # Images du projet
│   │   │   ├── hero-cv.png   # Image du hero
│   │   │   └── preview*.png  # Images de preview
│   │   └── logos/            # Logos et icônes
│   │       ├── logo2.png     # Logo navbar
│   │       └── sopra-steria-logo.svg
│   ├── components/           # Composants réutilisables
│   │   ├── HeroSection.jsx   # Section hero
│   │   ├── Navbar.jsx        # Navigation principale
│   │   └── SopraLogo.jsx     # Composant logo Sopra
│   ├── hooks/                # Hooks React personnalisés
│   │   └── useDarkMode.js    # Hook pour dark/light mode
│   ├── pages/                # Pages de l'application
│   │   ├── Home/             # Page d'accueil
│   │   │   ├── Home.jsx
│   │   │   └── Home.css
│   │   ├── Start/            # Page upload CV
│   │   │   ├── Start.jsx
│   │   │   └── Start.css
│   │   ├── Example/          # Page exemple CV
│   │   │   ├── Example.jsx
│   │   │   └── Example.css
│   │   └── HowItWorks/       # Page comment ça marche
│   │       ├── HowItWorks.jsx
│   │       └── HowItWorks.css
│   ├── styles/               # Styles globaux
│   │   └── index.css         # CSS principal
│   ├── utils/                # Utilitaires et constantes
│   │   └── constants.js      # Constantes de l'app
│   ├── App.jsx               # Composant racine
│   └── main.jsx              # Point d'entrée
├── index.html                # Template HTML
├── package.json              # Dépendances
├── vite.config.js           # Configuration Vite
└── tailwind.config.js       # Configuration Tailwind
```

## 🧩 Composants

### 📱 **Navbar.jsx**
- Navigation principale avec dark/light mode
- Menu responsive avec hamburger sur mobile
- Utilise le hook `useDarkMode`

### 🏠 **HeroSection.jsx**
- Section d'accueil avec titre et image
- Composant réutilisable

### 🏢 **SopraLogo.jsx**
- Logo Sopra Steria réutilisable
- Positions configurables via props

## 📄 Pages

### 🏠 **Home** - Page d'accueil
- Hero section avec présentation
- Navbar avec navigation

### 🚀 **Start** - Upload de CV
- Zone de drag & drop
- Validation des fichiers
- Processus de standardisation

### 👁️ **Example** - Exemple de CV
- Affichage d'un CV template
- Toggle entre vue visuelle et JSON
- Téléchargement du JSON

### ❓ **HowItWorks** - Comment ça marche
- Explication du processus
- Étapes détaillées

## 🎨 Styles

### **index.css** - Styles globaux
- Variables CSS
- Styles de base
- Navbar responsive
- Dark/Light mode
- Composants réutilisables

## 🔧 Utilitaires

### **constants.js**
- Routes de navigation
- Types de fichiers autorisés
- Constantes de l'application
- Clés de localStorage

### **useDarkMode.js**
- Hook pour gérer le thème
- Persistance en localStorage
- Application des classes CSS

## 🚀 Scripts disponibles

```bash
npm run dev       # Développement avec hot reload
npm run build     # Build de production
npm run preview   # Preview du build
npm run lint      # Vérification du code
```

## 🎯 Bonnes pratiques

1. **Composants** : Un composant par fichier, nommage PascalCase
2. **Styles** : CSS modules ou classes globales dans index.css
3. **Assets** : Organisation par type (images, logos)
4. **Hooks** : Logique réutilisable extraite en hooks
5. **Constants** : Variables globales centralisées
6. **Pages** : Dossier par page avec JSX + CSS associé

## 📦 Technologies

- **React 19** - Framework frontend
- **Vite** - Build tool et dev server
- **React Router** - Navigation
- **Tailwind CSS** - Framework CSS utilitaire
- **Lucide React** - Icônes
- **React Icons** - Icônes supplémentaires