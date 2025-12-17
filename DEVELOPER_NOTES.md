# 📝 NOTES DE DÉVELOPPEMENT - Mistral Integration

## Architecture Décisions

### 1. Pas de dépendances Python supplémentaires
**Décision:** Utiliser uniquement `urllib` de stdlib au lieu de `requests`
**Raison:** Réduire les dépendances et la surface d'attaque
**Impact:** Code légèrement plus verbeux mais autonome

### 2. Classe + Fonction wrapper
**Décision:** Créer une classe `MistralCVAnalyzer` ET une fonction `analyze_cv()`
**Raison:** Flexibilité - utilisateurs peuvent utiliser la classe ou la fonction
**Impact:** Deux APIs disponibles pour différents cas d'usage

### 3. Température basse par défaut (0.3)
**Décision:** `temperature: 0.3` pour plus de déterminisme
**Raison:** Pour l'extraction de CV, on veut de la cohérence pas de créativité
**Impact:** Résultats plus reproductibles

### 4. Retries automatiques (3x)
**Décision:** Réessayer automatiquement en cas d'erreur JSON
**Raison:** Mistral génère occasionnellement du JSON invalide
**Impact:** Plus résilient mais +latence en cas d'erreur

### 5. Parsing JSON robuste
**Décision:** Chercher les limites du JSON au lieu de parser directement
**Raison:** Mistral peut retourner du texte avant/après le JSON
**Impact:** Plus flexible et forgiving

---

## Points d'extension futurs

### 1. Cache des résultats
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def analyze_cv(text):
    # Implémenter le cache
    pass
```

### 2. Support de plusieurs modèles
```python
class MistralCVAnalyzer:
    def __init__(self, model="mistral"):
        self.model_name = model
    
    def switch_model(self, new_model):
        # Changer de modèle
        pass
```

### 3. Streaming de réponses
```python
def analyze_cv_stream(text):
    # Implémenter le streaming pour grandes réponses
    pass
```

### 4. Batch processing avec queue
```python
from queue import Queue
from threading import Thread

class BatchAnalyzer:
    def __init__(self, max_workers=4):
        self.queue = Queue()
        self.workers = [Thread(target=self._worker) for _ in range(max_workers)]
```

### 5. Support de plusieurs formats d'output
```python
class MistralCVAnalyzer:
    def analyze_cv(self, text, format="json"):
        # Support json, xml, csv, etc.
        pass
```

---

## Optimisations possibles

### Performance
- [ ] Cache LRU pour les CVs similaires
- [ ] Utiliser async/await pour les appels Ollama
- [ ] Pipeline de traitement parallèle
- [ ] Quantization du modèle (INT8)
- [ ] Model distillation

### Fiabilité
- [ ] Circuit breaker pour Ollama
- [ ] Health checks périodiques
- [ ] Logging structuré (JSON)
- [ ] Metrics Prometheus
- [ ] Fallback sur analyse classique

### Scalabilité
- [ ] Load balancer devant plusieurs Ollama
- [ ] Cache distribué (Redis)
- [ ] Queue de traitement (Celery)
- [ ] Database pour les résultats
- [ ] API Webhook pour notifications

---

## Considérations de sécurité

### Input Validation
```python
def analyze_cv(text: str) -> Optional[Dict]:
    # Valider la taille
    if len(text) > 100000:
        raise ValueError("CV trop volumineux")
    
    # Valider le contenu
    if not text.strip():
        raise ValueError("CV vide")
```

### Rate Limiting
```python
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests=10, window=60):
        self.max_requests = max_requests
        self.window = window
        self.requests = []
    
    def is_allowed(self):
        now = datetime.now()
        self.requests = [r for r in self.requests 
                        if now - r < timedelta(seconds=self.window)]
        
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False
```

### Sanitization
```python
def sanitize_cv(text: str) -> str:
    # Retirer les caractères dangereux
    # Normaliser les espaces
    # Limiter la longueur
    pass
```

---

## Testing Strategy

### Unit Tests
- [x] Parser JSON
- [x] Prompt building
- [x] Error handling
- [x] Initialization

### Integration Tests
- [ ] Communication Ollama (skip si offline)
- [ ] Full pipeline
- [ ] Error scenarios

### Performance Tests
- [ ] Temps de réponse
- [ ] Utilisation mémoire
- [ ] Throughput

### Load Tests
- [ ] Multiple concurrent requests
- [ ] Memory leaks
- [ ] Connection pooling

---

## Known Issues & Workarounds

### Issue 1: JSON invalide de Mistral
**Problem:** Mistral génère parfois du JSON invalide
**Workaround:** Retries automatiques (implémenté)
**Future:** Fine-tuning sur JSON structuré

### Issue 2: Première requête lente
**Problem:** Warm-up du modèle ~5-10s
**Workaround:** Documenter, informer l'utilisateur
**Future:** Keep-alive connection

### Issue 3: Timeout sur CVs très longs
**Problem:** Timeouts avec CVs >10000 caractères
**Workaround:** Augmenter timeout dans `.env.mistral`
**Future:** Chunking automatique

### Issue 4: Ollama crash occasionnel
**Problem:** Ollama peut crash sous charge
**Workaround:** Restart automatique + health checks
**Future:** Isoler Ollama en service systemd

---

## Monitoring & Logging

### Logs à implémenter
```python
import logging

logger = logging.getLogger(__name__)

