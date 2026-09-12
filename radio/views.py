import hashlib
import logging

import requests
from django.conf import settings
from django.contrib import messages
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.utils.text import slugify

from .forms import ContactForm, HotlineForm, WerbungForm
from .models import FrequencyEntry, Show

logger = logging.getLogger(__name__)

NEWS_PAGE_SIZE = 16
# Groß genug, um beim Auflösen einer Detail-URL (Slug) jeden dauerhaft gespeicherten Artikel zu
# erreichen, statt nur die erste Seite - die Artikel-Liste ist paginiert, ein einzelner Artikel
# kann also auf einer späteren Seite stehen.
NEWS_SLUG_SEARCH_SIZE = 500


def news_slug(item):
    """Baut eine lesbare, stabile URL aus der (ansonsten wenig aussagekräftigen) Artikel-ID des
    Studios - gut für SEO/GEO, da die URL selbst schon das Thema nennt. Der Hash-Suffix hält die
    Slugs eindeutig, falls zwei Schlagzeilen sich sehr ähneln."""
    digest = hashlib.sha1(item['id'].encode('utf-8')).hexdigest()[:8]
    base = slugify(item['headline'])[:70] or 'artikel'
    return f'{base}-{digest}'


def _fetch_news(page=1, page_size=NEWS_PAGE_SIZE, query=None):
    """Ruft eine Seite der dauerhaft gespeicherten Nachrichtenartikel vom Studio ab (dieselben
    KI-Artikel wie in /nachrichten dort, nach Aktualität sortiert, optional durchsucht). Gibt
    (items, totalPages, fehlermeldung) zurück - wirft nie."""
    params = {'page': page, 'pageSize': page_size}
    if query:
        params['q'] = query
    try:
        response = requests.get(settings.RADIO_NEWS_API_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get('items', []), data.get('totalPages', 1), None
    except (requests.RequestException, ValueError) as exc:
        logger.warning('Nachrichten-Abruf fehlgeschlagen: %s', exc)
        return [], 1, 'Die aktuellen Nachrichten sind gerade nicht erreichbar. Bitte versuche es gleich erneut.'


def _excerpt_of(article):
    """Der erste vollständige Absatz statt einer wortgenauen Abschneidung mitten im Satz - liest
    sich als Vorschau natürlicher, vor allem sobald die Artikel wieder mehrere Absätze haben."""
    for paragraph in article.split('\n'):
        if paragraph.strip():
            return paragraph.strip()
    return article


# --- Öffentliche Seiten ---------------------------------------------------

def home(request):
    # Kleine Nachrichten-Vorschau auf der Startseite - die Artikel bleiben hier auch dann sichtbar,
    # wenn die Ursprungsmeldung längst aus dem Live-Feed des Studios gerutscht ist (dauerhaft in
    # Postgres gespeichert, siehe news-articles-store.ts im Studio).
    news_items, _, _ = _fetch_news(page=1, page_size=4)
    for item in news_items:
        item['slug'] = news_slug(item)
        item['excerpt'] = _excerpt_of(item['article'])

    # Kleine Vorschau aus der Hörer-Hotline (Verkehr + Blitzer zusammen, neueste zuerst) - dieselben
    # Meldungen, die auch im Programm laufen, gehören genauso auf die Startseite wie die News.
    _, hotline_traffic, blitzer, _ = _fetch_traffic_overview()
    hotline_items = sorted(
        hotline_traffic + blitzer, key=lambda h: h.get('createdAt', 0), reverse=True,
    )[:3]

    context = {
        'shows': Show.objects.all()[:3],
        'frequencies': FrequencyEntry.objects.all()[:4],
        'player_embed_url': settings.RADIO_PLAYER_EMBED_URL,
        'news_items': news_items,
        'hotline_items': hotline_items,
    }
    return render(request, 'radio/home.html', context)


def programm(request):
    context = {'shows': Show.objects.all()}
    return render(request, 'radio/programm.html', context)


def musik(request):
    return render(request, 'radio/musik.html')


def empfang(request):
    context = {
        'frequencies': FrequencyEntry.objects.all(),
    }
    return render(request, 'radio/empfang.html', context)


def live(request):
    # Die Hörerzahl wird bewusst NICHT öffentlich gezeigt (solange die Reichweite noch klein ist,
    # wirkt "0 Hörer" eher abschreckend) - intern sieht das Team sie im Studio-Dashboard.
    context = {
        'player_embed_url': settings.RADIO_PLAYER_EMBED_URL,
    }
    return render(request, 'radio/live.html', context)


def _fetch_traffic_overview():
    """Ruft die Verkehrsübersicht des Studios ab (offizielle Staus/Sperrungen + Hörer-Hotline für
    Verkehr und Blitzer, dieselben Daten wie on air). Gibt (traffic, hotline_traffic, blitzer,
    fehlermeldung) zurück - wirft nie."""
    try:
        response = requests.get(settings.RADIO_TRAFFIC_API_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get('traffic', []), data.get('hotlineTraffic', []), data.get('blitzer', []), None
    except (requests.RequestException, ValueError) as exc:
        logger.warning('Verkehrs-Übersicht-Abruf fehlgeschlagen: %s', exc)
        return [], [], [], 'Die aktuellen Verkehrsdaten sind gerade nicht erreichbar. Bitte versuche es gleich erneut.'


def verkehr(request):
    """Staus/Sperrungen, Hörer-Verkehrsmeldungen und Blitzer-Meldungen, live vom Studio abgerufen
    (dieselben Daten wie on air). Wirft nie - ist das Studio gerade nicht erreichbar, zeigt die
    Seite einen Hinweis statt eines Fehlers."""
    traffic, hotline_traffic, blitzer, error = _fetch_traffic_overview()

    return render(request, 'radio/verkehr.html', {
        'traffic': traffic,
        'hotline_traffic': hotline_traffic,
        'blitzer': blitzer,
        'error': error,
    })


def nachrichten(request):
    """Nachrichtenübersicht mit ausführlichen, von der KI im Studio geschriebenen Artikeln - nach
    Aktualität sortiert (neueste zuerst), durchsuchbar und paginiert, wie auf der
    /nachrichten-Seite im Studio selbst. Artikel bleiben dauerhaft erreichbar, auch wenn die
    Ursprungsmeldung längst aus dem Live-Feed gerutscht ist."""
    try:
        page = max(1, int(request.GET.get('page', 1)))
    except ValueError:
        page = 1
    query = request.GET.get('q', '').strip()

    items, total_pages, error = _fetch_news(page=page, query=query or None)
    for item in items:
        item['slug'] = news_slug(item)
        item['excerpt'] = _excerpt_of(item['article'])

    return render(request, 'radio/nachrichten.html', {
        'items': items,
        'has_items': bool(items),
        'error': error,
        'page': page,
        'total_pages': total_pages,
        'prev_page': page - 1 if page > 1 else None,
        'next_page': page + 1 if page < total_pages else None,
        'query': query,
    })


def nachrichten_detail(request, slug):
    """Einzelner Artikel mit eigener URL/eigenen Meta-Daten (SEO: pro Thema eine indexierbare
    Seite statt nur einer Sammelseite; GEO: strukturierte Daten + klarer Aufbau, damit
    KI-Suchsysteme den Artikel sauber zitieren können). Artikel sind dauerhaft gespeichert
    (Postgres im Studio), ein 404 hier bedeutet also nur einen falschen/veralteten Link, nicht
    einen inzwischen verschwundenen Artikel."""
    items, _, error = _fetch_news(page=1, page_size=NEWS_SLUG_SEARCH_SIZE)

    article = next((item for item in items if news_slug(item) == slug), None)
    if article is None:
        if error:
            return render(request, 'radio/nachrichten_detail.html', {
                'article': None,
                'error': error,
            }, status=502)
        raise Http404('Dieser Artikel ist nicht mehr aktuell oder wurde nicht gefunden.')

    paragraphs = [p for p in article['article'].split('\n') if p.strip()]
    return render(request, 'radio/nachrichten_detail.html', {
        'article': article,
        'paragraphs': paragraphs,
        'error': None,
    })


def _submit_hotline_report(payload):
    """Reicht eine Meldung an die Hörer-Hotline des Studios weiter (POST /api/public/hotline).
    Gibt (ok, fehlermeldung) zurück – wirft nie, damit ein nicht erreichbares Studio nie den
    Formular-Erfolg auf dieser Seite verhindert."""
    try:
        response = requests.post(settings.RADIO_HOTLINE_API_URL, json=payload, timeout=5)
        if response.status_code >= 400:
            try:
                detail = response.json().get('error')
            except ValueError:
                detail = None
            return False, detail or 'Die Meldung konnte nicht angenommen werden.'
        return True, None
    except requests.RequestException as exc:
        logger.warning('Hotline-Übermittlung fehlgeschlagen: %s', exc)
        return False, 'Das Studio ist gerade nicht erreichbar. Bitte versuche es später erneut.'


def hotline(request):
    if request.method == 'POST':
        form = HotlineForm(request.POST)
        if form.is_valid():
            payload = dict(form.cleaned_data)
            # Bei Blitzer darf die Nachricht leer bleiben (siehe HotlineForm) - das Studio
            # verlangt aber weiterhin mindestens 3 Zeichen, also hier ein neutraler Platzhalter.
            if payload['type'] == 'blitzer' and not payload.get('message', '').strip():
                payload['message'] = 'Blitzer gemeldet.'
            ok, error = _submit_hotline_report(payload)
            if ok:
                messages.success(
                    request,
                    'Danke! Deine Meldung ist direkt im Studio eingegangen.'
                )
                return redirect('radio:hotline')
            messages.error(request, error)
    else:
        form = HotlineForm(initial={'region': 'Saarland'})

    return render(request, 'radio/hotline.html', {'form': form})


def werbung(request):
    if request.method == 'POST':
        form = WerbungForm(request.POST)
        if form.is_valid():
            payload = {
                'advertiser': form.cleaned_data['advertiser'],
                'contact': form.cleaned_data['contact'],
                'text': form.cleaned_data['text'],
                'perHour': form.cleaned_data['per_hour'],
            }
            try:
                response = requests.post(settings.RADIO_AD_REQUESTS_API_URL, json=payload, timeout=5)
                if response.status_code >= 400:
                    try:
                        detail = response.json().get('error')
                    except ValueError:
                        detail = None
                    messages.error(request, detail or 'Die Bewerbung konnte nicht angenommen werden.')
                else:
                    messages.success(
                        request,
                        'Danke! Ihre Bewerbung liegt der Redaktion im Studio zur Prüfung vor.'
                    )
                    return redirect('radio:werbung')
            except requests.RequestException as exc:
                logger.warning('Werbe-Bewerbung fehlgeschlagen: %s', exc)
                messages.error(
                    request,
                    'Das Studio ist gerade nicht erreichbar. Bitte versuche es später erneut.'
                )
    else:
        form = WerbungForm()

    return render(request, 'radio/werbung.html', {'form': form})


def ueber_uns(request):
    return render(request, 'radio/ueber_uns.html')


def impressum(request):
    return render(request, 'radio/impressum.html')


def datenschutz(request):
    return render(request, 'radio/datenschutz.html')


def kontakt(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            nachricht = form.save()
            # Zusätzlich zur lokalen Speicherung (Admin-Bereich) auch ans Studio weiterreichen,
            # damit Kontaktnachrichten nicht in einem separaten System untergehen, das niemand
            # checkt. Bewusst kein eigener Hotline-Typ nötig - 'sonstiges' ist dafür da.
            _submit_hotline_report({
                'type': 'sonstiges',
                'region': 'Saarland',
                'place': '',
                'road': '',
                'message': f'[Kontaktformular] {nachricht.nachricht}'[:400],
                'caller': nachricht.name,
                'contact': nachricht.email,
            })
            messages.success(
                request,
                'Danke für deine Nachricht! Wir melden uns so schnell wie möglich.'
            )
            return redirect('radio:kontakt')
    else:
        form = ContactForm()

    return render(request, 'radio/kontakt.html', {'form': form})


# --- Now-Playing-Proxy ------------------------------------------------------
# Ruft die Metadaten des Studios serverseitig ab und reicht sie als JSON
# weiter. Das umgeht CORS-Probleme, die beim direkten Aufruf der externen
# API aus dem Browser heraus auftreten könnten.

def nowplaying_proxy(request):
    try:
        response = requests.get(settings.RADIO_NOWPLAYING_API_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        logger.warning('Now-Playing-Abruf fehlgeschlagen: %s', exc)
        return JsonResponse(
            {'error': 'now-playing-nicht-verfuegbar'},
            status=502,
        )

    return JsonResponse(data, safe=False)
