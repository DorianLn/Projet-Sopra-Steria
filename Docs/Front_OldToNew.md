# Documentation Frontend : Transition Ancien → Nouveau Format CV

## 📋 Vue d'ensemble

Ce document récapitule **tous les changements apportés au frontend** pour supporter la transition du format CV ancien vers le nouveau format normalisé v2.0.

**Date de mise à jour** : Janvier 2026  
**Branche** : `versionnage`  
**Statut** : Production-Ready

---

## 🗂️ Structure Frontend

```
frontend/
├── src/
│   ├── App.jsx                          [MODIFIÉ] Routes principales
│   ├── main.jsx
│   ├── components/
│   │   ├── Navbar.jsx                   [MODIFIÉ] Navigation mise à jour
│   │   └── ...autres composants
│   ├── pages/
│   │   ├── Home/
│   │   ├── Start/
│   │   ├── Normalize/                   [NOUVEAU] Page de normalisation CV
│   │   ├── Example/
│   │   ├── HowItWorks/
│   │   └── ...
│   ├── hooks/
│   │   ├── useDarkMode.js               [EXISTANT] Dark mode hook
│   │   └── ...
│   ├── utils/
│   │   ├── constants.js                 [MODIFIÉ] Constantes centralisées
│   │   └── ...
│   ├── styles/
│   │   ├── index.css                    [MODIFIÉ] Styles généraux
│   │   └── ...
│   └── assets/
└── ...
```

---

## 🔧 Fichiers Modifiés

### 1️⃣ **src/App.jsx**

**Localisation** : `frontend/src/App.jsx`

**Changements** :
- ✅ Route `/normalize` ajoutée → composant `Normalize`
- ✅ Route `/howitworks` disponible
- ✅ Structure de routage complète pour l'écosystème CV

**Code** :
```jsx
import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home/Home';
import Start from './pages/Start/Start';
import Normalize from './pages/Normalize/Normalize';          // NEW
import HowItWorks from './pages/HowItWorks/HowItWorks';       // NEW
import Example from './pages/Example/Example';
import './styles/index.css'

const App = () => {
  return (
      <div className='root'>
        <Routes>
          <Route path='/' element={<Home />} />
          <Route path='/start' element={<Start />} />
          <Route path='/normalize' element={<Normalize />} />  {/* NEW */}
          <Route path='/howitworks' element={<HowItWorks />} />{/* NEW */}
          <Route path='/example' element={<Example />} />
        </Routes>
      </div>
  );
}

export default App;
```

---

### 2️⃣ **src/utils/constants.js**

**Localisation** : `frontend/src/utils/constants.js`

**Changements** :
- ✅ Centralisation de **toutes les constantes** d'application
- ✅ Définition des routes (ROUTES object)
- ✅ Navigation links (NAV_LINKS) pour éviter code en dur
- ✅ Constantes d'upload fichier (types, taille max)
- ✅ Constantes de thème (dark/light mode)

**Code** :
```javascript
// ===================== NAVIGATION CONSTANTS =====================
export const ROUTES = {
  HOME: '/',
  START: '/start',
  NORMALIZE: '/normalize',
  EXAMPLE: '/example',
  HOW_IT_WORKS: '/howitworks'
}

export const NAV_LINKS = [
  { path: ROUTES.HOME, label: 'Home' },
  { path: ROUTES.EXAMPLE, label: 'Voir un exemple' },
  { path: ROUTES.NORMALIZE, label: 'Normaliser un CV' },
  { path: ROUTES.HOW_IT_WORKS, label: 'Comment ça marche' }
]

// ===================== APP CONSTANTS =====================
export const APP_NAME = 'CV Generator'
export const COMPANY_NAME = 'Sopra Steria'

// ===================== FILE UPLOAD CONSTANTS =====================
export const ALLOWED_FILE_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
]

export const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

export const FILE_TYPE_EXTENSIONS = {
  'application/pdf': '.pdf',
  'application/msword': '.doc',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx'
}

// ===================== THEME CONSTANTS =====================  
export const THEMES = {
  LIGHT: 'light',
  DARK: 'dark'
}

export const STORAGE_KEYS = {
  DARK_MODE: 'darkMode'
}
```

**Avantages** :
- 🎯 **Single Source of Truth** : routes définies une seule fois
- 🎯 **Maintenabilité** : modification facile des chemins/labels
- 🎯 **Réutilisabilité** : importées partout où nécessaire
- 🎯 **Type-safe** : constants plutôt que chaînes en dur

---

### 3️⃣ **src/components/Navbar.jsx**

**Localisation** : `frontend/src/components/Navbar.jsx`

**Changements** :
- ✅ Import de `NAV_LINKS` et `ROUTES` depuis constants.js
- ✅ Navigation dynamique basée sur `NAV_LINKS`
- ✅ Support du dark mode avec `useDarkMode()` hook
- ✅ Menu responsive (desktop + mobile)
- ✅ Bouton "Commencer" lié à route START

