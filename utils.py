# -*- coding: utf-8 -*-
"""
Fonctions utilitaires pour le scraper
"""

import re
from urllib.parse import urlparse, urljoin
import tldextract
from typing import Optional, Set
import logging

logger = logging.getLogger(__name__)


def extract_domain(url: str) -> Optional[str]:
    """
    Extrait le domaine principal d'une URL
    
    Args:
        url: URL complète
        
    Returns:
        Domaine principal (ex: "example.com") ou None si invalide
    """
    try:
        extracted = tldextract.extract(url)
        if extracted.domain and extracted.suffix:
            return f"{extracted.domain}.{extracted.suffix}"
        return None
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction du domaine de {url}: {e}")
        return None


def get_base_url(url: str) -> str:
    """
    Obtient l'URL de base (protocole + domaine)
    
    Args:
        url: URL complète
        
    Returns:
        URL de base (ex: "https://example.com")
    """
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def is_valid_url(url: str) -> bool:
    """
    Vérifie si une URL est valide
    
    Args:
        url: URL à vérifier
        
    Returns:
        True si valide, False sinon
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
    except Exception:
        return False


def normalize_url(url: str, base_url: str) -> str:
    """
    Normalise une URL (gère les URLs relatives)
    
    Args:
        url: URL à normaliser
        base_url: URL de base du site
        
    Returns:
        URL normalisée et absolue
    """
    # Si l'URL est déjà absolue, la retourner
    if url.startswith('http://') or url.startswith('https://'):
        return url
    
    # Sinon, la rendre absolue par rapport à base_url
    return urljoin(base_url, url)


def is_same_domain(url1: str, url2: str) -> bool:
    """
    Vérifie si deux URLs appartiennent au même domaine
    
    Args:
        url1: Première URL
        url2: Deuxième URL
        
    Returns:
        True si même domaine, False sinon
    """
    domain1 = extract_domain(url1)
    domain2 = extract_domain(url2)
    return domain1 == domain2 if domain1 and domain2 else False


def email_belongs_to_domain(email: str, site_domain: str, known_providers: Set[str]) -> bool:
    """
    Vérifie si un email doit être gardé selon les critères :
    1. Email du domaine du site
    2. Email d'un fournisseur connu (gmail, hotmail, etc.)
    
    Args:
        email: Adresse email à vérifier
        site_domain: Domaine du site scrapé
        known_providers: Set des fournisseurs d'email connus
        
    Returns:
        True si l'email doit être gardé, False sinon
    """
    if not email or '@' not in email:
        return False
    
    # Extraire le domaine de l'email
    email_domain = email.split('@')[1].lower()
    
    # Vérifier si c'est le domaine du site
    if site_domain and email_domain == site_domain.lower():
        return True
    
    # Vérifier si c'est un fournisseur connu
    if email_domain in known_providers:
        return True
    
    # Vérifier les sous-domaines du site (ex: contact.example.com)
    if site_domain and site_domain.lower() in email_domain:
        return True
    
    return False


def is_valid_email(email: str) -> bool:
    """
    Validation basique d'une adresse email
    
    Args:
        email: Email à valider
        
    Returns:
        True si valide, False sinon
    """
    # Pattern regex pour email basique
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False
    
    # Vérifications supplémentaires
    if email.count('@') != 1:
        return False
    
    local, domain = email.split('@')
    
    # Longueur minimale
    if len(local) < 1 or len(domain) < 3:
        return False
    
    # Pas d'espaces
    if ' ' in email:
        return False
    
    return True


def clean_email(email: str) -> str:
    """
    Nettoie une adresse email
    
    Args:
        email: Email à nettoyer
        
    Returns:
        Email nettoyé
    """
    # Supprimer les espaces
    email = email.strip()
    
    # Convertir en minuscules
    email = email.lower()
    
    # Supprimer les caractères parasites courants
    email = email.rstrip('.,;:!?')
    
    return email


def detect_page_type(url: str, content: str = "") -> str:
    """
    Détecte le type de page à partir de l'URL et du contenu
    
    Args:
        url: URL de la page
        content: Contenu HTML (optionnel)
        
    Returns:
        Type de page (home, contact, legal, cgv, about, etc.)
    """
    url_lower = url.lower()
    
    # Page d'accueil
    if url_lower.endswith('/') or url_lower.count('/') <= 3:
        return 'home'
    
    # Contact
    if any(word in url_lower for word in ['contact', 'coordonnee']):
        return 'contact'
    
    # Mentions légales
    if any(word in url_lower for word in ['mention', 'legal-notice']):
        return 'legal'
    
    # CGV
    if 'cgv' in url_lower or 'conditions-generales-vente' in url_lower:
        return 'cgv'
    
    # CGU
    if 'cgu' in url_lower or 'conditions-generales-utilisation' in url_lower or 'terms' in url_lower:
        return 'cgu'
    
    # Politique de confidentialité
    if any(word in url_lower for word in ['privacy', 'confidentialite', 'rgpd', 'donnees-personnelles']):
        return 'privacy'
    
    # À propos
    if any(word in url_lower for word in ['about', 'a-propos', 'qui-sommes-nous']):
        return 'about'
    
    return 'other'


def get_context_around_email(text: str, email: str, context_length: int = 50) -> str:
    """
    Obtient le contexte textuel autour d'un email
    
    Args:
        text: Texte complet
        email: Email à chercher
        context_length: Nombre de caractères de contexte de chaque côté
        
    Returns:
        Contexte autour de l'email
    """
    try:
        index = text.lower().find(email.lower())
        if index == -1:
            return ""
        
        start = max(0, index - context_length)
        end = min(len(text), index + len(email) + context_length)
        
        context = text[start:end]
        # Nettoyer les retours à la ligne multiples
        context = re.sub(r'\s+', ' ', context).strip()
        
        return context
    except Exception:
        return ""


def classify_email_type(email: str, context: str = "") -> str:
    """
    Classifie le type d'email selon son préfixe et son contexte
    
    Args:
        email: Adresse email
        context: Contexte textuel autour de l'email
        
    Returns:
        Type d'email (contact, service_client, dpo, direction, commercial, other)
    """
    email_lower = email.lower()
    context_lower = context.lower()
    
    # Contact général
    if any(prefix in email_lower for prefix in ['contact@', 'info@', 'bonjour@', 'hello@']):
        return 'contact_general'
    
    # Service client
    if any(prefix in email_lower for prefix in ['service@', 'client@', 'support@', 'aide@', 'sav@']):
        return 'service_client'
    
    # Protection des données
    if any(prefix in email_lower for prefix in ['dpo@', 'rgpd@', 'donnees@', 'privacy@']) or \
       any(word in context_lower for word in ['dpo', 'protection des données', 'délégué']):
        return 'dpo'
    
    # Direction
    if any(prefix in email_lower for prefix in ['direction@', 'admin@', 'directeur@']):
        return 'direction'
    
    # Commercial
    if any(prefix in email_lower for prefix in ['commercial@', 'vente@', 'sales@']):
        return 'commercial'
    
    # Email personnel (prénom.nom)
    if re.match(r'^[a-z]+\.[a-z]+@', email_lower):
        return 'personnel'
    
    return 'other'


def sanitize_filename(filename: str) -> str:
    """
    Sanitize un nom de fichier en supprimant les caractères invalides
    
    Args:
        filename: Nom de fichier à nettoyer
        
    Returns:
        Nom de fichier nettoyé
    """
    # Remplacer les caractères invalides par des underscores
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limiter la longueur
    filename = filename[:200]
    return filename


