# -*- coding: utf-8 -*-
"""
Convertit CSV en JSON complet (toutes les données) + JSON simple (URLs seulement)
"""
import csv
import json
import uuid

csv_file = 'google-maps-ae6ab7ba-5af8-4b9e-8273-d6638e8a9f84.csv'

# 1. JSON COMPLET avec toutes les données du CSV
full_data = []
sites_only = []

with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        website = row.get('Site Web', '').strip()
        
        if website and website.startswith('http'):
            site_id = str(uuid.uuid4())
            
            # JSON complet
            full_data.append({
                'id': site_id,
                'nom': row.get('Nom', ''),
                'website': website,
                'email_google': row.get('Email Principal', ''),
                'tous_emails_google': row.get('Tous les Emails', ''),
                'reseaux_sociaux_google': row.get('Réseaux Sociaux', ''),
                'telephone': row.get('Téléphone Principal', ''),
                'ville': row.get('Ville', ''),
            })
            
            # JSON simple (URLs seulement)
            sites_only.append({
                'id': site_id,
                'website': website
            })

# Sauvegarder JSON complet
with open('amiens_formations_complet.json', 'w', encoding='utf-8') as f:
    json.dump(full_data, f, ensure_ascii=False, indent=2)

# Sauvegarder JSON simple
with open('amiens_formations_urls.json', 'w', encoding='utf-8') as f:
    json.dump(sites_only, f, ensure_ascii=False, indent=2)

print(f"\n{'='*80}")
print(f"CONVERSION TERMINEE")
print(f"{'='*80}")
print(f"Sites extraits: {len(sites_only)}")
print(f"\nFichiers créés:")
print(f"  1. amiens_formations_complet.json - Toutes les données Google Maps")
print(f"  2. amiens_formations_urls.json - URLs seulement (pour le scraper)")
print(f"{'='*80}\n")

# Compter combien ont des emails/réseaux dans Google Maps
avec_email_google = sum(1 for s in full_data if s['email_google'] or s['tous_emails_google'])
avec_social_google = sum(1 for s in full_data if s['reseaux_sociaux_google'])

print(f"DONNEES GOOGLE MAPS (REFERENCE):")
print(f"  Sites avec email: {avec_email_google}/{len(full_data)}")
print(f"  Sites avec réseaux sociaux: {avec_social_google}/{len(full_data)}")
print(f"{'='*80}\n")