**Code clé** :
```jsx
import { useDarkMode } from "../hooks/useDarkMode";
import { NAV_LINKS, ROUTES } from "../utils/constants";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { darkMode, toggleDarkMode } = useDarkMode();

  return (
    <header className="navbar">
      {/* Logo */}
      <NavLink to="/" className="navbar-logo">
        <img src={logo2} alt="Sopra Steria" />
      </NavLink>

      {/* Menu Desktop - DYNAMIQUE depuis NAV_LINKS */}
      <nav className="navbar-links">
        {NAV_LINKS.map((link) => (
          <NavLink
            key={link.path}
            to={link.path}
            className={({ isActive }) =>
              isActive ? "navbar-link navbar-link-active" : "navbar-link"
            }
          >
            {link.label}
          </NavLink>
        ))}
      </nav>

      {/* Dark Mode Toggle */}
      <button
        onClick={toggleDarkMode}
        className={`text-xl focus:outline-none ${
          darkMode ? "text-white" : "text-black"
        }`}
        aria-label="Toggle Dark Mode"
      >
        {darkMode ? <HiOutlineSun size={28} /> : <HiOutlineMoon size={28} />}
      </button>

      {/* Bouton Commencer */}
      <NavLink to={ROUTES.START} className="navbar-btn">
        Commencer
      </NavLink>

      {/* Menu Mobile */}
      {isOpen && (
        <div className="navbar-mobile md:hidden">
          {/* Menu items dynamique */}
          {/* Dark Mode Toggle */}
        </div>
      )}
    </header>
  );
};
```

**Améliorations** :
- 🎯 **DRY Principle** : pas de duplication de liens
- 🎯 **Responsive** : desktop et mobile synchronisés
- 🎯 **Accessibilité** : aria-labels pour icônes
- 🎯 **Dark Mode** : support complet du thème sombre

---

## 🎨 Pages Nouvelles / Principales

### A. Page `/normalize` (Normalize.jsx)

**Fonction** : Permet aux utilisateurs de :
1. ✅ Uploader un CV ancien format (JSON ou DOCX)
2. ✅ Normaliser vers le nouveau format v2.0
3. ✅ Télécharger le DOCX généré

**Flux utilisateur** :
```
Utilisateur uploads CV
    ↓
Backend analyse (extraction + normalisation)
    ↓
Frontend affiche résumé (# expériences, formations, etc.)
    ↓
Utilisateur télécharge DOCX formaté
```

**Endpoints utilisés** :
- `POST /api/cv/analyze` → analyse du CV uploadé
- `POST /api/cv/normalize/docx` → génération Word normalisé

---

### B. Page `/example` (Example.jsx)

**Fonction** : Affiche un exemple de CV normalisé

---

### C. Page `/howitworks` (HowItWorks.jsx)

**Fonction** : Explication du processus de normalisation

---

## 🔌 Intégration API Frontend

### Endpoints consommés

| Endpoint | Méthode | Utilisation |
|----------|---------|-------------|
| `/api/cv/analyze` | POST | Analyse du CV uploadé |
| `/api/cv/normalize` | POST | Normalisation JSON |
| `/api/cv/normalize/docx` | POST | Génération DOCX normalisé |
| `/api/cv/normalize/pdf` | POST | Génération PDF normalisé |

### Exemple de fetch (Normalize.jsx)

```javascript
// Analyse
const response = await fetch('/api/cv/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ cv_data: extractedData })
});

// Récupération du résumé
const result = await response.json();
console.log(`Experiences: ${result.metadata.nb_experiences}`);

// Génération DOCX
const docxResponse = await fetch('/api/cv/normalize/docx', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ cv_data: normalizedData })
});

// Téléchargement
const blob = await docxResponse.blob();
const url = window.URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'CV_normalized.docx';
a.click();
```

---

## 🎨 Styles (CSS/Tailwind)

**Fichier** : `frontend/src/styles/index.css` [MODIFIÉ]

**Éléments stylisés** :
- ✅ Navbar (desktop + mobile responsive)
- ✅ Boutons (CTA, submit, cancel)
- ✅ Formulaires d'upload
- ✅ Sections de contenu
- ✅ Dark mode (toggle, couleurs)
- ✅ Animations transitions

**Classes principales** :
```css
/* Navbar */
.navbar, .navbar-container, .navbar-logo, .navbar-links, .navbar-btn, .navbar-mobile

/* Upload zone */
.upload-zone, .file-input, .file-preview

/* Boutons */
.btn-primary, .btn-secondary, .btn-danger

/* Formulaires */
.form-group, .form-input, .form-textarea

/* Dark mode */
.dark .bg-white { @apply bg-gray-900; }
.dark .text-black { @apply text-white; }
```

---

## 🪝 Hooks Disponibles

### `useDarkMode` (existant, utilisé)

**Localisation** : `frontend/src/hooks/useDarkMode.js`

**Usage** :
```javascript
const { darkMode, toggleDarkMode } = useDarkMode();
```

**Sauvegarde** : LocalStorage clé `'darkMode'` (via `STORAGE_KEYS.DARK_MODE`)

