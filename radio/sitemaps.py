import logging

import requests
from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .views import news_slug

logger = logging.getLogger(__name__)


class StaticViewSitemap(Sitemap):
    changefreq = 'weekly'

    def items(self):
        return [
            'radio:home', 'radio:programm', 'radio:musik', 'radio:empfang',
            'radio:live', 'radio:verkehr', 'radio:nachrichten', 'radio:hotline',
            'radio:werbung', 'radio:ueber_uns', 'radio:kontakt',
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return 1.0 if item == 'radio:home' else 0.6


class NewsSitemap(Sitemap):
    """Holt die dauerhaft gespeicherten Artikel des Studios zur Sitemap-Generierung - fällt bei
    nicht erreichbarem Studio auf eine leere Liste zurück statt die ganze Sitemap zu zerschießen."""
    changefreq = 'hourly'
    priority = 0.7

    def items(self):
        try:
            response = requests.get(
                settings.RADIO_NEWS_API_URL,
                params={'page': 1, 'pageSize': 500},
                timeout=5,
            )
            response.raise_for_status()
            return response.json().get('items', [])
        except (requests.RequestException, ValueError) as exc:
            logger.warning('Sitemap: Nachrichten-Abruf fehlgeschlagen: %s', exc)
            return []

    def location(self, item):
        return reverse('radio:nachrichten_detail', args=[news_slug(item)])
