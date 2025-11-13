# -*- coding: utf-8 -*-
"""
Script pour ajouter un job de scraping à la queue
Usage: python add_job.py fichier.csv [--priority 1-10]
"""

import json
import os
import sys
from datetime import datetime
import argparse


def add_job(csv_file: str, priority: int = 5, user: str = "default"):
    """
    Ajoute un job à la queue
    
    Args:
        csv_file: Chemin vers le fichier CSV
        priority: Priorité (1=haute, 10=basse)
        user: Nom de l'utilisateur
    """
    # Vérifier que le fichier existe
    if not os.path.exists(csv_file):
        print(f"Erreur: Fichier {csv_file} introuvable")
        return False
    
    # Créer l'ID du job (timestamp)
    job_id = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    
    # Créer le job
    job = {
        "id": job_id,
        "user": user,
        "csv_file": os.path.abspath(csv_file),
        "status": "pending",
        "priority": priority,
        "created_at": datetime.now().isoformat(),
        "started_at": None,
        "completed_at": None,
        "result_file": None,
        "error": None
    }
    
    # Sauvegarder dans queue/pending
    os.makedirs('queue/pending', exist_ok=True)
    job_file = f'queue/pending/job_{job_id}.json'
    
    with open(job_file, 'w', encoding='utf-8') as f:
        json.dump(job, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*80}")
    print(f"JOB AJOUTE A LA QUEUE")
    print(f"{'='*80}")
    print(f"ID: {job_id}")
    print(f"Fichier: {csv_file}")
    print(f"Priorite: {priority}")
    print(f"User: {user}")
    print(f"{'='*80}")
    print(f"\nLe worker traitera ce job automatiquement.")
    print(f"Verifiez l'etat avec: python monitor.py")
    print(f"{'='*80}\n")
    
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ajouter un job de scraping à la queue')
    parser.add_argument('csv_file', help='Fichier CSV à scraper')
    parser.add_argument('--priority', type=int, default=5, choices=range(1, 11),
                        help='Priorité du job (1=haute, 10=basse), défaut=5')
    parser.add_argument('--user', default='default', help='Nom de l\'utilisateur')
    
    args = parser.parse_args()
    
    add_job(args.csv_file, args.priority, args.user)

