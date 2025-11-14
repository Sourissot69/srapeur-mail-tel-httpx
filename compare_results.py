# -*- coding: utf-8 -*-
"""
Script de comparaison des résultats AVANT vs APRÈS amélioration
"""
import json

print("\n" + "="*80)
print("COMPARAISON : AVANT vs APRÈS AMÉLIORATION")
print("="*80 + "\n")

# Charger les 2 versions
with open('results/formations_aix_resultats.json', encoding='utf-8') as f:
    avant = json.load(f)

with open('results/formations_aix_AMELIORE.json', encoding='utf-8') as f:
    apres = json.load(f)

# Stats AVANT
avant_emails = sum(1 for s in avant if s['nb_emails'] > 0)
avant_total_emails = sum(s['nb_emails'] for s in avant)
avant_social = sum(1 for s in avant if s['nb_reseaux_sociaux'] > 0)
avant_total_social = sum(s['nb_reseaux_sociaux'] for s in avant)

# Stats APRÈS
apres_emails = sum(1 for s in apres if s['nb_emails'] > 0)
apres_total_emails = sum(s['nb_emails'] for s in apres)
apres_social = sum(1 for s in apres if s['nb_reseaux_sociaux'] > 0)
apres_total_social = sum(s['nb_reseaux_sociaux'] for s in apres)

print("AVANT AMÉLIORATION :")
print(f"  Sites avec emails: {avant_emails}/111 ({avant_emails/111*100:.1f}%)")
print(f"  Total emails: {avant_total_emails}")
print(f"  Sites avec réseaux sociaux: {avant_social}/111 ({avant_social/111*100:.1f}%)")
print(f"  Total réseaux sociaux: {avant_total_social}")

print("\nAPRÈS AMÉLIORATION :")
print(f"  Sites avec emails: {apres_emails}/111 ({apres_emails/111*100:.1f}%)")
print(f"  Total emails: {apres_total_emails}")
print(f"  Sites avec réseaux sociaux: {apres_social}/111 ({apres_social/111*100:.1f}%)")
print(f"  Total réseaux sociaux: {apres_total_social}")

print("\n" + "="*80)
print("GAINS :")
print("="*80)
print(f"  Sites avec emails: +{apres_emails - avant_emails} ({(apres_emails - avant_emails)/111*100:.1f}% de gain)")
print(f"  Total emails: +{apres_total_emails - avant_total_emails} (+{(apres_total_emails/avant_total_emails-1)*100:.1f}%)")
print(f"  Sites avec réseaux sociaux: +{apres_social - avant_social} ({(apres_social - avant_social)/111*100:.1f}% de gain)")
print(f"  Total réseaux sociaux: +{apres_total_social - avant_total_social} (+{(apres_total_social/avant_total_social-1)*100 if avant_total_social > 0 else 0:.1f}%)")

print("\n" + "="*80)
print("EXEMPLES D'AMÉLIORATIONS :")
print("="*80 + "\n")

# Trouver des sites qui ont gagné des emails
gains = []
for i in range(len(avant)):
    if avant[i]['nb_emails'] < apres[i]['nb_emails']:
        gains.append({
            'url': apres[i]['url'],
            'avant': avant[i]['nb_emails'],
            'apres': apres[i]['nb_emails'],
            'emails': apres[i]['emails']
        })

if gains:
    print(f"Sites avec emails trouvés en PLUS (top 10) :")
    for i, gain in enumerate(gains[:10], 1):
        print(f"{i}. {gain['url']}")
        print(f"   Avant: {gain['avant']} emails | Après: {gain['apres']} emails")
        print(f"   Emails trouvés: {', '.join(gain['emails'])}")
        print()

print("="*80 + "\n")

