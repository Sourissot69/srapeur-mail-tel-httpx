# -*- coding: utf-8 -*-
"""
Script principal pour scraper des sites depuis un fichier CSV Google Maps
Usage: python run_scraper.py nom_du_fichier.csv
"""

import asyncio
import json
import csv
import os
import sys
from scraper import WebScraper
from datetime import datetime


async def scrape_from_csv(csv_file: str):
    """
    Scrape tous les sites d'un fichier CSV
    
    Args:
        csv_file: Chemin vers le fichier CSV
    """
    # Extraire les sites du CSV
    sites = []
    
    print(f"\nExtraction des sites depuis {csv_file}...\n")
    
    try:
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
    except FileNotFoundError:
        print(f"Erreur: Fichier {csv_file} introuvable")
        return
    except Exception as e:
        print(f"Erreur lors de la lecture du CSV: {e}")
        return
    
    if not sites:
        print("Aucun site avec URL trouvé dans le CSV")
        return
    
    print(f"{'='*80}")
    print(f"SCRAPING DE {len(sites)} SITES")
    print(f"{'='*80}")
    print(f"Temps estime: ~{len(sites) * 2.5 / 60:.1f} minutes")
    print(f"{'='*80}\n")
    
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
    
    # Sauvegarder le JSON simplifié
    os.makedirs('results', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_name = os.path.splitext(os.path.basename(csv_file))[0]
    output_file = f'results/scraping_{csv_name}_{timestamp}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(simplified_results, f, ensure_ascii=False, indent=2)
    
    # Stats
    total_emails = sum(s['nb_emails'] for s in simplified_results)
    total_social = sum(s['nb_reseaux_sociaux'] for s in simplified_results)
    sites_with_emails = sum(1 for s in simplified_results if s['nb_emails'] > 0)
    sites_with_social = sum(1 for s in simplified_results if s['nb_reseaux_sociaux'] > 0)
    
    print(f"\n{'='*80}")
    print(f"STATISTIQUES FINALES")
    print(f"{'='*80}")
    print(f"Total sites: {len(simplified_results)}")
    print(f"Sites avec emails: {sites_with_emails}/{len(simplified_results)} ({sites_with_emails/len(simplified_results)*100:.1f}%)")
    print(f"Sites avec reseaux sociaux: {sites_with_social}/{len(simplified_results)} ({sites_with_social/len(simplified_results)*100:.1f}%)")
    print(f"Total emails: {total_emails}")
    print(f"Total reseaux sociaux: {total_social}")
    print(f"\nFichier sauvegarde: {output_file}")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("\nUsage: python run_scraper.py nom_du_fichier.csv")
        print("\nExemple: python run_scraper.py google-maps-avocats.csv\n")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    asyncio.run(scrape_from_csv(csv_file))

