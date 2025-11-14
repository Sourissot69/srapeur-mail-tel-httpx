# -*- coding: utf-8 -*-
"""
Script pour convertir un CSV Google Maps en JSON pour le scraper
"""

import csv
import json
import sys
import uuid

def convert_csv_to_json(csv_file, output_file=None):
    """
    Convertit un CSV Google Maps en JSON
    
    Args:
        csv_file: Fichier CSV d'entrée
        output_file: Fichier JSON de sortie (optionnel)
    """
    if output_file is None:
        output_file = csv_file.replace('.csv', '.json')
    
    sites = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                website = row.get('Site Web', '').strip()
                
                # Ne garder que les sites avec URL valide
                if website and website.startswith('http'):
                    # Générer un ID unique si pas présent
                    site_id = str(uuid.uuid4())
                    
                    sites.append({
                        'id': site_id,
                        'website': website
                    })
        
        # Sauvegarder en JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sites, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*80}")
        print(f"CONVERSION TERMINEE")
        print(f"{'='*80}")
        print(f"Fichier CSV: {csv_file}")
        print(f"Fichier JSON: {output_file}")
        print(f"Sites extraits: {len(sites)}")
        print(f"{'='*80}\n")
        
        # Afficher quelques exemples
        print("Exemples (5 premiers) :")
        for i, site in enumerate(sites[:5], 1):
            print(f"{i}. ID: {site['id']}")
            print(f"   URL: {site['website']}\n")
        
        if len(sites) > 5:
            print(f"... et {len(sites) - 5} autres sites")
        
        print(f"\nPour lancer le scraping :")
        print(f"  python add_job.py {output_file} --priority 1\n")
        
        return sites
    
    except Exception as e:
        print(f"Erreur: {e}")
        return []


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python convert_csv_to_json.py fichier.csv [output.json]")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    convert_csv_to_json(csv_file, output_file)

