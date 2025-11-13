# -*- coding: utf-8 -*-
"""
Worker qui traite les jobs de scraping
Usage: python worker.py
"""

import asyncio
import json
import os
import time
import csv
from datetime import datetime
from pathlib import Path
from scraper import WebScraper


class JobWorker:
    """Worker qui traite les jobs de la queue"""
    
    def __init__(self):
        self.running = True
        self.current_job = None
        
    def get_next_job(self):
        """Récupère le prochain job de la queue (par priorité puis date)"""
        pending_dir = 'queue/pending'
        
        if not os.path.exists(pending_dir):
            return None
        
        # Lister tous les jobs pending
        job_files = [f for f in os.listdir(pending_dir) if f.endswith('.json')]
        
        if not job_files:
            return None
        
        # Charger et trier par priorité puis date
        jobs = []
        for job_file in job_files:
            try:
                with open(os.path.join(pending_dir, job_file), 'r', encoding='utf-8') as f:
                    job = json.load(f)
                    job['_filename'] = job_file
                    jobs.append(job)
            except Exception as e:
                print(f"Erreur lecture job {job_file}: {e}")
        
        if not jobs:
            return None
        
        # Trier : priorité (1 = haute) puis date (ancien = prioritaire)
        jobs.sort(key=lambda j: (j.get('priority', 5), j.get('created_at', '')))
        
        return jobs[0]
    
    def move_job(self, job, from_dir, to_dir):
        """Déplace un job d'un dossier à un autre"""
        try:
            os.makedirs(to_dir, exist_ok=True)
            
            src = os.path.join(from_dir, job['_filename'])
            dst = os.path.join(to_dir, job['_filename'])
            
            # Mettre à jour le job
            with open(dst, 'w', encoding='utf-8') as f:
                json.dump(job, f, ensure_ascii=False, indent=2)
            
            # Supprimer l'ancien
            if os.path.exists(src):
                os.remove(src)
            
            return True
        except Exception as e:
            print(f"Erreur deplacement job: {e}")
            return False
    
    async def process_job(self, job):
        """Traite un job de scraping"""
        job_id = job['id']
        csv_file = job['csv_file']
        
        print(f"\n{'='*80}")
        print(f"TRAITEMENT DU JOB {job_id}")
        print(f"{'='*80}")
        print(f"Fichier: {csv_file}")
        print(f"User: {job['user']}")
        print(f"Priorite: {job['priority']}")
        print(f"{'='*80}\n")
        
        # Marquer comme en traitement
        job['status'] = 'processing'
        job['started_at'] = datetime.now().isoformat()
        self.move_job(job, 'queue/pending', 'queue/processing')
        self.current_job = job
        
        try:
            # Extraire les sites du CSV
            sites = []
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    website = row.get('Site Web', '').strip()
                    if website and website.startswith('http'):
                        sites.append({
                            'url': website,
                            'name': row.get('Nom', 'Unknown').strip(),
                            'category': row.get('Type', 'Unknown').strip(),
                            'phone': row.get('Téléphone Principal', '').strip(),
                            'city': row.get('Ville', '').strip(),
                            'rating': row.get('Note', '').strip(),
                        })
            
            if not sites:
                raise Exception("Aucun site avec URL trouvé dans le CSV")
            
            print(f"Scraping de {len(sites)} sites...\n")
            
            # Créer et lancer le scraper
            scraper = WebScraper()
            results = await scraper.scrape_multiple_sites(sites)
            
            # Créer la version simplifiée
            simplified_results = []
            
            for idx, result in enumerate(results, 1):
                emails_list = [email_data['email'] for email_data in result['emails']]
                
                social_list = {}
                for platform, urls in result['social_media'].items():
                    social_list[platform] = urls
                
                simplified = {
                    "id": idx,
                    "url": result['url'],
                    "nom": result['name'],
                    "nb_emails": len(emails_list),
                    "emails": emails_list,
                    "nb_reseaux_sociaux": sum(len(urls) for urls in result['social_media'].values()),
                    "reseaux_sociaux": social_list
                }
                
                simplified_results.append(simplified)
            
            # Sauvegarder le résultat
            os.makedirs('results', exist_ok=True)
            csv_name = Path(csv_file).stem
            output_file = f'results/scraping_{csv_name}_{job_id}.json'
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(simplified_results, f, ensure_ascii=False, indent=2)
            
            # Statistiques
            total_emails = sum(s['nb_emails'] for s in simplified_results)
            total_social = sum(s['nb_reseaux_sociaux'] for s in simplified_results)
            sites_with_emails = sum(1 for s in simplified_results if s['nb_emails'] > 0)
            sites_with_social = sum(1 for s in simplified_results if s['nb_reseaux_sociaux'] > 0)
            
            print(f"\n{'='*80}")
            print(f"JOB {job_id} TERMINE")
            print(f"{'='*80}")
            print(f"Total sites: {len(simplified_results)}")
            print(f"Sites avec emails: {sites_with_emails}/{len(simplified_results)}")
            print(f"Sites avec reseaux sociaux: {sites_with_social}/{len(simplified_results)}")
            print(f"Total emails: {total_emails}")
            print(f"Total reseaux sociaux: {total_social}")
            print(f"Resultat: {output_file}")
            print(f"{'='*80}\n")
            
            # Marquer comme complété
            job['status'] = 'completed'
            job['completed_at'] = datetime.now().isoformat()
            job['result_file'] = output_file
            job['stats'] = {
                'total_sites': len(simplified_results),
                'total_emails': total_emails,
                'total_social': total_social,
                'sites_with_emails': sites_with_emails,
                'sites_with_social': sites_with_social
            }
            
            self.move_job(job, 'queue/processing', 'queue/completed')
            
        except Exception as e:
            print(f"\n{'='*80}")
            print(f"ERREUR LORS DU TRAITEMENT DU JOB {job_id}")
            print(f"{'='*80}")
            print(f"Erreur: {e}")
            print(f"{'='*80}\n")
            
            # Marquer comme erreur
            job['status'] = 'error'
            job['completed_at'] = datetime.now().isoformat()
            job['error'] = str(e)
            
            self.move_job(job, 'queue/processing', 'queue/completed')
        
        finally:
            self.current_job = None
    
    async def run(self):
        """Boucle principale du worker"""
        print(f"\n{'#'*80}")
        print(f"WORKER DEMARRE")
        print(f"{'#'*80}")
        print(f"En attente de jobs dans queue/pending/")
        print(f"Appuyez sur Ctrl+C pour arreter")
        print(f"{'#'*80}\n")
        
        try:
            while self.running:
                # Chercher un job
                job = self.get_next_job()
                
                if job:
                    await self.process_job(job)
                else:
                    # Pas de job, attendre 5 secondes
                    print("Aucun job en attente... (verification toutes les 5s)")
                    await asyncio.sleep(5)
        
        except KeyboardInterrupt:
            print("\n\nArret du worker...")
            if self.current_job:
                print("ATTENTION: Un job etait en cours!")
                print(f"Job ID: {self.current_job['id']}")
                # Remettre dans pending
                self.move_job(self.current_job, 'queue/processing', 'queue/pending')
                print("Job remis dans la queue pending")
        
        print("\nWorker arrete.\n")


if __name__ == '__main__':
    worker = JobWorker()
    asyncio.run(worker.run())

