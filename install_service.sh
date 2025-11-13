#!/bin/bash
# Installation du service systemd pour le worker
# Usage: sudo bash install_service.sh

echo "Installation du service systemd..."

# Obtenir le chemin absolu du projet
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
USER=$(whoami)

# Créer le fichier service
cat > /tmp/scraper-worker.service << EOF
[Unit]
Description=Scraper Worker - Queue Job Processor
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/worker.py
Restart=always
RestartSec=10
StandardOutput=append:$PROJECT_DIR/logs/worker.log
StandardError=append:$PROJECT_DIR/logs/worker_error.log

[Install]
WantedBy=multi-user.target
EOF

# Copier le fichier service
sudo cp /tmp/scraper-worker.service /etc/systemd/system/

# Recharger systemd
sudo systemctl daemon-reload

# Créer le fichier service pour l'API (port 8014)
cat > /tmp/scraper-api.service << EOF
[Unit]
Description=Scraper API Web - Port 8014
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/api_server.py
Restart=always
RestartSec=10
StandardOutput=append:$PROJECT_DIR/logs/api.log
StandardError=append:$PROJECT_DIR/logs/api_error.log

[Install]
WantedBy=multi-user.target
EOF

# Copier le fichier service API
sudo cp /tmp/scraper-api.service /etc/systemd/system/

# Recharger systemd
sudo systemctl daemon-reload

echo ""
echo "========================================"
echo "Services installés !"
echo "========================================"
echo ""
echo "WORKER (traitement jobs) :"
echo "  Démarrer    : sudo systemctl start scraper-worker"
echo "  Arrêter     : sudo systemctl stop scraper-worker"
echo "  Status      : sudo systemctl status scraper-worker"
echo "  Auto-start  : sudo systemctl enable scraper-worker"
echo "  Logs        : tail -f logs/worker.log"
echo ""
echo "API WEB (port 8014) :"
echo "  Démarrer    : sudo systemctl start scraper-api"
echo "  Arrêter     : sudo systemctl stop scraper-api"
echo "  Status      : sudo systemctl status scraper-api"
echo "  Auto-start  : sudo systemctl enable scraper-api"
echo "  Logs        : tail -f logs/api.log"
echo ""
echo "Accès API : http://VOTRE_IP:8014"
echo ""

