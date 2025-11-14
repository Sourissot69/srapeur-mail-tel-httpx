# -*- coding: utf-8 -*-
"""
Compare VERSION NORMALE (7 pages) vs VERSION RAPIDE (3 pages)
"""
import json

print("\n" + "="*80)
print("COMPARAISON: VERSION 7 PAGES vs VERSION 3 PAGES")
print("="*80 + "\n")

# Charger les 2 versions
with open('results/amiens_scraper_results.json', encoding='utf-8') as f:
    v7pages = json.load(f)

with open('results/amiens_RAPIDE.json', encoding='utf-8') as f:
    v3pages = json.load(f)

# Stats version 7 pages
v7_emails_sites = sum(1 for s in v7pages if s['nb_emails'] > 0)
v7_total_emails = sum(s['nb_emails'] for s in v7pages)
v7_social_sites = sum(1 for s in v7pages if s['nb_reseaux_sociaux'] > 0)
v7_total_social = sum(s['nb_reseaux_sociaux'] for s in v7pages)

# Stats version 3 pages
v3_emails_sites = sum(1 for s in v3pages if s['nb_emails'] > 0)
v3_total_emails = sum(s['nb_emails'] for s in v3pages)
v3_social_sites = sum(1 for s in v3pages if s['nb_reseaux_sociaux'] > 0)
v3_total_social = sum(s['nb_reseaux_sociaux'] for s in v3pages)

print("VERSION 7 PAGES (normale):")
print(f"  Temps: ~4 minutes")
print(f"  Sites avec email: {v7_emails_sites}/76 ({v7_emails_sites/76*100:.1f}%)")
print(f"  Total emails: {v7_total_emails}")
print(f"  Sites avec réseaux: {v7_social_sites}/76 ({v7_social_sites/76*100:.1f}%)")
print(f"  Total réseaux: {v7_total_social}")
print(f"  TOTAL données: {v7_total_emails + v7_total_social}")

print("\nVERSION 3 PAGES (rapide):")
print(f"  Temps: ~2 minutes 14s")
print(f"  Sites avec email: {v3_emails_sites}/76 ({v3_emails_sites/76*100:.1f}%)")
print(f"  Total emails: {v3_total_emails}")
print(f"  Sites avec réseaux: {v3_social_sites}/76 ({v3_social_sites/76*100:.1f}%)")
print(f"  Total réseaux: {v3_total_social}")
print(f"  TOTAL données: {v3_total_emails + v3_total_social}")

print("\n" + "="*80)
print("DIFFÉRENCE:")
print("="*80)
print(f"  Vitesse: ~45% PLUS RAPIDE ✅")
print(f"  Sites avec email: {v3_emails_sites - v7_emails_sites} ({(v3_emails_sites - v7_emails_sites)/76*100:+.1f}%)")
print(f"  Total emails: {v3_total_emails - v7_total_emails} ({(v3_total_emails - v7_total_emails)/v7_total_emails*100 if v7_total_emails > 0 else 0:+.1f}%)")
print(f"  Sites avec réseaux: {v3_social_sites - v7_social_sites} ({(v3_social_sites - v7_social_sites)/76*100:+.1f}%)")
print(f"  Total réseaux: {v3_total_social - v7_total_social} ({(v3_total_social - v7_total_social)/v7_total_social*100 if v7_total_social > 0 else 0:+.1f}%)")

print("\n" + "="*80)
if v3_total_emails + v3_total_social >= v7_total_emails + v7_total_social:
    print("✅ VERDICT: VERSION 3 PAGES GAGNANTE !")
    print("   - Beaucoup plus rapide (45%)")
    print("   - Même qualité ou meilleure")
else:
    perte = ((v7_total_emails + v7_total_social) - (v3_total_emails + v3_total_social)) / (v7_total_emails + v7_total_social) * 100
    print(f"⚠️ VERDICT: Perte de {perte:.1f}% de données")
    print(f"   - Gain de vitesse: 45%")
    print(f"   - À vous de décider si le compromis vaut le coup")

print("="*80 + "\n")

