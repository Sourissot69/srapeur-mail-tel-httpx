#!/bin/bash
# Script de déploiement rapide sur VPS Hostinger
# Usage: bash deploy.sh

set -e  # Arrêter en cas d'erreur

echo "========================================"
echo "DEPLOIEMENT SUR VPS HOSTINGER"
echo "========================================"

# Variables (à modifier selon votre VPS)
VPS_USER="root"
VPS_IP="VOTRE_IP_VPS"  # À MODIFIER
PROJECT_NAME="scrapeur-site-web"
INSTALL_DIR="/opt/$PROJECT_NAME"

echo ""
echo "Configuration :"
echo "  VPS: $VPS_USER@$VPS_IP"
echo "  Dossier: $INSTALL_DIR"
echo ""

read -p "Les informations sont-elles correctes ? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Modifiez les variables dans deploy.sh"
    exit 1
fi

echo ""
echo "1. Connexion au VPS et création du dossier..."
ssh $VPS_USER@$VPS_IP "mkdir -p $INSTALL_DIR"

echo "2. Copie des fichiers..."
scp -r ./* $VPS_USER@$VPS_IP:$INSTALL_DIR/

echo "3. Installation sur le VPS..."
ssh $VPS_USER@$VPS_IP << 'EOF'
cd /opt/scrapeur-site-web
bash install_vps.sh
EOF

echo "4. Installation du service systemd..."
ssh $VPS_USER@$VPS_IP "cd $INSTALL_DIR && sudo bash install_service.sh"

echo "5. Démarrage du worker..."
ssh $VPS_USER@$VPS_IP "sudo systemctl start scraper-worker && sudo systemctl enable scraper-worker"

echo ""
echo "========================================"
echo "DEPLOIEMENT TERMINE !"
echo "========================================"
echo ""
echo "Pour ajouter un job :"
echo "  1. Copier votre CSV : scp mon_fichier.csv $VPS_USER@$VPS_IP:$INSTALL_DIR/"
echo "  2. SSH au VPS : ssh $VPS_USER@$VPS_IP"
echo "  3. cd $INSTALL_DIR && source venv/bin/activate"
echo "  4. python add_job.py mon_fichier.csv"
echo ""
echo "Pour consulter l'état :"
echo "  ssh $VPS_USER@$VPS_IP 'cd $INSTALL_DIR && source venv/bin/activate && python monitor.py'"
echo ""
echo "Pour récupérer les résultats :"
echo "  scp $VPS_USER@$VPS_IP:$INSTALL_DIR/results/*.json ./results/"
echo ""

