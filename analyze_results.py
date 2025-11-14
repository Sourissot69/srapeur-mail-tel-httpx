# -*- coding: utf-8 -*-
import json

with open('results/formations_aix_resultats.json', encoding='utf-8') as f:
    data = json.load(f)

total = len(data)
avec_emails = sum(1 for s in data if s['nb_emails'] > 0)
avec_social = sum(1 for s in data if s['nb_reseaux_sociaux'] > 0)
total_emails = sum(s['nb_emails'] for s in data)
total_social = sum(s['nb_reseaux_sociaux'] for s in data)

print(f'\n{"="*80}')
print(f'RESULTATS - 111 SITES DE FORMATIONS')
print(f'{"="*80}')
print(f'Total sites: {total}')
print(f'Sites avec emails: {avec_emails}/{total} ({avec_emails/total*100:.1f}%)')
print(f'Sites avec reseaux sociaux: {avec_social}/{total} ({avec_social/total*100:.1f}%)')
print(f'Total emails trouves: {total_emails}')
print(f'Total reseaux sociaux: {total_social}')
print(f'{"="*80}\n')

print('Top 5 sites avec le plus d\'emails:')
top = sorted(data, key=lambda x: x['nb_emails'], reverse=True)[:5]
for i, s in enumerate(top, 1):
    print(f'{i}. [{s["nb_emails"]} emails] {s["url"]}')
    print(f'   Emails: {", ".join(s["emails"])}')
    print()

print('\nTop 5 sites avec reseaux sociaux:')
top_social = sorted(data, key=lambda x: x['nb_reseaux_sociaux'], reverse=True)[:5]
for i, s in enumerate(top_social, 1):
    if s['nb_reseaux_sociaux'] > 0:
        print(f'{i}. [{s["nb_reseaux_sociaux"]} reseaux] {s["url"]}')
        for platform, urls in s['reseaux_sociaux'].items():
            print(f'   {platform}: {urls[0]}')
        print()

