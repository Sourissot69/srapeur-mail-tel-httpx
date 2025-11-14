# -*- coding: utf-8 -*-
"""
Scraper principal pour extraire emails et réseaux sociaux
"""

import asyncio
import httpx
import time
import logging
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import random
from datetime import datetime
import json
import os

from config import (
    USER_AGENTS, HTTP_HEADERS, TIMEOUT, DELAY_BETWEEN_REQUESTS,
    MAX_RETRIES, BACKOFF_FACTOR, MAX_PAGES_PER_SITE, MAX_CONCURRENT_SITES,
    SITE_TIMEOUT, PAGES_TO_SCRAPE, IMPORTANT_LINK_PATTERNS, RESULTS_DIR
)
from extractors import EmailExtractor, SocialMediaExtractor
from utils import (
    extract_domain, get_base_url, is_valid_url, normalize_url,
    is_same_domain, detect_page_type, sanitize_filename
)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WebScraper:
    """Scraper web asynchrone pour emails et réseaux sociaux"""
    
    def __init__(self):
        """Initialise le scraper"""
        self.visited_urls: Set[str] = set()
        self.results: List[Dict] = []
        self.start_time = None
        
    def get_random_user_agent(self) -> str:
        """Retourne un User-Agent aléatoire"""
        return random.choice(USER_AGENTS)
    
    def get_headers(self) -> Dict[str, str]:
        """Retourne les headers HTTP avec un User-Agent aléatoire"""
        headers = HTTP_HEADERS.copy()
        headers['User-Agent'] = self.get_random_user_agent()
        return headers
    
    async def check_page_exists(self, client: httpx.AsyncClient, url: str) -> bool:
        """
        Vérifie rapidement si une page existe avec une requête HEAD
        
        Args:
            client: Client HTTP asyncio
            url: URL à vérifier
            
        Returns:
            True si page existe (200), False sinon
        """
        try:
            response = await client.head(url, timeout=5, follow_redirects=True)
            return response.status_code == 200
        except Exception:
            # En cas d'erreur HEAD, on considère que la page existe (pour être sûr)
            return True
    
    async def fetch_page(self, client: httpx.AsyncClient, url: str, retry: int = 0) -> Optional[str]:
        """
        Récupère le contenu d'une page
        
        Args:
            client: Client HTTP asyncio
            url: URL à récupérer
            retry: Nombre de tentatives effectuées
            
        Returns:
            Contenu HTML ou None si erreur
        """
        try:
            logger.info(f"Récupération de {url}")
            response = await client.get(url, timeout=TIMEOUT, follow_redirects=True)
            
            if response.status_code == 200:
                return response.text
            elif response.status_code == 429:  # Rate limiting
                if retry < MAX_RETRIES:
                    wait_time = BACKOFF_FACTOR ** retry
                    logger.warning(f"Rate limited sur {url}, attente de {wait_time}s")
                    await asyncio.sleep(wait_time)
                    return await self.fetch_page(client, url, retry + 1)
            else:
                logger.warning(f"Status code {response.status_code} pour {url}")
                return None
                
        except httpx.TimeoutException:
            logger.error(f"Timeout sur {url}")
            if retry < MAX_RETRIES:
                return await self.fetch_page(client, url, retry + 1)
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de {url}: {e}")
            if retry < MAX_RETRIES:
                await asyncio.sleep(1)
                return await self.fetch_page(client, url, retry + 1)
            return None
    
    def find_important_links(self, html: str, base_url: str) -> List[str]:
        """
        Trouve les liens importants dans le HTML (contact, mentions légales, etc.)
        
        Args:
            html: Contenu HTML
            base_url: URL de base du site
            
        Returns:
            Liste des URLs importantes trouvées
        """
        soup = BeautifulSoup(html, 'html.parser')
        important_links = []
        
        # Chercher tous les liens
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href', '')
            
            # Normaliser l'URL
            full_url = normalize_url(href, base_url)
            
            # Vérifier si c'est du même domaine
            if not is_same_domain(full_url, base_url):
                continue
            
            # Vérifier si c'est un lien important
            for pattern in IMPORTANT_LINK_PATTERNS:
                import re
                if re.search(pattern, full_url, re.I) or re.search(pattern, link.get_text(), re.I):
                    if full_url not in important_links:
                        important_links.append(full_url)
                        break
        
        return important_links
    
    async def scrape_site(self, site_data: Dict) -> Dict:
        """
        Scrape un site complet
        
        Args:
            site_data: Dictionnaire avec les infos du site (url, name, etc.)
            
        Returns:
            Résultats du scraping
        """
        site_url = site_data.get('url', '')
        site_name = site_data.get('name', 'Unknown')
        
        logger.info(f"\n{'='*80}")
        logger.info(f"Début du scraping de: {site_name}")
        logger.info(f"URL: {site_url}")
        logger.info(f"{'='*80}")
        
        start_time = time.time()
        
        result = {
            'url': site_url,
            'name': site_name,
            'status': 'pending',
            'scraping_time': 0,
            'pages_visited': [],
            'emails': [],
            'social_media': {},
            'error': None
        }
        
        try:
            # Vérifier que l'URL est valide
            if not is_valid_url(site_url):
                result['status'] = 'error'
                result['error'] = 'URL invalide'
                return result
            
            base_url = get_base_url(site_url)
            
            # Initialiser les extracteurs
            email_extractor = EmailExtractor(site_url)
            social_extractor = SocialMediaExtractor()
            
            # Liste des URLs à visiter
            urls_to_visit = [site_url]
            
            # Ajouter les pages communes à tester
            for page in PAGES_TO_SCRAPE:
                url = urljoin(base_url, page)
                if url not in urls_to_visit:
                    urls_to_visit.append(url)
            
            visited_count = 0
            
            async with httpx.AsyncClient(headers=self.get_headers()) as client:
                # Timeout global pour le site
                try:
                    async with asyncio.timeout(SITE_TIMEOUT):
                        for url in urls_to_visit:
                            if visited_count >= MAX_PAGES_PER_SITE:
                                logger.info(f"Limite de {MAX_PAGES_PER_SITE} pages atteinte")
                                break
                            
                            if url in self.visited_urls:
                                continue
                            
                            # Vérifier d'abord si la page existe (HEAD request)
                            if not await self.check_page_exists(client, url):
                                logger.debug(f"Page inexistante (HEAD), skip: {url}")
                                continue
                            
                            # Récupérer la page
                            html = await self.fetch_page(client, url)
                            
                            if html:
                                self.visited_urls.add(url)
                                visited_count += 1
                                
                                page_type = detect_page_type(url, html)
                                
                                page_result = {
                                    'url': url,
                                    'type': page_type,
                                    'status': 'success',
                                    'emails_found': 0,
                                    'social_found': 0
                                }
                                
                                # Extraire les emails
                                emails = email_extractor.extract_emails_from_html(html, url)
                                if emails:
                                    result['emails'].extend(emails)
                                    page_result['emails_found'] = len(emails)
                                    logger.info(f"  ✓ {len(emails)} email(s) trouvé(s) sur {url}")
                                
                                # Extraire les réseaux sociaux
                                social_media = social_extractor.extract_social_media(html, url)
                                if social_media:
                                    for platform, urls_list in social_media.items():
                                        if platform not in result['social_media']:
                                            result['social_media'][platform] = []
                                        for social_url in urls_list:
                                            if social_url not in result['social_media'][platform]:
                                                result['social_media'][platform].append(social_url)
                                    page_result['social_found'] = sum(len(v) for v in social_media.values())
                                    logger.info(f"  ✓ Réseaux sociaux trouvés: {', '.join(social_media.keys())}")
                                
                                result['pages_visited'].append(page_result)
                                
                                # Si c'est la page d'accueil, chercher d'autres liens importants
                                if visited_count == 1:
                                    important_links = self.find_important_links(html, base_url)
                                    for link in important_links[:5]:  # Limiter à 5 liens supplémentaires
                                        if link not in urls_to_visit:
                                            urls_to_visit.append(link)
                                
                                # Délai entre les requêtes
                                await asyncio.sleep(DELAY_BETWEEN_REQUESTS)
                            else:
                                result['pages_visited'].append({
                                    'url': url,
                                    'type': detect_page_type(url),
                                    'status': 'failed',
                                    'emails_found': 0,
                                    'social_found': 0
                                })
                
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout global atteint pour {site_name}")
                    result['error'] = 'Timeout global'
            
            # Dédupliquer les emails
            result['emails'] = self._deduplicate_emails(result['emails'])
            
            # Calculer le temps de scraping
            result['scraping_time'] = round(time.time() - start_time, 2)
            result['status'] = 'success'
            
            # Résumé
            logger.info(f"\n{'-'*80}")
            logger.info(f"Scraping terminé pour: {site_name}")
            logger.info(f"  • Pages visitées: {len(result['pages_visited'])}")
            logger.info(f"  • Emails trouvés: {len(result['emails'])}")
            logger.info(f"  • Réseaux sociaux: {', '.join(result['social_media'].keys()) if result['social_media'] else 'Aucun'}")
            logger.info(f"  • Temps: {result['scraping_time']}s")
            logger.info(f"{'-'*80}\n")
            
        except Exception as e:
            logger.error(f"Erreur lors du scraping de {site_name}: {e}")
            result['status'] = 'error'
            result['error'] = str(e)
            result['scraping_time'] = round(time.time() - start_time, 2)
        
        return result
    
    def _deduplicate_emails(self, emails: List[Dict]) -> List[Dict]:
        """Déduplique les emails en gardant la première occurrence"""
        seen = set()
        deduplicated = []
        
        for email_data in emails:
            email = email_data['email']
            if email not in seen:
                seen.add(email)
                deduplicated.append(email_data)
        
        return deduplicated
    
    async def scrape_multiple_sites(self, sites: List[Dict]) -> List[Dict]:
        """
        Scrape plusieurs sites en parallèle (limité)
        
        Args:
            sites: Liste des sites à scraper
            
        Returns:
            Liste des résultats
        """
        self.start_time = time.time()
        results = []
        
        # Créer des batches de sites à scraper en parallèle
        for i in range(0, len(sites), MAX_CONCURRENT_SITES):
            batch = sites[i:i+MAX_CONCURRENT_SITES]
            logger.info(f"\n{'#'*80}")
            logger.info(f"Traitement du batch {i//MAX_CONCURRENT_SITES + 1} ({len(batch)} sites)")
            logger.info(f"{'#'*80}")
            
            tasks = [self.scrape_site(site) for site in batch]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
            
            # Sauvegarder progressivement
            self._save_progress(results)
        
        return results
    
    def _save_progress(self, results: List[Dict]):
        """Sauvegarde progressive des résultats"""
        try:
            os.makedirs(RESULTS_DIR, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            progress_file = os.path.join(RESULTS_DIR, f'progress_{timestamp}.json')
            
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Progression sauvegardée dans {progress_file}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {e}")
    
    def generate_report(self, results: List[Dict]) -> Dict:
        """
        Génère un rapport de statistiques
        
        Args:
            results: Résultats du scraping
            
        Returns:
            Dictionnaire de statistiques
        """
        total_sites = len(results)
        successful = sum(1 for r in results if r['status'] == 'success')
        failed = total_sites - successful
        
        total_emails = sum(len(r['emails']) for r in results)
        total_pages = sum(len(r['pages_visited']) for r in results)
        
        # Réseaux sociaux par plateforme
        social_stats = {}
        for result in results:
            for platform, urls in result.get('social_media', {}).items():
                social_stats[platform] = social_stats.get(platform, 0) + len(urls)
        
        total_time = round(time.time() - self.start_time, 2) if self.start_time else 0
        avg_time = round(total_time / total_sites, 2) if total_sites > 0 else 0
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_sites': total_sites,
            'successful': successful,
            'failed': failed,
            'success_rate': round(successful / total_sites * 100, 1) if total_sites > 0 else 0,
            'total_emails': total_emails,
            'total_pages_visited': total_pages,
            'social_media_stats': social_stats,
            'total_time_seconds': total_time,
            'average_time_per_site': avg_time,
        }
        
        return report
    
    def save_results(self, results: List[Dict], report: Dict):
        """
        Sauvegarde les résultats finaux
        
        Args:
            results: Résultats du scraping
            report: Rapport de statistiques
        """
        os.makedirs(RESULTS_DIR, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON complet
        json_file = os.path.join(RESULTS_DIR, f'scraping_results_{timestamp}.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'report': report,
                'results': results
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"RAPPORT FINAL")
        logger.info(f"{'='*80}")
        logger.info(f"Sites scrapés: {report['total_sites']}")
        logger.info(f"Succès: {report['successful']} ({report['success_rate']}%)")
        logger.info(f"Échecs: {report['failed']}")
        logger.info(f"Total emails: {report['total_emails']}")
        logger.info(f"Total pages visitées: {report['total_pages_visited']}")
        logger.info(f"Réseaux sociaux: {report['social_media_stats']}")
        logger.info(f"Temps total: {report['total_time_seconds']}s")
        logger.info(f"Temps moyen par site: {report['average_time_per_site']}s")
        logger.info(f"\nRésultats sauvegardés dans: {json_file}")
        logger.info(f"{'='*80}\n")


async def main():
    """Fonction principale"""
    # Exemple d'utilisation
    scraper = WebScraper()
    
    # Charger les sites depuis le JSON
    sites = []
    try:
        with open('sites_to_scrape.json', 'r', encoding='utf-8') as f:
            sites = json.load(f)
    except FileNotFoundError:
        logger.error("Fichier sites_to_scrape.json introuvable. Utilisez extract_sites.py d'abord.")
        return
    
    if not sites:
        logger.error("Aucun site à scraper")
        return
    
    logger.info(f"Démarrage du scraping de {len(sites)} sites...")
    
    # Scraper tous les sites
    results = await scraper.scrape_multiple_sites(sites)
    
    # Générer le rapport
    report = scraper.generate_report(results)
    
    # Sauvegarder les résultats
    scraper.save_results(results, report)


if __name__ == '__main__':
    asyncio.run(main())

