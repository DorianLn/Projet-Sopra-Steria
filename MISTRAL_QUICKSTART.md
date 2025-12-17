# IMPLÉMENTATION RAPIDE - Mistral 7B Instruct

## 🚀 Quick Start (5 minutes)

### 1. Installer Ollama
- **Windows**: Télécharger depuis https://ollama.ai/download/windows
- **macOS**: `brew install ollama`
- **Linux**: `curl https://ollama.ai/install.sh | sh`

### 2. Démarrer Ollama
```bash
ollama serve
```
(Garder le terminal ouvert)

### 3. Télécharger Mistral
```bash
ollama pull mistral
```

### 4. Utiliser le code
```python
from extractors.mistral_analyzer import analyze_cv

cv_text = "..."  # Texte du CV
result = analyze_cv(cv_text)  # Retourne du JSON structuré
```

## 📁 Fichiers créés

```
backend/
├── extractors/
│   └── mistral_analyzer.py       # Module principal (300+ lignes)
│
├── routes/
│   └── mistral_routes.py          # Endpoints Flask (80 lignes)
│
├── examples_mistral.py            # 7 exemples d'utilisation (300+ lignes)
├── setup_ollama.py                # Setup automatisé (200+ lignes)
├── startup.py                     # Startup avec vérifications (300+ lignes)
├── test_mistral.py                # Tests unitaires (250+ lignes)
├── mistral_menu.bat               # Menu Windows
├── .env.mistral                   # Configuration
├── INTEGRATION_MISTRAL.md         # Guide d'intégration API
└── MISTRAL_GUIDE.md               # Guide complet

Docs/
└── MISTRAL_GUIDE.md               # Documentation complète
```

## 🎯 Utilisation directe

### Option 1: Simple (sans API)
```python
from extractors.mistral_analyzer import analyze_cv

result = analyze_cv("Jean Dupont\nEmail: jean@example.com\n...")
print(result)  # {'identite': {...}, 'contact': {...}, ...}
```

### Option 2: Avec la classe
```python
from extractors.mistral_analyzer import MistralCVAnalyzer

analyzer = MistralCVAnalyzer()
result = analyzer.analyze_cv(cv_text)
```

### Option 3: Via API Flask
```bash
curl -X POST http://localhost:5000/api/mistral/analyze \
  -H "Content-Type: application/json" \
  -d '{"cv_text": "..."}'
```

## 📊 Structure JSON retournée

```json
{
  "identite": {
    "nom": "Dupont",
    "prenom": "Jean"
  },
  "contact": {
    "adresse": "123 Rue de Paris",
    "ville": "Paris",
    "code_postal": "75001",
    "email": "jean@example.com",
    "telephone": "+33612345678"
  },
  "experience": [
    {
      "poste": "Développeur Python",
      "entreprise": "Acme Corp",
      "ville": "Paris",
      "date_debut": "2020-01-15",
      "date_fin": "2023-12-31",
      "description": "..."
    }
  ],
  "formation": [...],
  "certifications": [...],
  "langues": [...],
  "competences": [...],
  "resume": "..."
}
```

## ⚙️ Configuration

### Changer l'hôte Ollama
```python
analyzer = MistralCVAnalyzer(ollama_host="http://192.168.1.1:11434")
```

### Ajuster la température (détail/créativité)
- 0.0 = déterministe (mieux pour extraction)
- 0.5 = équilibré
- 1.0 = créatif

Modifier dans `mistral_analyzer.py`, fonction `_call_ollama()`:
```python
"temperature": 0.3,  # ← modifier ici
```

## 🔧 Dépannage

### "Ollama n'est pas accessible"
```bash
# Vérifier Ollama
ollama --version

# Lancer Ollama
ollama serve
```

### "Mistral non trouvé"
```bash
# Télécharger
ollama pull mistral
```

### Performance lente
- Première requête plus lente (warm-up)
- Fermer les autres applications
- Attendre quelques secondes entre les requêtes

## ✅ Vérifications

```python
from extractors.mistral_analyzer import verify_mistral_setup

status = verify_mistral_setup()
print(status)
# {
#   'ollama_accessible': True,
#   'mistral_downloaded': True,
#   'status': 'OK',
#   'next_steps': [...]
# }
```

## 🧪 Tests

```bash
# Test simple
python -c "from extractors.mistral_analyzer import analyze_cv; print(analyze_cv('Test'))"

# Tous les tests
python -m pytest backend/test_mistral.py

# Test manuel
python backend/test_mistral.py --manual

# Menu interactif (Windows)
backend/mistral_menu.bat

# Startup complet
python backend/startup.py
```

## 📈 Performances attendues

| Configuration | Temps/CV |
|---|---|
| CPU 8 cores | 30-60s |
| CPU 16 cores | 15-30s |
| GPU RTX 3070+ | 5-15s |
| Première requête | +5-10s |

## 🔐 Sécurité

- ✅ 100% local - Aucune donnée externe
- ✅ Open source - Code transparent
- ✅ Sans API - Pas de clé à gérer
- ⚠️ Isoler le port 11434 sur réseau public

## 📚 Ressources

- [Ollama](https://ollama.ai/)
- [Mistral 7B](https://mistral.ai/)
- [API Ollama](https://github.com/ollama/ollama/blob/main/docs/api.md)

## 🎓 Exemples complets

Voir `examples_mistral.py` pour 7 exemples complets:
1. Utilisation simple
2. Avec la classe
3. Depuis un fichier
4. Vérification setup
5. Traitement batch
6. Sauvegarde résultats
7. Gestion erreurs

```bash
python backend/examples_mistral.py
```

## 🚦 Intégration à votre API

Voir `INTEGRATION_MISTRAL.md` pour les snippets à ajouter à `api.py`:
- Endpoint `/api/mistral/analyze` pour texte direct
- Endpoint `/api/mistral/status` pour vérifier le setup
- Endpoint `/api/cv/analyze-hybrid` pour combiner extraction classique + Mistral

## 📝 Notes importantes

1. **Ollama doit rester actif** - Gardez `ollama serve` lancé
2. **Première requête plus lente** - C'est normal (warm-up du modèle)
3. **~4 GB de RAM** nécessaires pour Mistral 7B
4. **Erreurs JSON** - Mistral peut générer du JSON invalide, retries automatiques
5. **Langue mixte** - Fonctionne avec CV en français, anglais, etc.

## ✨ Points forts

- ✅ Vraiment local (100% privé)
- ✅ Pas de dépendances externes (urllib seulement)
- ✅ Gestion d'erreurs robuste
- ✅ Retries automatiques
- ✅ Logging détaillé
- ✅ Prêt pour production
- ✅ Code Python pur (2 fichiers principaux)

---

**Besoin d'aide?** Vérifiez les logs:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```
