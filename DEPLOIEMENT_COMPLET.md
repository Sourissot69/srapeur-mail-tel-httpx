# 🚀 Guide de Déploiement Complet - GitHub + VPS Hostinger

## 📦 PARTIE 1 : PUBLICATION SUR GITHUB

### Étape 1 : Préparation locale

```bash
# Nettoyer les fichiers sensibles
rm -f *.log
rm -f queue/pending/*.json
rm -f queue/processing/*.json
rm -f queue/completed/*.json

# Vérifier ce qui sera commité
git status
```

### Étape 2 : Premier commit

```bash
# Ajouter tous les fichiers
git add .

# Commit initial
git commit -m "Initial commit - Scraper emails et réseaux sociaux avec système de queue"

# Pousser vers GitHub
git branch -M main
git push -u origin main
```

**✅ Repository GitHub :** https://github.com/Sourissot69/srapeur-mail-tel-httpx

---

## 🌐 PARTIE 2 : DÉPLOIEMENT SUR VPS HOSTINGER

### Prérequis VPS

- VPS Ubuntu 20.04+ ou Debian 11+
- 2 GB RAM minimum
- Accès SSH root
- **Port 8014 disponible** (pour l'API)

### Méthode 1 : Déploiement Automatique

```bash
# 1. Modifier deploy.sh avec votre IP VPS
nano deploy.sh
# Changer : VPS_IP="VOTRE_IP_VPS"

# 2. Lancer le déploiement
bash deploy.sh
```

### Méthode 2 : Déploiement Manuel

```bash
# 1. SSH au VPS
ssh root@VOTRE_IP_VPS

# 2. Cloner le repository
cd /opt
git clone https://github.com/Sourissot69/srapeur-mail-tel-httpx.git
cd srapeur-mail-tel-httpx

# 3. Installation
bash install_vps.sh

# 4. Installer les services systemd
sudo bash install_service.sh

# 5. Démarrer les services
sudo systemctl start scraper-worker
sudo systemctl start scraper-api

# 6. Activer au démarrage
sudo systemctl enable scraper-worker
sudo systemctl enable scraper-api

# 7. Vérifier que tout fonctionne
sudo systemctl status scraper-worker
sudo systemctl status scraper-api
```

### Vérification Installation

```bash
# Test API (doit retourner status: ok)
curl http://VOTRE_IP_VPS:8014/health

# Test worker
python monitor.py

# Logs
tail -f logs/worker.log
tail -f logs/api.log
```

---

## 🔧 CONFIGURATION DU FIREWALL

```bash
# Autoriser SSH
sudo ufw allow 22/tcp

# Autoriser l'API sur port 8014
sudo ufw allow 8014/tcp

# Activer le firewall
sudo ufw enable

# Vérifier
sudo ufw status
```

**Résultat attendu :**
```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
8014/tcp                   ALLOW       Anywhere
```

---

## 📊 UTILISATION POST-DÉPLOIEMENT

### Via API Web (Port 8014)

```bash
# Upload CSV et créer job
curl -X POST http://VOTRE_IP_VPS:8014/job/upload-and-start \
  -F "file=@mon_fichier.csv" \
  -F "priority=1" \
  -F "user=VotreNom"

# Vérifier l'état
curl http://VOTRE_IP_VPS:8014/queue

# Lister les résultats
curl http://VOTRE_IP_VPS:8014/results

# Télécharger un résultat
curl http://VOTRE_IP_VPS:8014/results/scraping_FILENAME.json --output resultat.json
```

### Via SSH Direct

```bash
# 1. Copier CSV sur VPS
scp mon_fichier.csv root@VOTRE_IP:/opt/srapeur-mail-tel-httpx/

# 2. SSH au VPS
ssh root@VOTRE_IP

# 3. Ajouter job
cd /opt/srapeur-mail-tel-httpx
source venv/bin/activate
python add_job.py mon_fichier.csv --priority 1

# 4. Monitoring
python monitor.py

# 5. Récupérer résultats (depuis PC local)
scp root@VOTRE_IP:/opt/srapeur-mail-tel-httpx/results/*.json ./
```

---

## 🔄 MISE À JOUR DU CODE

### Sur GitHub

```bash
# Modifications locales
git add .
git commit -m "Description des changements"
git push
```

### Sur VPS

```bash
ssh root@VOTRE_IP_VPS
cd /opt/srapeur-mail-tel-httpx
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart scraper-worker
sudo systemctl restart scraper-api
```

---

## 🔍 MONITORING ET LOGS

### Vérifier les services

```bash
# Status worker
sudo systemctl status scraper-worker

# Status API
sudo systemctl status scraper-api
```

### Consulter les logs

```bash
# Logs worker en temps réel
tail -f logs/worker.log

# Logs API en temps réel
tail -f logs/api.log

# Logs système
sudo journalctl -u scraper-worker -f
sudo journalctl -u scraper-api -f
```

### Monitoring de la queue

```bash
# État actuel
python monitor.py

# Refresh automatique toutes les 5s
watch -n 5 python monitor.py
```

---

## 🔒 SÉCURITÉ VPS

### Recommandations

1. **Changer le mot de passe root**
```bash
passwd
```

2. **Créer un utilisateur dédié**
```bash
adduser scraper
usermod -aG sudo scraper
# Puis utiliser cet utilisateur au lieu de root
```

3. **Désactiver connexion root par mot de passe**
```bash
nano /etc/ssh/sshd_config
# Modifier : PermitRootLogin no
# Modifier : PasswordAuthentication no
sudo systemctl restart sshd
```

4. **Installer fail2ban**
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
```

---

## 🎯 CHECKLIST POST-INSTALLATION

- [ ] Worker démarre : `sudo systemctl status scraper-worker`
- [ ] API démarre : `sudo systemctl status scraper-api`
- [ ] Port 8014 ouvert : `sudo ufw status`
- [ ] API répond : `curl http://VOTRE_IP:8014/health`
- [ ] Test upload CSV via API
- [ ] Test ajout job via SSH
- [ ] Logs accessibles
- [ ] Résultats générés correctement
- [ ] Services auto-start au reboot

---

## 📞 URLS ET ACCÈS

- **GitHub** : https://github.com/Sourissot69/srapeur-mail-tel-httpx
- **API VPS** : http://VOTRE_IP_VPS:8014
- **SSH** : ssh root@VOTRE_IP_VPS
- **Logs** : /opt/srapeur-mail-tel-httpx/logs/

---

## 🐛 Dépannage

### Worker ne démarre pas
```bash
sudo journalctl -u scraper-worker -n 50
```

### API ne répond pas sur port 8014
```bash
# Vérifier que le port est ouvert
sudo ufw status
sudo netstat -tulpn | grep 8014

# Vérifier les logs
tail -f logs/api_error.log
```

### Permissions refusées
```bash
sudo chown -R $USER:$USER /opt/srapeur-mail-tel-httpx
```

---

## ✅ PROJET PRÊT !

- ✅ Code sur GitHub
- ✅ VPS Hostinger configuré
- ✅ Worker tourne 24/7
- ✅ API accessible sur port 8014
- ✅ Système de queue opérationnel
- ✅ Multi-utilisateurs

**Bon scraping ! 🎉**

