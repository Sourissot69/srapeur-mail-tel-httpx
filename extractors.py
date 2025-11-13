# -*- coding: utf-8 -*-
"""
Extracteurs pour emails et réseaux sociaux
"""

import re
from bs4 import BeautifulSoup
from typing import List, Dict, Set, Optional
import logging
from urllib.parse import urljoin, urlparse

from config import SOCIAL_NETWORKS, HTML_SECTIONS, EMAIL_PROVIDERS
from utils import (
    clean_email, is_valid_email, email_belongs_to_domain,
    get_context_around_email, classify_email_type, extract_domain
)

logger = logging.getLogger(__name__)


class EmailExtractor:
    """Extracteur d'adresses email"""
    
    # Patterns regex pour emails
    EMAIL_PATTERNS = [
        # Email standard
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        # Email avec caractères accentués
        r'\b[A-Za-zÀ-ÿ0-9._%+-]+@[A-Za-zÀ-ÿ0-9.-]+\.[A-Z|a-z]{2,}\b',
        # Email obfusqué avec [at] ou (at)
        r'\b[A-Za-z0-9._%+-]+\s*[\[\(]at[\]\)]\s*[A-Za-z0-9.-]+\s*[\[\(]dot[\]\)]\s*[A-Z|a-z]{2,}\b',
        # Email obfusqué avec @ écrit
        r'\b[A-Za-z0-9._%+-]+\s*@\s*[A-Za-z0-9.-]+\s*\.\s*[A-Z|a-z]{2,}\b',
    ]
    
    def __init__(self, site_url: str):
        """
        Initialise l'extracteur
        
        Args:
            site_url: URL du site à scraper
        """
        self.site_url = site_url
        self.site_domain = extract_domain(site_url)
        self.known_providers = set(EMAIL_PROVIDERS)
        
    def extract_emails_from_html(self, html: str, page_url: str) -> List[Dict]:
        """
        Extrait les emails d'un contenu HTML
        
        Args:
            html: Contenu HTML
            page_url: URL de la page
            
        Returns:
            Liste de dictionnaires avec les emails et leur contexte
        """
        emails_found = []
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 1. Chercher dans le texte visible
        text = soup.get_text()
        emails_from_text = self._extract_from_text(text, page_url, 'body')
        emails_found.extend(emails_from_text)
        
        # 2. Chercher dans les attributs href (mailto:)
        emails_from_mailto = self._extract_from_mailto(soup, page_url)
        emails_found.extend(emails_from_mailto)
        
        # 3. Chercher dans les sections prioritaires
        emails_from_sections = self._extract_from_sections(soup, page_url)
        emails_found.extend(emails_from_sections)
        
        # 4. Chercher dans les scripts JSON-LD (données structurées)
        emails_from_jsonld = self._extract_from_jsonld(soup, page_url)
        emails_found.extend(emails_from_jsonld)
        
        # 5. Chercher dans les balises meta
        emails_from_meta = self._extract_from_meta(soup, page_url)
        emails_found.extend(emails_from_meta)
        
        # Dédupliquer et filtrer
        return self._deduplicate_and_filter(emails_found)
    
    def _extract_from_text(self, text: str, page_url: str, section: str) -> List[Dict]:
        """Extrait les emails du texte brut"""
        emails = []
        
        for pattern in self.EMAIL_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                raw_email = match.group(0)
                
                # Désobfusquer si nécessaire
                email = self._deobfuscate_email(raw_email)
                email = clean_email(email)
                
                if is_valid_email(email):
                    context = get_context_around_email(text, raw_email, 80)
                    email_type = classify_email_type(email, context)
                    
                    emails.append({
                        'email': email,
                        'page': page_url,
                        'section': section,
                        'context': context,
                        'type': email_type
                    })
        
        return emails
    
    def _extract_from_mailto(self, soup: BeautifulSoup, page_url: str) -> List[Dict]:
        """Extrait les emails des liens mailto:"""
        emails = []
        
        mailto_links = soup.find_all('a', href=re.compile(r'^mailto:', re.I))
        
        for link in mailto_links:
            href = link.get('href', '')
            # Extraire l'email du mailto:
            email_match = re.search(r'mailto:([^?&]+)', href, re.I)
            if email_match:
                email = clean_email(email_match.group(1))
                
                if is_valid_email(email):
                    # Déterminer la section
                    section = self._find_parent_section(link)
                    
                    # Obtenir le contexte (texte du lien et autour)
                    context = link.get_text(strip=True)
                    if link.parent:
                        context += ' ' + link.parent.get_text(strip=True)[:100]
                    
                    email_type = classify_email_type(email, context)
                    
                    emails.append({
                        'email': email,
                        'page': page_url,
                        'section': section,
                        'context': context,
                        'type': email_type
                    })
        
        return emails
    
    def _extract_from_sections(self, soup: BeautifulSoup, page_url: str) -> List[Dict]:
        """Extrait les emails des sections HTML prioritaires"""
        emails = []
        
        for section_name, selectors in HTML_SECTIONS.items():
            for selector in selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text()
                    section_emails = self._extract_from_text(text, page_url, section_name)
                    emails.extend(section_emails)
        
        return emails
    
    def _extract_from_jsonld(self, soup: BeautifulSoup, page_url: str) -> List[Dict]:
        """Extrait les emails des données structurées JSON-LD"""
        emails = []
        
        scripts = soup.find_all('script', type='application/ld+json')
        
        for script in scripts:
            try:
                import json
                data = json.loads(script.string)
                
                # Chercher récursivement les champs email
                email_fields = self._find_email_in_dict(data)
                
                for email in email_fields:
                    email = clean_email(email)
                    if is_valid_email(email):
                        emails.append({
                            'email': email,
                            'page': page_url,
                            'section': 'json-ld',
                            'context': 'Données structurées Schema.org',
                            'type': classify_email_type(email, '')
                        })
            except Exception as e:
                logger.debug(f"Erreur parsing JSON-LD: {e}")
        
        return emails
    
    def _extract_from_meta(self, soup: BeautifulSoup, page_url: str) -> List[Dict]:
        """Extrait les emails des balises meta"""
        emails = []
        
        meta_tags = soup.find_all('meta')
        
        for meta in meta_tags:
            content = meta.get('content', '')
            if content and '@' in content:
                # Chercher des emails dans le contenu
                for pattern in self.EMAIL_PATTERNS:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        email = clean_email(match.group(0))
                        if is_valid_email(email):
                            emails.append({
                                'email': email,
                                'page': page_url,
                                'section': 'meta',
                                'context': f"Meta {meta.get('name', meta.get('property', ''))}",
                                'type': classify_email_type(email, '')
                            })
        
        return emails
    
    def _find_email_in_dict(self, data: any, emails: Optional[List] = None) -> List[str]:
        """Recherche récursive d'emails dans une structure de données"""
        if emails is None:
            emails = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                if key.lower() in ['email', 'e-mail', 'mail'] and isinstance(value, str):
                    emails.append(value)
                else:
                    self._find_email_in_dict(value, emails)
        elif isinstance(data, list):
            for item in data:
                self._find_email_in_dict(item, emails)
        
        return emails
    
    def _find_parent_section(self, element) -> str:
        """Trouve la section parente d'un élément"""
        # Chercher le parent footer, header, etc.
        for section_name, selectors in HTML_SECTIONS.items():
            for selector in selectors:
                # Simplifier le sélecteur pour find_parent
                tag = selector.lstrip('.#').split('[')[0]
                parent = element.find_parent(tag)
                if parent:
                    return section_name
        
        return 'body'
    
    def _deobfuscate_email(self, email: str) -> str:
        """Désobfusque un email (remplace [at], (at), etc.)"""
        email = re.sub(r'\s*[\[\(]at[\]\)]\s*', '@', email, flags=re.I)
        email = re.sub(r'\s*[\[\(]dot[\]\)]\s*', '.', email, flags=re.I)
        email = re.sub(r'\s+', '', email)
        return email
    
    def _deduplicate_and_filter(self, emails: List[Dict]) -> List[Dict]:
        """
        Déduplique et filtre les emails selon les critères :
        - Garder emails du domaine du site
        - Garder emails des fournisseurs connus
        """
        seen = set()
        filtered = []
        
        for email_data in emails:
            email = email_data['email']
            
            # Ignorer si déjà vu
            if email in seen:
                continue
            
            # Vérifier si l'email doit être gardé
            if email_belongs_to_domain(email, self.site_domain, self.known_providers):
                seen.add(email)
                filtered.append(email_data)
                logger.debug(f"Email gardé: {email} (domaine: {self.site_domain})")
            else:
                logger.debug(f"Email ignoré: {email} (ne correspond pas aux critères)")
        
        return filtered


