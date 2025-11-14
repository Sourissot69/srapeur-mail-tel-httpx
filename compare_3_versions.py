# -*- coding: utf-8 -*-
"""
Comparaison des 3 versions
"""
import json

print("\n" + "="*80)
print("COMPARAISON DES 3 VERSIONS - 111 SITES")
print("="*80 + "\n")

# Charger les 3 versions
with open('results/formations_aix_resultats.json', encoding='utf-8') as f:
    v1 = json.load(f)

with open('results/formations_aix_AMELIORE.json', encoding='utf-8') as f:
    v2 = json.load(f)

with open('results/formations_aix_V2.json', encoding='utf-8') as f:
    v3 = json.load(f)

# Stats pour chaque version
versions = [
    ("VERSION 1 (Originale)", v1),
    ("VERSION 2 (Amélioration 1)", v2),
    ("VERSION 3 (Amélioration 2)", v3)
]

for nom, data in versions:
    emails_sites = sum(1 for s in data if s['nb_emails'] > 0)
    total_emails = sum(s['nb_emails'] for s in data)
    social_sites = sum(1 for s in data if s['nb_reseaux_sociaux'] > 0)
    total_social = sum(s['nb_reseaux_sociaux'] for s in data)
    
    print(f"{nom}:")
    print(f"  Sites avec emails: {emails_sites}/111 ({emails_sites/111*100:.1f}%)")
    print(f"  Total emails: {total_emails}")
    print(f"  Sites avec réseaux: {social_sites}/111 ({social_sites/111*100:.1f}%)")
    print(f"  Total réseaux: {total_social}")
    print()

print("="*80)
print("MEILLEURE VERSION: V3")
print("="*80)
v3_emails = sum(s['nb_emails'] for s in v3)
v3_social = sum(s['nb_reseaux_sociaux'] for s in v3)
print(f"Total données extraites: {v3_emails + v3_social} (emails + réseaux sociaux)")
print("="*80 + "\n")

