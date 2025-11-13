# Guide de Publication sur GitHub

## 📝 Préparation

### 1. Créer un repository sur GitHub

1. Aller sur https://github.com
2. Cliquer sur "New repository"
3. Nom : `scraper-emails-reseaux-sociaux` (ou autre)
4. Description : "Scraper web pour extraire emails et réseaux sociaux avec système de queue"
5. Public ou Private (votre choix)
6. **NE PAS** cocher "Add README" (on a déjà le nôtre)
7. Créer le repository

### 2. Initialiser Git localement

Ouvrir un terminal dans le dossier du projet :

```bash
# Initialiser Git
git init

# Ajouter tous les fichiers
git add .

# Premier commit
git commit -m "Initial commit - Scraper avec système de queue"

# Ajouter le remote GitHub (remplacer par votre URL)
git remote add origin https://github.com/votre-username/scraper-emails-reseaux-sociaux.git

# Pousser sur GitHub
git branch -M main
git push -u origin main
```

## 🔒 Vérifications avant publication

### Fichiers à NE PAS commiter (déjà dans .gitignore)

✅ **Déjà protégé :**
- `*.csv` - Vos données CSV
- `results/*.json` - Résultats de scraping
- `queue/**/*.json` - Jobs en cours/terminés
- `*.log` - Logs
- `.env` - Configuration sensible
- `__pycache__/` - Cache Python

### Nettoyage avant publication

```bash
# Supprimer les résultats locaux
rm -rf results/*.json
rm -rf queue/pending/*.json
rm -rf queue/processing/*.json
rm -rf queue/completed/*.json
rm -f *.log

# Vérifier ce qui sera commité
git status
```

## 📄 README.md pour GitHub

Le README.md est déjà optimisé avec :
- ✅ Description claire
- ✅ Instructions d'installation
- ✅ Exemples d'utilisation
- ✅ Documentation système de queue
- ✅ Format des résultats

## 🏷️ Tags et Releases

### Créer une release

```bash
# Créer un tag
git tag -a v1.0.0 -m "Version 1.0.0 - Système de queue opérationnel"

# Pousser le tag
git push origin v1.0.0
```

Puis sur GitHub :
1. Aller dans "Releases"
2. "Create a new release"
3. Choisir le tag v1.0.0
4. Titre : "v1.0.0 - Premier release"
5. Description : Features + statistiques
6. Publier

## 📦 Structure finale sur GitHub

```
votre-repo/
├── .gitignore
├── README.md
├── GUIDE_UTILISATION.txt
├── DEPLOIEMENT_VPS.md
├── requirements.txt
├── .env.example
├── config.py
├── scraper.py
├── extractors.py
├── utils.py
├── add_job.py
├── worker.py
├── monitor.py
├── run_scraper.py
├── install_vps.sh
├── install_service.sh
├── deploy.sh
├── queue/
│   ├── pending/.gitkeep
│   ├── processing/.gitkeep
│   └── completed/.gitkeep
└── results/.gitkeep
```

## 🎨 Badges GitHub (optionnel)

Ajouter en haut du README.md :

```markdown
![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
```

## 🔐 Secrets GitHub (pour CI/CD futur)

Si vous voulez ajouter CI/CD plus tard :

1. Aller dans Settings → Secrets and variables → Actions
2. Ajouter :
   - `VPS_HOST` : IP du VPS
   - `VPS_USER` : Utilisateur SSH
   - `VPS_SSH_KEY` : Clé SSH privée

## 📊 GitHub Actions (optionnel)

Créer `.github/workflows/deploy.yml` pour déploiement automatique :

```yaml
name: Deploy to VPS

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to VPS
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd /opt/scrapeur-site-web
            git pull
            source venv/bin/activate
            pip install -r requirements.txt
            sudo systemctl restart scraper-worker
```

## ✅ Checklist avant publication

- [ ] Supprimer tous les CSV de données
- [ ] Supprimer tous les résultats JSON
- [ ] Supprimer les logs
- [ ] Vérifier .gitignore
- [ ] Tester git status (aucun fichier sensible)
- [ ] Modifier deploy.sh avec la vraie IP VPS
- [ ] README.md complet et clair
- [ ] License ajoutée (MIT ou autre)
- [ ] Tests effectués localement

## 📝 Description GitHub recommandée

**Short description :**
```
Scraper web asynchrone pour extraire emails et réseaux sociaux. Système de queue FIFO intégré. ~2.5s/site. Python 3.7+
```

**Topics (tags) :**
- web-scraping
- python
- async
- httpx
- beautifulsoup
- email-extraction
- social-media
- queue-system
- google-maps

## 🎯 Prêt pour publication !

Après ces étapes, votre projet sera :
- ✅ Sur GitHub (code source)
- ✅ Déployable sur VPS Hostinger en 1 commande
- ✅ Service systemd qui tourne 24/7
- ✅ Multi-utilisateurs avec queue
- ✅ Documentation complète

