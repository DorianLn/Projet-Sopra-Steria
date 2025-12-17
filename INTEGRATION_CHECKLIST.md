# ✅ CHECKLIST D'INTÉGRATION - Mistral 7B

## Phase 1: Installation système (10-30 minutes)

### Étape 1.1: Installer Ollama
- [ ] Télécharger Ollama depuis https://ollama.ai/download
- [ ] Exécuter l'installer
- [ ] Vérifier l'installation: `ollama --version`

**Resources:**
- Windows: https://ollama.ai/download/windows
- macOS: https://ollama.ai/download/mac
- Linux: `curl https://ollama.ai/install.sh | sh`

### Étape 1.2: Lancer Ollama
- [ ] Ouvrir un terminal
- [ ] Exécuter: `ollama serve`
- [ ] Garder le terminal ouvert en arrière-plan

### Étape 1.3: Télécharger Mistral
- [ ] Ouvrir un NOUVEAU terminal
- [ ] Exécuter: `ollama pull mistral`
- [ ] Attendre la fin du téléchargement (~4 GB)
- [ ] Vérifier: `ollama list` (Mistral doit apparaître)

---

## Phase 2: Vérification du projet (5 minutes)

### Étape 2.1: Vérifier les fichiers créés
- [ ] `backend/extractors/mistral_analyzer.py` existe
- [ ] `backend/routes/mistral_routes.py` existe
- [ ] `backend/setup_ollama.py` existe
- [ ] `backend/startup.py` existe
- [ ] Documentation existe:
  - [ ] `MISTRAL_QUICKSTART.md`
  - [ ] `Docs/MISTRAL_GUIDE.md`
  - [ ] `backend/INTEGRATION_MISTRAL.md`

### Étape 2.2: Vérifier l'environment Python
- [ ] Python 3.8+ installé: `python --version`
- [ ] Environment virtuel actif: `(venv)` visible dans le terminal
- [ ] Dépendances installées: `pip install -r requirements.txt`

### Étape 2.3: Tester Mistral seul
```bash
python -c "from extractors.mistral_analyzer import verify_mistral_setup; print(verify_mistral_setup())"
```
- [ ] Résultat: `'status': 'OK'`

---

## Phase 3: Test du module (10 minutes)

### Étape 3.1: Test simple
```bash
python -c "
from extractors.mistral_analyzer import analyze_cv
result = analyze_cv('Jean Dupont\nEmail: jean@example.com\nDéveloppeur')
print(result)
"
```
- [ ] Résultat: JSON structuré avec identité, contact, etc.

### Étape 3.2: Lancer les exemples
```bash
python backend/examples_mistral.py
```
- [ ] Résultat: 7 exemples fonctionnent sans erreur

### Étape 3.3: Lancer les tests
```bash
python -m pytest backend/test_mistral.py -v
```
- [ ] Résultat: Tous les tests passent

---

## Phase 4: Intégration API Flask (10 minutes)

### Étape 4.1: Ajouter les imports
Éditer `backend/api.py`:
```python
# Ajouter après les autres imports:
from extractors.mistral_analyzer import analyze_cv as mistral_analyze_cv
from routes.mistral_routes import mistral_bp
```
- [ ] Imports ajoutés

### Étape 4.2: Enregistrer le blueprint
Éditer `backend/api.py` (après `CORS(app)`):
```python
# Enregistrer les routes Mistral
app.register_blueprint(mistral_bp)
```
- [ ] Blueprint enregistré

### Étape 4.3: Tester les endpoints Mistral
```bash
# Terminal 1: Lancer l'API
python backend/api.py

# Terminal 2: Tester
curl http://localhost:5000/api/mistral/status
curl -X POST http://localhost:5000/api/mistral/analyze \
  -H "Content-Type: application/json" \
  -d '{"cv_text": "Jean Dupont..."}'
```
- [ ] Endpoints répondent correctement

---

## Phase 5: Startup complet (5 minutes)

### Étape 5.1: Tester le startup
```bash
python backend/startup.py
```
- [ ] Toutes les vérifications passent
- [ ] API démarre avec succès

### Étape 5.2: Accéder à l'API
- [ ] Ouvrir http://localhost:5000
- [ ] Vérifier que l'API fonctionne

---

## Phase 6: Production (optionnel)

### Étape 6.1: Logs et monitoring
- [ ] Configurer les logs: `LOG_LEVEL=INFO` dans `.env.mistral`
- [ ] Tester les logs: `python maintenance.py` → Option 9

### Étape 6.2: Sauvegarde automatique
- [ ] `AUTO_SAVE_RESULTS=true` dans `.env.mistral`
- [ ] Dossier `backend/data/output` existe

