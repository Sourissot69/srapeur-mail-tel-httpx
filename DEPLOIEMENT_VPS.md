# Guide de Déploiement sur VPS Hostinger

## 📋 Prérequis

- VPS Hostinger avec Ubuntu 20.04+ ou Debian 11+
- Accès SSH root ou sudo
- Au moins 1 GB RAM (2 GB recommandé)
- 10 GB d'espace disque

## 🚀 Installation sur VPS

### Étape 1 : Connexion SSH au VPS

```bash
ssh root@votre-ip-vps
# ou
ssh user@votre-ip-vps
```

### Étape 2 : Cloner le projet depuis GitHub

```bash
cd /home/votre-user
git clone https://github.com/votre-username/scrapeur-site-web.git
cd scrapeur-site-web
```

### Étape 3 : Installation automatique

```bash
bash install_vps.sh
```

Ce script va :
- Mettre à jour le système
- Installer Python 3 et pip
- Créer un environnement virtuel
- Installer toutes les dépendances
- Créer les dossiers nécessaires

### Étape 4 : Installer le service systemd (worker permanent)

```bash
sudo bash install_service.sh
```

### Étape 5 : Démarrer le worker

```bash
# Démarrer le service
sudo systemctl start scraper-worker

# Activer au démarrage du VPS
sudo systemctl enable scraper-worker

# Vérifier le status
sudo systemctl status scraper-worker
```

## 📊 Utilisation sur VPS

### Ajouter des jobs via SSH

**Option 1 : SSH direct**
```bash
ssh user@votre-ip-vps
cd /home/user/scrapeur-site-web
source venv/bin/activate
python add_job.py mon_fichier.csv --priority 1 --user "Alice"
```

**Option 2 : Upload CSV + ajouter job**
```bash
# Depuis votre PC local
scp mon_fichier.csv user@votre-ip-vps:/home/user/scrapeur-site-web/

# Puis SSH
ssh user@votre-ip-vps
cd /home/user/scrapeur-site-web
source venv/bin/activate
python add_job.py mon_fichier.csv --priority 1
```

### Consulter l'état de la queue

```bash
ssh user@votre-ip-vps
cd /home/user/scrapeur-site-web
source venv/bin/activate
python monitor.py
```

### Récupérer les résultats

```bash
# Depuis votre PC local
scp user@votre-ip-vps:/home/user/scrapeur-site-web/results/*.json ./
```

## 🔧 Gestion du Service

### Commandes principales

```bash
# Démarrer le worker
sudo systemctl start scraper-worker

# Arrêter le worker
sudo systemctl stop scraper-worker

# Redémarrer le worker
sudo systemctl restart scraper-worker

# Voir le status
sudo systemctl status scraper-worker

# Activer au démarrage
sudo systemctl enable scraper-worker

# Désactiver au démarrage
sudo systemctl disable scraper-worker
```

### Consulter les logs

```bash
# Logs du worker
tail -f logs/worker.log

# Logs d'erreur
tail -f logs/worker_error.log

# Logs systemd
sudo journalctl -u scraper-worker -f
```

## 🌐 API Web (Optionnel - Future amélioration)

Pour faciliter l'utilisation, vous pouvez ajouter une API web :

**Structure :**
```
api/
  └── app.py          # Flask/FastAPI
      ├── POST /upload    # Upload CSV
      ├── POST /job       # Créer job
      ├── GET /status     # État de la queue
      └── GET /results/:id # Télécharger résultat
```

**Installation :**
```bash
pip install flask flask-cors
python api/app.py
```

**Accès :**
- API : `http://votre-ip-vps:5000`
- Upload CSV via interface web
- Téléchargement automatique des résultats

## 🔒 Sécurité VPS

### Firewall

```bash
# Autoriser seulement SSH
sudo ufw allow 22/tcp
sudo ufw enable

# Si API Web activée
sudo ufw allow 5000/tcp
```

### Créer un utilisateur dédié

```bash
# Créer utilisateur scraper
sudo adduser scraper
sudo usermod -aG sudo scraper

# Installer le projet dans /home/scraper
su - scraper
```

### Limiter les ressources

Modifier `/etc/systemd/system/scraper-worker.service` :

```ini
[Service]
# Limiter RAM à 2 GB
MemoryLimit=2G

# Limiter CPU à 50%
CPUQuota=50%
```

## 📈 Monitoring et Maintenance

### Cron job pour nettoyage

Créer un cron pour nettoyer les vieux résultats :

```bash
crontab -e
```

Ajouter :
```bash
# Nettoyer résultats de plus de 30 jours à 3h du matin
0 3 * * * find /home/user/scrapeur-site-web/results -name "*.json" -mtime +30 -delete
0 3 * * * find /home/user/scrapeur-site-web/queue/completed -name "*.json" -mtime +30 -delete
```

### Rotation des logs

Créer `/etc/logrotate.d/scraper` :

```
/home/user/scrapeur-site-web/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

## 🔄 Mise à jour du code

```bash
cd /home/user/scrapeur-site-web
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart scraper-worker
```

## ⚡ Optimisation VPS

### Pour VPS avec peu de RAM (1 GB)

Modifier `config.py` :
```python
MAX_CONCURRENT_SITES = 5  # Réduire de 10 à 5
```

### Pour VPS puissant (4+ GB RAM)

```python
MAX_CONCURRENT_SITES = 15  # Augmenter à 15
```

## 📊 Estimation des Ressources

**VPS Recommandé :**
- **CPU** : 1-2 vCores
- **RAM** : 2 GB minimum
- **Disque** : 20 GB
- **Bande passante** : Illimitée recommandée

**Consommation :**
- CPU : 20-40% pendant scraping
- RAM : 300-800 MB
- Bande passante : ~10-50 MB par 100 sites

## 🐛 Dépannage VPS

### Worker ne démarre pas

```bash
# Vérifier les logs
sudo journalctl -u scraper-worker -n 50

# Tester manuellement
cd /home/user/scrapeur-site-web
source venv/bin/activate
python worker.py
```

### Permissions refusées

```bash
# Donner les bonnes permissions
sudo chown -R votre-user:votre-user /home/user/scrapeur-site-web
chmod -R 755 /home/user/scrapeur-site-web
```

### Python introuvable

```bash
# Vérifier Python
which python3
python3 --version

# Recréer venv si besoin
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📞 Support

En cas de problème :
1. Vérifier les logs : `tail -f logs/worker.log`
2. Vérifier le service : `sudo systemctl status scraper-worker`
3. Tester manuellement : `python worker.py`

