# -*- coding: utf-8 -*-
"""
Configuration du scraper
"""

# User Agents pour rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
]

# Fournisseurs d'emails publics connus à accepter
EMAIL_PROVIDERS = [
    'gmail.com',
    'googlemail.com',
    'hotmail.com',
    'hotmail.fr',
    'outlook.com',
    'outlook.fr',
    'yahoo.com',
    'yahoo.fr',
    'laposte.net',
    'orange.fr',
    'wanadoo.fr',
    'free.fr',
    'sfr.fr',
    'live.com',
    'live.fr',
    'msn.com',
    'icloud.com',
    'me.com',
    'mac.com',
    'aol.com',
    'protonmail.com',
    'protonmail.ch',
    'yandex.com',
    'mail.com',
    'gmx.com',
    'zoho.com',
]

# Timeouts et délais (OPTIMISÉ POUR VITESSE)
TIMEOUT = 10  # secondes (réduit de 15 à 10)
DELAY_BETWEEN_REQUESTS = 0.3  # secondes entre chaque requête (réduit de 1.0 à 0.3)
MAX_RETRIES = 2  # réduit de 3 à 2
BACKOFF_FACTOR = 2  # facteur multiplicateur pour retry

# Limites de crawling (OPTIMISÉ VITESSE)
MAX_PAGES_PER_SITE = 3  # réduit à 3 pour gain de vitesse (60% plus rapide)
MAX_DEPTH = 1  # réduit à 1 niveau
MAX_CONCURRENT_SITES = 10  # 10 sites en parallèle

# Timeout global par site
SITE_TIMEOUT = 20  # secondes (réduit à 20 pour plus de vitesse)

# Pages à chercher (PRIORITAIRES SEULEMENT - pour vitesse)
# Seulement les 3 pages les plus susceptibles d'avoir emails/réseaux sociaux
PAGES_TO_SCRAPE = [
    '/',  # Page d'accueil
    '/contact',
    '/mentions-legales',
]

# Patterns pour détecter les liens importants
IMPORTANT_LINK_PATTERNS = [
    r'(?i)(contact|mention|legal|cgv|cgu|condition|privacy|privac|rgpd|about|propos|qui-sommes)',
]

# Sections HTML prioritaires
HTML_SECTIONS = {
    'footer': ['footer', '.footer', '.site-footer', '#footer', '[class*="footer"]'],
    'header': ['header', '.header', '.site-header', '#header', 'nav', '.navbar', '.navigation'],
    'contact': ['.contact', '#contact', '.contact-info', '.contact-section', '[class*="contact"]'],
    'legal': ['.legal', '.mentions', '[class*="legal"]', '[class*="mention"]'],
    'sidebar': ['.sidebar', '.aside', 'aside', '[class*="sidebar"]'],
}

# Réseaux sociaux à détecter
SOCIAL_NETWORKS = {
    'facebook': [
        r'(?:https?://)?(?:www\.)?(?:facebook\.com|fb\.com|fb\.me)/[\w\-\.]+',
        r'(?:https?://)?(?:www\.)?(?:facebook\.com|fb\.com)/pages/[\w\-\./]+',
    ],
    'instagram': [
        r'(?:https?://)?(?:www\.)?instagram\.com/[\w\-\.]+',
    ],
    'twitter': [
        r'(?:https?://)?(?:www\.)?(?:twitter\.com|x\.com)/[\w\-]+',
    ],
    'linkedin': [
        r'(?:https?://)?(?:www\.)?linkedin\.com/(?:company|in)/[\w\-]+',
    ],
    'youtube': [
        r'(?:https?://)?(?:www\.)?youtube\.com/(?:c|channel|user)/[\w\-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/@[\w\-]+',
    ],
    'tiktok': [
        r'(?:https?://)?(?:www\.)?tiktok\.com/@[\w\-\.]+',
    ],
    'whatsapp': [
        r'(?:https?://)?(?:wa\.me|api\.whatsapp\.com)/[\d]+',
    ],
    'telegram': [
        r'(?:https?://)?(?:t\.me|telegram\.me)/[\w\-]+',
    ],
}

# Headers HTTP
HTTP_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'scraper.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Output
RESULTS_DIR = 'results'
OUTPUT_JSON = 'scraping_results.json'
OUTPUT_CSV = 'scraping_results.csv'
OUTPUT_HTML = 'scraping_report.html'

