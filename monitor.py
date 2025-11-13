# -*- coding: utf-8 -*-
"""
Script pour monitorer l'état de la queue
Usage: python monitor.py
"""

import json
import os
from datetime import datetime
from pathlib import Path


def count_jobs(directory):
    """Compte les jobs dans un dossier"""
    if not os.path.exists(directory):
        return 0
    return len([f for f in os.listdir(directory) if f.endswith('.json')])


def get_jobs(directory):
    """Récupère tous les jobs d'un dossier"""
    jobs = []
    if not os.path.exists(directory):
        return jobs
    
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            try:
                with open(os.path.join(directory, filename), 'r', encoding='utf-8') as f:
                    job = json.load(f)
                    jobs.append(job)
            except Exception:
                pass
    
    return jobs


def format_duration(start, end):
    """Formate la durée entre deux dates ISO"""
    try:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
        duration = (end_dt - start_dt).total_seconds()
        
        if duration < 60:
            return f"{duration:.0f}s"
        else:
            minutes = duration / 60
            return f"{minutes:.1f}min"
    except:
        return "N/A"


def monitor_queue():
    """Affiche l'état de la queue"""
    
    # Compter les jobs
    pending_count = count_jobs('queue/pending')
    processing_count = count_jobs('queue/processing')
    completed_count = count_jobs('queue/completed')
    
    # Récupérer les détails
    pending_jobs = get_jobs('queue/pending')
    processing_jobs = get_jobs('queue/processing')
    completed_jobs = get_jobs('queue/completed')
    
    # Trier par priorité et date
    pending_jobs.sort(key=lambda j: (j.get('priority', 5), j.get('created_at', '')))
    completed_jobs.sort(key=lambda j: j.get('completed_at', ''), reverse=True)
    
    print(f"\n{'='*80}")
    print(f"ETAT DE LA QUEUE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    print(f"En attente:       {pending_count}")
    print(f"En traitement:    {processing_count}")
    print(f"Termines:         {completed_count}")
    print(f"{'='*80}\n")
    
    # Jobs en traitement
    if processing_jobs:
        print(f"{'='*80}")
        print(f"JOB EN COURS")
        print(f"{'='*80}")
        for job in processing_jobs:
            csv_name = Path(job['csv_file']).name
            started = datetime.fromisoformat(job['started_at'])
            duration = (datetime.now() - started).total_seconds()
            print(f"ID: {job['id']}")
            print(f"Fichier: {csv_name}")
            print(f"User: {job['user']}")
            print(f"Demarre: {job['started_at']}")
            print(f"Duree: {duration:.0f}s")
        print(f"{'='*80}\n")
    
    # Jobs en attente
    if pending_jobs:
        print(f"{'='*80}")
        print(f"JOBS EN ATTENTE ({len(pending_jobs)})")
        print(f"{'='*80}")
        for i, job in enumerate(pending_jobs[:10], 1):
            csv_name = Path(job['csv_file']).name
            print(f"{i}. [{job['priority']}] {csv_name} - User: {job['user']}")
        
        if len(pending_jobs) > 10:
            print(f"... et {len(pending_jobs) - 10} autres")
        print(f"{'='*80}\n")
    
    # Jobs complétés (derniers 5)
    if completed_jobs:
        print(f"{'='*80}")
        print(f"DERNIERS JOBS TERMINES (5 derniers)")
        print(f"{'='*80}")
        
        recent_completed = [j for j in completed_jobs if j.get('status') == 'completed'][:5]
        recent_errors = [j for j in completed_jobs if j.get('status') == 'error'][:5]
        
        if recent_completed:
            print("SUCCES:")
            for job in recent_completed:
                csv_name = Path(job['csv_file']).name
                duration = format_duration(job['started_at'], job['completed_at'])
                stats = job.get('stats', {})
                print(f"  - {csv_name}")
                print(f"    Duree: {duration}")
                print(f"    Emails: {stats.get('total_emails', 0)}, Reseaux sociaux: {stats.get('total_social', 0)}")
                print(f"    Resultat: {Path(job['result_file']).name if job.get('result_file') else 'N/A'}")
        
        if recent_errors:
            print("\nERREURS:")
            for job in recent_errors:
                csv_name = Path(job['csv_file']).name
                print(f"  - {csv_name}")
                print(f"    Erreur: {job.get('error', 'Unknown')}")
        
        print(f"{'='*80}\n")
    
    if not pending_jobs and not processing_jobs:
        print("Queue vide. Ajoutez un job avec: python add_job.py fichier.csv\n")


if __name__ == '__main__':
    monitor_queue()

