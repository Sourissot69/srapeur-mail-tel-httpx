#!/bin/bash
# Script d'installation sur VPS Hostinger
# Usage: bash install_vps.sh

echo "========================================"
echo "Installation du Scraper sur VPS"
echo "========================================"

# Mise à jour du système
echo "Mise à jour du système..."
sudo apt update
sudo apt upgrade -y

# Installation de Python 3 et pip
echo "Installation de Python 3..."
sudo apt install -y python3 python3-pip python3-venv

# Création de l'environnement virtuel
echo "Création de l'environnement virtuel..."
python3 -m venv venv

# Activation de l'environnement virtuel
source venv/bin/activate

# Installation des dépendances
echo "Installation des dépendances Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Création des dossiers nécessaires
echo "Création des dossiers..."
mkdir -p queue/pending
mkdir -p queue/processing
mkdir -p queue/completed
mkdir -p results
mkdir -p logs

# Copier le fichier .env
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Fichier .env créé. Modifiez-le si nécessaire."
fi

# Permissions
chmod +x worker.py
chmod +x add_job.py
chmod +x monitor.py
chmod +x api_server.py

# Créer dossier uploads pour l'API
mkdir -p uploads

# Créer dossier logs
mkdir -p logs

# Configurer le firewall (port 8014 pour l'API)
echo "Configuration du firewall..."
if command -v ufw &> /dev/null; then
    sudo ufw allow 8014/tcp
    echo "Port 8014 ouvert pour l'API"
fi

echo ""
echo "========================================"
echo "Installation terminée !"
echo "========================================"
echo ""
echo "Prochaines étapes :"
echo "1. Modifier .env si nécessaire"
echo "2. Installer les services : sudo bash install_service.sh"
echo "3. Démarrer le worker : sudo systemctl start scraper-worker"
echo "4. (Optionnel) Démarrer l'API : sudo systemctl start scraper-api"
echo ""
echo "Port 8014 : API Web (accessible via http://VOTRE_IP:8014)"
echo ""

