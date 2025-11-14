# -*- coding: utf-8 -*-
"""
Compare les résultats du scraper VS les données Google Maps
"""
import json

print("\n" + "="*80)
print("COMPARAISON: SCRAPER vs GOOGLE MAPS")
print("="*80 + "\n")

# Charger les données
with open('amiens_formations_complet.json', encoding='utf-8') as f:
    google_data = json.load(f)

with open('results/amiens_scraper_results.json', encoding='utf-8') as f:
    scraper_data = json.load(f)

# Créer un dictionnaire ID -> données pour faciliter la comparaison
google_dict = {item['id']: item for item in google_data}

# Stats
google_avec_email = sum(1 for s in google_data if s['email_google'] or s['tous_emails_google'])
google_avec_social = sum(1 for s in google_data if s['reseaux_sociaux_google'])

scraper_avec_email = sum(1 for s in scraper_data if s['nb_emails'] > 0)
scraper_avec_social = sum(1 for s in scraper_data if s['nb_reseaux_sociaux'] > 0)

print("GOOGLE MAPS (référence):")
print(f"  Sites avec email: {google_avec_email}/76 ({google_avec_email/76*100:.1f}%)")
print(f"  Sites avec réseaux sociaux: {google_avec_social}/76 ({google_avec_social/76*100:.1f}%)")

print("\nSCRAPER (notre outil):")
print(f"  Sites avec email: {scraper_avec_email}/76 ({scraper_avec_email/76*100:.1f}%)")
print(f"  Total emails: {sum(s['nb_emails'] for s in scraper_data)}")
print(f"  Sites avec réseaux sociaux: {scraper_avec_social}/76 ({scraper_avec_social/76*100:.1f}%)")
print(f"  Total réseaux sociaux: {sum(s['nb_reseaux_sociaux'] for s in scraper_data)}")

print("\n" + "="*80)
print("COMPARAISON PAR SITE")
print("="*80 + "\n")

# Comparer site par site
manques = []
gains = []

for scraper_site in scraper_data:
    site_id = scraper_site['id']
    google_site = google_dict.get(site_id)
    
    if google_site:
        # Vérifier si Google a un email mais pas le scraper
        google_has_email = bool(google_site['email_google'] or google_site['tous_emails_google'])
        scraper_has_email = scraper_site['nb_emails'] > 0
        
        google_has_social = bool(google_site['reseaux_sociaux_google'])
        scraper_has_social = scraper_site['nb_reseaux_sociaux'] > 0
        
        # Sites où Google a trouvé mais pas le scraper
        if google_has_email and not scraper_has_email:
            manques.append({
                'url': scraper_site['url'],
                'type': 'email',
                'google_data': google_site['tous_emails_google'] or google_site['email_google']
            })
        
        if google_has_social and not scraper_has_social:
            manques.append({
                'url': scraper_site['url'],
                'type': 'réseaux sociaux',
                'google_data': google_site['reseaux_sociaux_google']
            })
        
        # Sites où le scraper a trouvé mais pas Google
        if scraper_has_email and not google_has_email:
            gains.append({
                'url': scraper_site['url'],
                'type': 'email',
                'scraper_data': ', '.join(scraper_site['emails'])
            })
        
        if scraper_has_social and not google_has_social:
            gains.append({
                'url': scraper_site['url'],
                'type': 'réseaux sociaux',
                'scraper_data': len(scraper_site['reseaux_sociaux'])
            })

print(f"SITES MANQUÉS PAR LE SCRAPER ({len(manques)}):")
print("(Google Maps a trouvé mais pas le scraper)\n")
for i, m in enumerate(manques[:10], 1):
    print(f"{i}. {m['url']}")
    print(f"   Type: {m['type']}")
    print(f"   Google avait: {m['google_data'][:100]}...")
    print()

if len(manques) > 10:
    print(f"... et {len(manques) - 10} autres\n")

print("\n" + "="*80)
print(f"SITES TROUVÉS EN PLUS PAR LE SCRAPER ({len(gains)}):")
print("(Scraper a trouvé mais pas Google Maps)\n")
for i, g in enumerate(gains[:10], 1):
    print(f"{i}. {g['url']}")
    print(f"   Type: {g['type']}")
    if g['type'] == 'email':
        print(f"   Scraper a trouvé: {g['scraper_data']}")
    else:
        print(f"   Scraper a trouvé: {g['scraper_data']} réseaux")
    print()

if len(gains) > 10:
    print(f"... et {len(gains) - 10} autres\n")

print("="*80)
print(f"TAUX DE RÉUSSITE:")
print(f"  Emails: {scraper_avec_email}/{google_avec_email} = {scraper_avec_email/google_avec_email*100 if google_avec_email > 0 else 0:.1f}% de couverture")
print(f"  Réseaux sociaux: {scraper_avec_social}/{google_avec_social} = {scraper_avec_social/google_avec_social*100 if google_avec_social > 0 else 0:.1f}% de couverture")
print("="*80 + "\n")