### Étape 6.3: Maintenance
- [ ] Lancer le menu maintenance: `python backend/maintenance.py`
- [ ] Tester le nettoyage des fichiers temporaires

---

## Tests de validation finale

### ✅ Test 1: Module seul
```python
from extractors.mistral_analyzer import analyze_cv

cv = """
Jean Dupont
jean@example.com
06 12 34 56 78
Développeur Python - 5 ans d'expérience
"""

result = analyze_cv(cv)
assert result is not None
assert "identite" in result
assert "contact" in result
print("✓ Module fonctionne")
```

### ✅ Test 2: API Flask
```bash
curl -X POST http://localhost:5000/api/mistral/analyze \
  -H "Content-Type: application/json" \
  -d '{"cv_text": "Jean Dupont"}'
```
- Réponse: `{"success": true, "data": {...}}`

### ✅ Test 3: Vérification setup
```python
from extractors.mistral_analyzer import verify_mistral_setup
status = verify_mistral_setup()
assert status['status'] == 'OK'
```

### ✅ Test 4: Avec fichier CV
```bash
# Créer un fichier test.txt avec un CV
echo "Jean Dupont, Développeur" > test.txt

# Analyser
python -c "
from extractors.mistral_analyzer import analyze_cv
with open('test.txt') as f:
    result = analyze_cv(f.read())
    print(result)
"
```

---

## Dépannage

### ❌ "Ollama n'est pas accessible"
- [ ] Ollama est installé: `ollama --version`
- [ ] Ollama tourne: `ollama serve` dans un autre terminal
- [ ] Port 11434 n'est pas bloqué

### ❌ "Mistral n'est pas téléchargé"
- [ ] Exécuter: `ollama pull mistral`
- [ ] Vérifier: `ollama list` (Mistral doit y être)

### ❌ "ImportError: No module named 'extractors'"
- [ ] Vérifier le chemin: Être dans le dossier `backend`
- [ ] `sys.path` contient le répertoire courant

### ❌ "JSON parsing error"
- [ ] Mistral peut générer du JSON invalide parfois
- [ ] Retries automatiques (3 fois par défaut)
- [ ] Vérifier les logs: `python maintenance.py` → Option 9

### ❌ "Request timeout"
- [ ] Mistral peut être lent la première fois
- [ ] Attendre 2-3 minutes
- [ ] Aumenter OLLAMA_TIMEOUT dans `.env.mistral`

---

## Optimisations optionnelles

### Performance
- [ ] GPU activé pour Ollama (si disponible)
- [ ] Température ajustée (0.3 = déterministe)
- [ ] Cache des résultats?

### Fiabilité
- [ ] Retries augmentés si nécessaire
- [ ] Timeouts adaptés à votre infrastructure
- [ ] Fallback vers analyse classique?

### Sécurité
- [ ] Port 11434 isolé sur réseau public
- [ ] Validation des inputs
- [ ] Logs détaillés pour audit

---

## Ressources

📚 Documentation créée:
- `MISTRAL_QUICKSTART.md` - Démarrage rapide (5 min)
- `Docs/MISTRAL_GUIDE.md` - Guide complet (30 min)
- `backend/INTEGRATION_MISTRAL.md` - Intégration API
- `backend/examples_mistral.py` - 7 exemples complets
- `backend/test_mistral.py` - Tests unitaires

🔗 Liens utiles:
- Ollama: https://ollama.ai/
- Mistral: https://mistral.ai/
- API Ollama: https://github.com/ollama/ollama/blob/main/docs/api.md

---

## Points importants à retenir

1. **Ollama doit rester actif** - Gardez `ollama serve` lancé
2. **Première requête lente** - C'est normal (warm-up du modèle)
3. **100% local** - Aucune données n'envoie vers l'extérieur
4. **Pas de dépendances** - Utilise seulement stdlib Python
5. **Retries automatiques** - Les erreurs JSON sont gérées

---

## Après l'intégration

Une fois tout en place, vous pouvez:

✅ Analyser des CVs avec Mistral:
```python
from extractors.mistral_analyzer import analyze_cv
result = analyze_cv(cv_text)
```

✅ Utiliser l'API:
```bash
POST /api/mistral/analyze
```

✅ Combiner avec votre analyse classique:
```python
# Analyse classique + Mistral
```

✅ Monitorer le système:
```bash
python backend/maintenance.py
```

---

**🎉 Intégration terminée!**

Votre projet Sopra Steria utilise maintenant Mistral 7B en local avec Ollama.

Besoin d'aide? Consultez la documentation complète:
1. `MISTRAL_QUICKSTART.md` pour un démarrage rapide
2. `Docs/MISTRAL_GUIDE.md` pour la documentation complète
3. `backend/examples_mistral.py` pour des exemples
4. `backend/test_mistral.py --manual` pour tester
