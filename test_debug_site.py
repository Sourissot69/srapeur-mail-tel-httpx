# -*- coding: utf-8 -*-
"""
Script de debug pour tester un site spécifique
"""
import asyncio
import httpx
from bs4 import BeautifulSoup
import re
from extractors import EmailExtractor, SocialMediaExtractor

async def test_site(url):
    print(f"\n{'='*80}")
    print(f"TEST DEBUG: {url}")
    print(f"{'='*80}\n")
    
    # Récupérer la page
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        try:
            response = await client.get(url)
            html = response.text
            
            print(f"✓ Page récupérée ({len(html)} caractères)")
            print(f"✓ Status code: {response.status_code}\n")
            
            # Tester l'extraction emails
            print("="*80)
            print("TEST EXTRACTION EMAILS")
            print("="*80)
            
            email_extractor = EmailExtractor(url)
            
            # Chercher tous les emails dans le HTML brut (avant filtrage)
            all_emails_raw = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)
            print(f"\nEmails trouvés dans HTML brut (AVANT filtrage): {len(set(all_emails_raw))}")
            for email in list(set(all_emails_raw))[:10]:
                print(f"  - {email}")
            
            # Chercher les mailto:
            mailto_links = re.findall(r'mailto:([^"\'<>\s]+)', html, re.I)
            print(f"\nLiens mailto: trouvés: {len(set(mailto_links))}")
            for email in list(set(mailto_links))[:10]:
                print(f"  - {email}")
            
            # Extraction avec le scraper
            emails_found = email_extractor.extract_emails_from_html(html, url)
            print(f"\nEmails APRÈS filtrage du scraper: {len(emails_found)}")
            for email_data in emails_found:
                print(f"  - {email_data['email']} ({email_data['type']}) - Section: {email_data['section']}")
            
            # Info sur le domaine
            print(f"\nDomaine du site: {email_extractor.site_domain}")
            print(f"Fournisseurs connus: {len(email_extractor.known_providers)} (gmail, hotmail, etc.)")
            
            # Tester l'extraction réseaux sociaux
            print("\n" + "="*80)
            print("TEST EXTRACTION RÉSEAUX SOCIAUX")
            print("="*80)
            
            social_extractor = SocialMediaExtractor()
            social_media = social_extractor.extract_social_media(html, url)
            
            print(f"\nRéseaux sociaux trouvés: {len(social_media)}")
            for platform, urls in social_media.items():
                print(f"\n{platform.upper()}:")
                for surl in urls:
                    print(f"  - {surl}")
            
            # Chercher LinkedIn manuellement
            linkedin_raw = re.findall(r'linkedin\.com/[^\s"\'<>]+', html, re.I)
            print(f"\nLinkedIn dans HTML brut: {len(set(linkedin_raw))}")
            for link in list(set(linkedin_raw))[:5]:
                print(f"  - {link}")
            
            print("\n" + "="*80)
            print("FIN DU TEST")
            print("="*80 + "\n")
            
        except Exception as e:
            print(f"Erreur: {e}")

if __name__ == '__main__':
    # Test sur le site problématique
    asyncio.run(test_site('https://retravailler-np.org/'))