---

## 📊 Architecture Composants

```
App
├── Home
├── Navbar
│   ├── NavLink (dynamique depuis ROUTES)
│   ├── Dark Mode Toggle
│   └── Mobile Menu
├── Routes
│   ├── /                 → Home
│   ├── /start            → Start (analyse)
│   ├── /normalize        → Normalize (normalisation)
│   ├── /example          → Example
│   └── /howitworks       → HowItWorks
└── Footer (?)
```

---

## 🚀 Fonctionnalités Frontend v2.0

### ✅ Implémentées

1. **Navigation centralisée** : Constants + dynamique
2. **Dark mode** : Toggle + persistence
3. **Upload fichiers** : PDF/DOCX acceptés
4. **Normalisation CV** : Appel API backend
5. **Génération DOCX** : Export normalisé
6. **Responsive design** : Desktop + mobile
7. **Feedback utilisateur** : Loading, succès, erreurs

### 🔮 Futures évolutions possibles

- [ ] Aperçu CV avant génération (JSON viewer)
- [ ] Upload batch (plusieurs CVs)
- [ ] Historique des conversions
- [ ] Éditeur interactif du CV
- [ ] Signature numérique
- [ ] Authentification utilisateur
- [ ] Statistiques d'usage
- [ ] Export multi-formats (PDF, HTML, etc.)

---

## 🔄 Flux de Normalisation Complet

```
┌─────────────────────────────────────────┐
│   Frontend (React)                      │
│   Page /normalize                       │
└────────────┬────────────────────────────┘
             │
             │ 1. Utilisateur upload CV (PDF/DOCX)
             ↓
┌─────────────────────────────────────────┐
│   Backend (Flask)                       │
│   POST /api/cv/analyze                  │
│   - Extraction texte (PDF → DOCX)       │
│   - Analyse sections (spaCy)            │
│   - JSON ancien format                  │
└────────────┬────────────────────────────┘
             │
             │ 2. JSON ancien retourné
             ↓
┌─────────────────────────────────────────┐
│   Backend                               │
│   Normalisation (version_mapper.py)     │
│   - Mappage champs                      │
│   - JSON v2.0 généré                    │
└────────────┬────────────────────────────┘
             │
             │ 3. Feedback utilisateur
             ↓
┌─────────────────────────────────────────┐
│   Frontend                              │
│   Affichage résumé:                     │
│   - # expériences, formations           │
│   - Boutons: Télécharger DOCX/PDF       │
└────────────┬────────────────────────────┘
             │
             │ 4. Utilisateur clique "Télécharger"
             ↓
┌─────────────────────────────────────────┐
│   Backend                               │
│   POST /api/cv/normalize/docx           │
│   - generate_sopra_docx()               │
│   - DOCX programmatique                 │
│   - Retour fichier binaire              │
└────────────┬────────────────────────────┘
             │
             │ 5. Blob téléchargé
             ↓
         💾 CV_normalized.docx
```

---

## 📝 Bonnes Pratiques Respectées

✅ **DRY** : Constants réutilisables, pas de duplication  
✅ **Responsive** : Navbar responsive desktop/mobile  
✅ **Accessibilité** : aria-labels, semantic HTML  
✅ **Performance** : Lazy loading des images  
✅ **Maintenabilité** : Code organisé, composants modulaires  
✅ **UX** : Feedback utilisateur, gestion erreurs  
✅ **Dark Mode** : Support complet avec persistence  

---

## 🧪 Tests Recommandés

### Frontend Tests
```bash
# Tests composants (exemple)
npm test

# Tests E2E
npm run test:e2e
```

### Checklist manuelle
- [ ] Navigation entre routes fonctionnelle
- [ ] Dark mode toggle persistant
- [ ] Upload fichiers (PDF + DOCX) accepté
- [ ] Normalistion CV retourne résumé correct
- [ ] Téléchargement DOCX fonctionne
- [ ] Menu mobile responsive
- [ ] Pas de console errors

---

## 📚 Résumé Modifications

| Fichier | Type | Changement |
|---------|------|-----------|
| App.jsx | Route | Routes `/normalize`, `/howitworks` |
| constants.js | Centralization | ROUTES, NAV_LINKS, THEMES, FILE_TYPES |
| Navbar.jsx | Enhancement | Nav dynamique, dark mode, mobile menu |
| Normalize.jsx | New Page | Upload + normalisation + export |
| index.css | Styles | Navbar, upload zone, responsiveness |

---

## 📞 Support

**Questions / Bugs** :
- Vérifier la console (F12 → Console tab)
- Vérifier le backend logs (Terminal Flask)
- Vérifier constants.js pour chemins API

**Modification future** :
- Ajouter constante → `constants.js`
- Ajouter route → `App.jsx` + `NAV_LINKS`
- Ajouter page → `pages/` + importer dans App

---

**Version du Document** : 1.0  
**Statut** : Production-Ready  
**Branche** : `versionnage`  
**Date** : Janvier 2026
