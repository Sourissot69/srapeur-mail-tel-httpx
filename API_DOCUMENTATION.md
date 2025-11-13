# Documentation API Web - Port 8014

## 🌐 Base URL

```
http://VOTRE_IP_VPS:8014
```

## 📋 Endpoints

### 1. Health Check

**GET** `/health`

Vérifie que l'API fonctionne.

**Réponse :**
```json
{
  "status": "ok",
  "service": "Scraper API",
  "port": 8014,
  "timestamp": "2025-11-13T10:00:00"
}
```

---

### 2. Upload CSV

**POST** `/upload`

Upload un fichier CSV.

**Paramètres :**
- `file` : Fichier CSV (multipart/form-data)

**Exemple (curl) :**
```bash
curl -X POST http://VOTRE_IP:8014/upload \
  -F "file=@mon_fichier.csv"
```

**Réponse :**
```json
{
  "success": true,
  "filename": "20251113_100000_mon_fichier.csv",
  "path": "uploads/20251113_100000_mon_fichier.csv"
}
```

---

### 3. Créer un Job

**POST** `/job`

Crée un job de scraping.

**Body (JSON) :**
```json
{
  "csv_file": "uploads/20251113_100000_mon_fichier.csv",
  "priority": 1,
  "user": "Alice"
}
```

**Paramètres :**
- `csv_file` : Chemin vers le CSV (requis)
- `priority` : Priorité 1-10 (optionnel, défaut: 5)
- `user` : Nom utilisateur (optionnel, défaut: "API")

**Exemple (curl) :**
```bash
curl -X POST http://VOTRE_IP:8014/job \
  -H "Content-Type: application/json" \
  -d '{
    "csv_file": "uploads/mon_fichier.csv",
    "priority": 1,
    "user": "Alice"
  }'
```

**Réponse :**
```json
{
  "success": true,
  "message": "Job ajouté à la queue",
  "csv_file": "uploads/mon_fichier.csv",
  "priority": 1,
  "user": "Alice"
}
```

---

### 4. Upload + Démarrer Job (Tout-en-un)

**POST** `/job/upload-and-start`

Upload un CSV et crée le job immédiatement.

**Paramètres (multipart/form-data) :**
- `file` : Fichier CSV
- `priority` : Priorité 1-10 (optionnel)
- `user` : Nom utilisateur (optionnel)

**Exemple (curl) :**
```bash
curl -X POST http://VOTRE_IP:8014/job/upload-and-start \
  -F "file=@mon_fichier.csv" \
  -F "priority=1" \
  -F "user=Alice"
```

**Réponse :**
```json
{
  "success": true,
  "message": "CSV uploadé et job ajouté",
  "filename": "20251113_100000_mon_fichier.csv",
  "priority": 1
}
```

---

### 5. État de la Queue

**GET** `/queue`

Obtient l'état de la queue.

**Exemple :**
```bash
curl http://VOTRE_IP:8014/queue
```

**Réponse :**
```json
{
  "pending": 2,
  "processing": 1,
  "completed": 15,
  "pending_jobs": [
    {
      "id": "20251113_100000_123456",
      "csv_file": "avocats.csv",
      "user": "Alice",
      "priority": 1,
      "created_at": "2025-11-13T10:00:00"
    },
    {
      "id": "20251113_100030_789012",
      "csv_file": "pharmacies.csv",
      "user": "Bob",
      "priority": 5,
      "created_at": "2025-11-13T10:00:30"
    }
  ]
}
```

---

### 6. Liste des Résultats

**GET** `/results`

Liste tous les résultats disponibles.

**Exemple :**
```bash
curl http://VOTRE_IP:8014/results
```

**Réponse :**
```json
{
  "count": 3,
  "results": [
    {
      "filename": "scraping_avocats_20251113_100530.json",
      "size": 15642,
      "created": "2025-11-13T10:05:30"
    },
    {
      "filename": "scraping_pharmacies_20251113_095230.json",
      "size": 23891,
      "created": "2025-11-13T09:52:30"
    }
  ]
}
```

---

### 7. Télécharger un Résultat

**GET** `/results/<filename>`

Télécharge un fichier de résultats.

**Exemple :**
```bash
curl http://VOTRE_IP:8014/results/scraping_avocats_20251113_100530.json \
  --output resultat.json
```

---

## 🔧 Démarrage de l'API

### Sur VPS (systemd) :
```bash
sudo systemctl start scraper-api
sudo systemctl enable scraper-api
```

### Manuel (développement) :
```bash
python api_server.py
```

---

## 🔒 Sécurité

### Firewall
```bash
# Ouvrir le port 8014
sudo ufw allow 8014/tcp
sudo ufw reload
```

### Authentification (À AJOUTER)

Pour sécuriser l'API en production, ajoutez :
- Token d'authentification
- Rate limiting
- HTTPS avec certificat SSL

---

## 📊 Exemple d'Utilisation Complète

### Workflow avec l'API :

```bash
# 1. Vérifier que l'API fonctionne
curl http://VOTRE_IP:8014/health

# 2. Upload CSV et créer job
curl -X POST http://VOTRE_IP:8014/job/upload-and-start \
  -F "file=@mon_fichier.csv" \
  -F "priority=1" \
  -F "user=Alice"

# 3. Vérifier l'état de la queue
curl http://VOTRE_IP:8014/queue

# 4. Attendre fin du traitement (polling)
watch -n 5 'curl -s http://VOTRE_IP:8014/queue'

# 5. Lister les résultats
curl http://VOTRE_IP:8014/results

# 6. Télécharger le résultat
curl http://VOTRE_IP:8014/results/scraping_mon_fichier_TIMESTAMP.json \
  --output resultat.json
```

---

## 🐍 Exemple avec Python

```python
import requests

# URL de l'API
API_URL = "http://VOTRE_IP:8014"

# 1. Upload et démarrer job
with open('mon_fichier.csv', 'rb') as f:
    response = requests.post(
        f"{API_URL}/job/upload-and-start",
        files={'file': f},
        data={'priority': 1, 'user': 'Alice'}
    )
    print(response.json())

# 2. Vérifier l'état
response = requests.get(f"{API_URL}/queue")
print(response.json())

# 3. Liste des résultats
response = requests.get(f"{API_URL}/results")
results = response.json()['results']

# 4. Télécharger le dernier résultat
if results:
    filename = results[0]['filename']
    response = requests.get(f"{API_URL}/results/{filename}")
    with open('resultat.json', 'wb') as f:
        f.write(response.content)
```

---

## 🌐 Interface Web (Future)

Créer une interface HTML simple pour :
- Upload CSV via drag & drop
- Voir l'état de la queue en temps réel
- Télécharger les résultats

Fichier : `static/index.html` (à créer)