class SocialMediaExtractor:
    """Extracteur de réseaux sociaux"""
    
    def __init__(self):
        """Initialise l'extracteur"""
        self.patterns = SOCIAL_NETWORKS
    
    def extract_social_media(self, html: str, page_url: str) -> Dict[str, List[str]]:
        """
        Extrait les réseaux sociaux d'un contenu HTML
        
        Args:
            html: Contenu HTML
            page_url: URL de la page
            
        Returns:
            Dictionnaire {platform: [urls]}
        """
        social_media = {}
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Chercher dans les liens
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href', '')
            
            # Vérifier chaque réseau social
            for platform, patterns in self.patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, href, re.IGNORECASE)
                    if match:
                        url = self._normalize_social_url(match.group(0), platform)
                        if url:
                            if platform not in social_media:
                                social_media[platform] = []
                            if url not in social_media[platform]:
                                social_media[platform].append(url)
        
        # Chercher aussi dans le texte brut (URLs non linkées)
        text = soup.get_text()
        for platform, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    url = self._normalize_social_url(match.group(0), platform)
                    if url:
                        if platform not in social_media:
                            social_media[platform] = []
                        if url not in social_media[platform]:
                            social_media[platform].append(url)
        
        return social_media
    
    def _normalize_social_url(self, url: str, platform: str) -> Optional[str]:
        """Normalise une URL de réseau social"""
        # Ajouter https:// si manquant
        if not url.startswith('http'):
            url = 'https://' + url
        
        # Supprimer les paramètres de tracking
        url = url.split('?')[0]
        
        # Supprimer le trailing slash
        url = url.rstrip('/')
        
        return url

