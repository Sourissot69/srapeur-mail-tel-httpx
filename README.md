# Scraper d'Emails et Réseaux Sociaux avec Système de Queue

Scraper web asynchrone en Python pour extraire les emails et réseaux sociaux de sites internet. Système de queue intégré pour gérer plusieurs requêtes.

## 🎯 Fonctionnalités

- ✅ Extraction d'emails avec filtrage intelligent (domaine du site + fournisseurs connus)
- ✅ Extraction de réseaux sociaux (Facebook, Instagram, Twitter, LinkedIn, etc.)
- ✅ Scraping multi-pages (contact, CGV, mentions légales, etc.)
- ✅ **Système de queue FIFO** pour gérer plusieurs requêtes
- ✅ **Gestion des priorités** (1=haute, 10=basse)
- ✅ Scraping asynchrone optimisé (~2.5s par site)
- ✅ Retry logic et rotation User-Agents
- ✅ Rapports JSON simplifiés

## 📋 Prérequis

- Python 3.7 ou supérieur
- pip (gestionnaire de paquets Python)

## 🚀 Installation

```bash
pip install -r requirements.txt
```

## 📖 Utilisation

### ÉTAPE 1 : Démarrer le worker (à laisser tourner)

```bash
python worker.py
```

Le worker attend des jobs dans la queue et les traite automatiquement.

### ÉTAPE 2 : Ajouter des jobs à la queue

**Terminal 1 (User 1) :**
```bash
python add_job.py google-maps-avocats.csv --priority 1
```

**Terminal 2 (User 2) :**
```bash
python add_job.py google-maps-pharmacies.csv --priority 2
```

**Terminal 3 (User 3) :**
```bash
python add_job.py google-maps-notaires.csv --priority 3
```

Les jobs seront traités dans l'ordre de priorité (1 à 10), puis par ordre d'arrivée.

### ÉTAPE 3 : Consulter l'état de la queue

```bash
python monitor.py
```

Affiche :
- Nombre de jobs en attente / en traitement / terminés
- Job en cours avec progression
- Derniers jobs complétés avec stats

## 📊 Résultats

Les résultats sont sauvegardés dans `results/` avec un format simplifié :

**Fichier :** `scraping_nom-du-csv_YYYYMMDD_HHMMSS.json`

### Structure simplifiée

```json
[
  {
    "id": 1,
    "url": "https://example.com",
    "nom": "Example Site",
    "nb_emails": 2,
    "emails": [
      "contact@example.com",
      "info@example.com"
    ],
    "nb_reseaux_sociaux": 3,
    "reseaux_sociaux": {
      "facebook": ["https://facebook.com/example"],
      "instagram": ["https://instagram.com/example"],
      "linkedin": ["https://linkedin.com/company/example"]
    }
  }
]
```

## 🔧 Configuration

Paramètres optimisés dans `config.py` :

- **MAX_CONCURRENT_SITES** : 10 sites en parallèle
- **MAX_PAGES_PER_SITE** : 7 pages par site
- **TIMEOUT** : 10 secondes par requête
- **SITE_TIMEOUT** : 30 secondes par site
- **DELAY_BETWEEN_REQUESTS** : 0.3 secondes (optimisé)

**Performance moyenne : ~2.5s par site**

## 📧 Filtrage des Emails

Le scraper garde uniquement les emails qui :

1. **Appartiennent au domaine du site** (ex: contact@example.com pour example.com)
2. **Proviennent de fournisseurs connus** (gmail, hotmail, yahoo, outlook, etc.)

Cela évite les faux positifs et les emails non pertinents.

## 🌐 Pages Scrapées

Le scraper visite automatiquement :

- Page d'accueil
- /contact, /contactez-nous
- /mentions-legales, /legal-notice
- /cgv, /conditions-generales-vente
- /cgu, /conditions-generales-utilisation
- /politique-confidentialite, /privacy-policy
- /rgpd, /donnees-personnelles
- /about, /a-propos
- Liens détectés dans le footer

## 🔍 Sections Analysées

Pour chaque page, le scraper analyse :

- **Footer** (zone la plus riche en informations de contact)
- **Header/Navigation**
- **Sections Contact**
- **Mentions légales / CGV / CGU**
- **Sidebar**
- **Métadonnées** (balises meta)
- **Données structurées** (JSON-LD, Schema.org)
- **Liens mailto:**

## 📝 Logs

Les logs sont sauvegardés dans `scraper.log` avec :
- Progression du scraping
- Emails et réseaux sociaux trouvés
- Erreurs et timeouts
- Statistiques finales

## 🔄 Système de Queue

### Workflow multi-utilisateurs :

1. **User 1** ajoute un job → `add_job.py avocats.csv --priority 1`
2. **User 2** ajoute un job → `add_job.py pharmacies.csv --priority 2`  
3. **Worker** traite les jobs dans l'ordre (priorité puis FIFO)
4. **Résultats** disponibles dans `results/`

### Commandes :

```bash
# Démarrer le worker (terminal dédié)
python worker.py

# Ajouter des jobs (n'importe quel terminal)
python add_job.py mon_fichier.csv --priority 5 --user "Nom"

# Voir l'état de la queue
python monitor.py
```

## ⚠️ Sécurité et Bonnes Pratiques

- ✅ **1 seul worker** → Évite bannissement IP
- ✅ **Délais entre requêtes** (0.3s) → Respectueux
- ✅ **Filtrage emails** → Seulement domaine du site + fournisseurs connus
- ⚠️ **Usage légal uniquement** → Sites publics seulement
- ⚠️ **Respecter RGPD** → Ne pas abuser des données

## 🐛 Dépannage

### Le worker ne traite pas les jobs

Vérifiez que le worker tourne : `python worker.py`

### Erreur "CSV introuvable"

Utilisez le chemin complet ou relatif correct du CSV

## 📄 Licence

Usage éducatif et personnel uniquement.


