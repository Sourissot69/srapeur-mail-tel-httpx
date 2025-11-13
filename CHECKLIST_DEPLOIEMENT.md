# ✅ Checklist de Déploiement

## 🔧 PRÉPARATION LOCALE

- [ ] Installer les dépendances : `pip install -r requirements.txt`
- [ ] Tester le scraper localement : `python run_scraper.py example.csv`
- [ ] Tester le système de queue :
  - [ ] Démarrer worker : `python worker.py`
  - [ ] Ajouter job : `python add_job.py example.csv`
  - [ ] Vérifier monitoring : `python monitor.py`
- [ ] Nettoyer les fichiers sensibles :
  - [ ] Supprimer `results/*.json` (sauf .gitkeep)
  - [ ] Supprimer `queue/**/*.json`
  - [ ] Supprimer `*.log`
  - [ ] Supprimer vos CSV de données

## 📤 GITHUB

- [ ] Créer repository sur GitHub
- [ ] Modifier README.md avec votre description
- [ ] Vérifier .gitignore
- [ ] Initialiser Git : `git init`
- [ ] Premier commit : `git add . && git commit -m "Initial commit"`
- [ ] Ajouter remote : `git remote add origin https://github.com/username/repo.git`
- [ ] Push : `git push -u origin main`
- [ ] Ajouter topics/tags sur GitHub
- [ ] Créer release v1.0.0

## 🌐 VPS HOSTINGER

### Prérequis VPS
- [ ] VPS commandé et actif
- [ ] Ubuntu 20.04+ ou Debian 11+
- [ ] Au moins 2 GB RAM
- [ ] Accès SSH root/sudo
- [ ] Note de l'IP du VPS : `___________________`

### Installation
- [ ] Modifier `deploy.sh` avec l'IP VPS
- [ ] SSH au VPS fonctionne : `ssh root@IP`
- [ ] Option A - Déploiement automatique :
  - [ ] `bash deploy.sh`
- [ ] Option B - Déploiement manuel :
  - [ ] SSH au VPS
  - [ ] `git clone https://github.com/username/repo.git`
  - [ ] `cd repo`
  - [ ] `bash install_vps.sh`
  - [ ] `sudo bash install_service.sh`
  - [ ] `sudo systemctl start scraper-worker`
  - [ ] `sudo systemctl enable scraper-worker`

### Vérification VPS
- [ ] Service actif : `sudo systemctl status scraper-worker`
- [ ] Logs OK : `tail -f logs/worker.log`
- [ ] Ajouter un job test
- [ ] Vérifier résultat généré
- [ ] Récupérer résultat sur PC local

## 🔒 SÉCURITÉ

- [ ] Firewall configuré : `sudo ufw enable`
- [ ] SSH seulement par clé (désactiver password)
- [ ] Créer utilisateur dédié (pas root)
- [ ] Limiter ressources du service (CPU/RAM)
- [ ] Configurer rotation logs
- [ ] Backup automatique des résultats

## 📊 TESTS POST-DÉPLOIEMENT

- [ ] Test 1 : Ajouter job priorité haute
- [ ] Test 2 : Ajouter 3 jobs simultanés
- [ ] Test 3 : Vérifier ordre de traitement (priorité)
- [ ] Test 4 : Crash test (arrêter worker pendant job)
- [ ] Test 5 : Récupération résultats
- [ ] Test 6 : Monitoring en temps réel
- [ ] Test 7 : Charge CPU/RAM acceptable
- [ ] Test 8 : Logs propres et lisibles

## 📝 DOCUMENTATION

- [ ] README.md clair et complet
- [ ] GUIDE_UTILISATION.txt accessible
- [ ] DEPLOIEMENT_VPS.md testé
- [ ] COMMANDES_RAPIDES.txt utile
- [ ] License ajoutée

## 🎯 MISE EN PRODUCTION

- [ ] URL GitHub partagée avec l'équipe
- [ ] IP VPS communiquée
- [ ] Credentials SSH distribués (de manière sécurisée)
- [ ] Formation utilisateurs (add_job.py, monitor.py)
- [ ] Process de récupération résultats documenté
- [ ] Support/contact défini

## 🔄 MAINTENANCE

- [ ] Plan de backup (hebdomadaire)
- [ ] Monitoring (Uptime, CPU, RAM)
- [ ] Process de mise à jour code
- [ ] Rotation des logs configurée
- [ ] Nettoyage vieux résultats (cron)

================================================================================
✅ TOUT EST PRÊT QUAND TOUTES LES CASES SONT COCHÉES !
================================================================================