# Levels
logger.debug("Calling Ollama...")      # Verbeux
logger.info("Analysis successful")      # Infos
logger.warning("Retry attempt 2/3")     # Attentions
logger.error("Connection failed")       # Erreurs
logger.critical("Service down")         # Critiques
```

### Metrics à tracker
- Nombre d'analyses par jour
- Temps moyen par analyse
- Taux de succès/erreur
- Taille moyenne des CVs
- Latence de réponse Ollama
- Utilisation mémoire/CPU

### Alertes recommandées
- Ollama down
- Taux d'erreur > 5%
- Latence > 120s
- Utilisation mémoire > 80%
- Aucune requête en 30 minutes

---

## Roadmap

### Phase 1 (✅ Complétée)
- [x] Module Mistral de base
- [x] Routes Flask
- [x] Documentation
- [x] Tests de base
- [x] Exemples

### Phase 2 (À faire)
- [ ] Cache des résultats
- [ ] Async/await
- [ ] Metrics Prometheus
- [ ] Logging structuré
- [ ] Health checks

### Phase 3 (À faire)
- [ ] Support multi-modèles
- [ ] Batch processing
- [ ] Pipeline d'inférence
- [ ] Fine-tuning
- [ ] Model distillation

### Phase 4 (À faire)
- [ ] Load balancing
- [ ] Cache distribué
- [ ] Queue de traitement
- [ ] Monitoring avancé
- [ ] Auto-scaling

---

## Standards & Conventions

### Code Style
```python
# PEP 8
# - 80 caractères max par ligne
# - 4 espaces d'indentation
# - snake_case pour fonctions/variables
# - UPPER_CASE pour constantes

# Type hints
def analyze_cv(text: str) -> Optional[Dict[str, Any]]:
    """Docstring avec description."""
    pass
```

### Naming Conventions
```
Classes:        PascalCase (MistralCVAnalyzer)
Functions:      snake_case (analyze_cv)
Constants:      UPPER_SNAKE_CASE (MAX_RETRIES)
Private:        _prefix (_call_ollama)
Protected:      __dunder (si vraiment nécessaire)
```

### Documentation
```python
def analyze_cv(text: str) -> Optional[Dict[str, Any]]:
    """
    Analyse un CV avec Mistral et retourne JSON structuré.
    
    Args:
        text: Texte du CV à analyser
        
    Returns:
        Dict contenant les informations structurées, ou None en cas d'erreur
        
    Raises:
        ValueError: Si le texte est vide
        ConnectionError: Si Ollama n'est pas accessible
        
    Examples:
        >>> result = analyze_cv("Jean Dupont...")
        >>> result['identite']['nom']
        'Dupont'
    """
    pass
```

---

## Déploiement

### Dépendances système
- Python 3.8+
- Ollama (accessible sur localhost:11434)
- ~4 GB RAM
- ~10 GB disque (pour Mistral)

### Vérification pré-déploiement
```bash
# Tests
python -m pytest backend/test_mistral.py

# Verification
python backend/startup.py

# Health check
python quick_test.py
```

### Variables d'environnement
```bash
export OLLAMA_HOST=http://localhost:11434
export MISTRAL_TEMPERATURE=0.3
export MISTRAL_MAX_RETRIES=3
```

### Docker (optionnel)
```dockerfile
FROM python:3.9

RUN pip install -r requirements.txt

# Ollama doit tourner en-dehors du container
ENV OLLAMA_HOST=http://ollama:11434

CMD ["python", "api.py"]
```

---

## Troubleshooting Guide

### Problème: ImportError
```
Solution:
1. Vérifier les chemins Python
2. Vérifier que backend/ est dans sys.path
3. Lancer depuis le dossier backend
```

### Problème: Connection refused
```
Solution:
1. Vérifier qu'Ollama tourne: ollama serve
2. Vérifier le port: lsof -i :11434
3. Vérifier le firewall
```

### Problème: JSON parse error
```
Solution:
1. Retries automatiques gèrent cela
2. Vérifier les logs pour plus de détails
3. Augmenter max_retries si nécessaire
```

### Problème: Out of memory
```
Solution:
1. Fermer les autres applications
2. Utiliser un modèle quantisé (INT8)
3. Augmenter la RAM système
4. Chunking des CVs longs
```

---

## Performance Tips

### Pour l'utilisateur
- Garder Ollama actif
- Première requête peut être lente
- Les suivantes sont rapides
- Fermer autres applications

### Pour le développeur
- Cache des résultats fréquents
- Batch processing pour plusieurs CVs
- Utiliser GPU si disponible
- Quantization du modèle

### Pour l'infra
- Load balancing
- Keep-alive connections
- Connection pooling
- Resource monitoring

---

## Resources & References

### Documentation officielles
- https://ollama.ai/
- https://mistral.ai/
- https://github.com/ollama/ollama

### Code samples
- [mistral_analyzer.py](backend/extractors/mistral_analyzer.py)
- [examples_mistral.py](backend/examples_mistral.py)
- [test_mistral.py](backend/test_mistral.py)

### Guides
- [MISTRAL_GUIDE.md](../Docs/MISTRAL_GUIDE.md)
- [ARCHITECTURE.md](../ARCHITECTURE.md)
- [INTEGRATION_CHECKLIST.md](../INTEGRATION_CHECKLIST.md)

---

## Contact & Support

Pour questions/problèmes:
1. Consultez la documentation
2. Vérifiez les logs
3. Lancez les tests
4. Lisez les exemples

---

**Document de développement - Mistral 7B Integration**  
*Dernière mise à jour: 2024*
