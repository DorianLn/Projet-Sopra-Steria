# Guide Complet d'Intégration de Mistral 7B avec Ollama

## 📋 Vue d'ensemble

Ce projet intègre **Mistral 7B Instruct** en mode local via **Ollama**. Aucune API externe n'est utilisée - tout fonctionne sur votre machine.

## 🚀 Installation Rapide

### Étape 1: Installer Ollama

#### Windows
1. Allez sur https://ollama.ai/download/windows
2. Téléchargez et exécutez l'installateur
3. Suivez les instructions

#### macOS
```bash
brew install ollama
```

Ou téléchargez depuis https://ollama.ai/download/mac

#### Linux
```bash
curl https://ollama.ai/install.sh | sh
```

### Étape 2: Télécharger Mistral

Ouvrez un terminal et exécutez:
```bash
ollama pull mistral
```

Cela télécharge le modèle Mistral 7B Instruct (~4 GB).

### Étape 3: Lancer Ollama

Gardez un terminal ouvert avec:
```bash
ollama serve
```

Ollama doit rester en arrière-plan pour que le projet fonctionne.

### Étape 4: Utiliser dans le projet

#### Option A: Utiliser le module directement

```python
from extractors.mistral_analyzer import analyze_cv

# Votre texte CV
cv_text = "..."

# Analyser
result = analyze_cv(cv_text)

if result:
    print(result)  # JSON structuré
else:
    print("Erreur lors de l'analyse")
```

#### Option B: Via l'API Flask

```bash
# Vérifier le statut
curl http://localhost:5000/api/mistral/status

# Analyser un CV
curl -X POST http://localhost:5000/api/mistral/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "cv_text": "Jean Dupont... (texte du CV)"
  }'
```

#### Option C: Utiliser le script de setup automatisé

```bash
python backend/setup_ollama.py
```

## 📁 Structure des fichiers

```
backend/
├── extractors/
│   └── mistral_analyzer.py      # Module principal d'analyse
├── routes/
│   └── mistral_routes.py         # Endpoints Flask pour Mistral
├── setup_ollama.py               # Script de setup automatisé
└── requirements.txt              # Dépendances Python
```

## 🔧 Configuration

### Changer l'URL d'Ollama

Par défaut, le code utilise `http://localhost:11434` (URL par défaut d'Ollama).

Pour utiliser une autre URL:
```python
from extractors.mistral_analyzer import MistralCVAnalyzer

analyzer = MistralCVAnalyzer(ollama_host="http://192.168.1.100:11434")
result = analyzer.analyze_cv(cv_text)
```

### Ajuster les paramètres du modèle

Dans `mistral_analyzer.py`, fonction `_call_ollama()`:

```python
request_data = {
    "model": "mistral",
    "prompt": prompt,
    "stream": False,
    "temperature": 0.3,      # Baisse = plus déterministe
    "top_p": 0.9,            # (Optionnel)
    "top_k": 40,             # (Optionnel)
}
```

## 📊 Structure JSON de sortie

Le modèle retourne:

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
      "description": "Développement d'applications..."
    }
  ],
  "formation": [
    {
      "diplome": "Master Informatique",
      "ecole": "Université X",
      "date_debut": "2016-09-01",
      "date_fin": "2018-06-30"
    }
  ],
  "certifications": ["AWS Solutions Architect"],
  "langues": ["Français", "Anglais", "Espagnol"],
  "competences": ["Python", "Django", "Docker", "PostgreSQL"],
  "resume": "Développeur expérimenté avec..."
}
```

## 🧪 Test

### Test du module

```bash
cd backend
python -m extractors.mistral_analyzer
```

### Test du setup

```bash
python backend/setup_ollama.py
```

### Test avec curl

```bash
# Vérifier la santé
curl http://localhost:5000/api/mistral/health

# Analyser
curl -X POST http://localhost:5000/api/mistral/analyze \
  -H "Content-Type: application/json" \
  -d '{"cv_text": "Mon CV..."}'
```

## 🐛 Dépannage

### "Ollama n'est pas accessible"

**Solution:**
1. Vérifiez qu'Ollama est installé: `ollama --version`
2. Lancez Ollama: `ollama serve` (dans un autre terminal)
3. Vérifiez que le port 11434 n'est pas bloqué

### "Le modèle Mistral n'est pas téléchargé"

**Solution:**
```bash
ollama pull mistral
```

Attendez que le téléchargement (~4 GB) soit complet.

### "Impossible de parser le JSON"

**Cause:** Le modèle a généré une réponse invalide

**Solutions:**
1. Vérifiez que le CV est bien formaté
2. Réessayez - Mistral peut générer du JSON valide au prochain essai
3. Augmentez le nombre de tentatives dans `MistralCVAnalyzer.max_retries`

### Performance lente

**Causes possibles:**
1. La première requête peut être lente (warm-up du modèle)
2. Votre CPU/GPU n'est pas assez puissant
3. Ollama utilise trop de RAM

**Solutions:**
1. Les requêtes suivantes seront plus rapides
2. Fermez d'autres applications
3. Attendez quelques secondes avant la prochaine requête

## 🔐 Sécurité

- ✅ **100% local** - Aucune donnée ne quitte votre machine
- ✅ **Open source** - Code Mistral disponible
- ✅ **Sans API** - Aucune clé API à gérer
- ⚠️ **À protéger** - Isolez le port 11434 sur un réseau public

## 📦 Dépendances Python

Aucune dépendance Python spéciale requise! Le code n'utilise que la stdlib:
- `json` (parsing JSON)
- `logging` (logs)
- `urllib` (requêtes HTTP)
- `subprocess` (lancer les commandes)

## 🎯 Prochaines étapes

1. **Intégration dans l'API:**
   - Ajoutez les blueprints Flask de `mistral_routes.py` à votre `api.py`:
   ```python
   from routes.mistral_routes import mistral_bp
   app.register_blueprint(mistral_bp)
   ```

2. **Pipeline complet:**
   - Combinez avec votre extraction PDF/DOCX
   - Utilisez `analyze_cv()` sur le texte extrait

3. **Optimisations:**
   - Cache des résultats
   - Queue d'attente pour les analyses longues
   - Support de modèles plus petits (quantifiés) pour plus de vitesse

## 📚 Ressources

- [Ollama](https://ollama.ai/)
- [Mistral 7B](https://mistral.ai/)
- [API Ollama](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Format des prompts](https://docs.mistral.ai/capabilities/function_calling/)

## 📝 Notes

- Le modèle utilise le format chat Mistral (optimal pour instruction following)
- Température à 0.3 pour plus de déterminisme
- Retries automatiques en cas d'erreur
- Logs détaillés pour le débogage

## ⚡ Performance attendue

| Configuration | Temps/CV |
|---|---|
| CPU moderne (8+ cores) | 30-60s |
| GPU (RTX 3070+) | 5-15s |
| Première requête | +5-10s (warm-up) |

Doublez ces estimations si vous lancez d'autres applications.

---

**Besoin d'aide?** Vérifiez d'abord les logs avec:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```
