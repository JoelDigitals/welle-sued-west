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

NEWS_REGION_ORDER = ['Saarland', 'Rheinland-Pfalz', 'Deutschland', 'Welt']


def news_slug(item):
    """Baut eine lesbare, stabile URL aus der (ansonsten wenig aussagekräftigen) Artikel-ID des
    Studios - gut für SEO/GEO, da die URL selbst schon das Thema nennt. Der Hash-Suffix hält die
    Slugs eindeutig, falls zwei Schlagzeilen sich sehr ähneln."""
    digest = hashlib.sha1(item['id'].encode('utf-8')).hexdigest()[:8]
    base = slugify(item['headline'])[:70] or 'artikel'
    return f'{base}-{digest}'


def _fetch_news():
    """Ruft die Nachrichten-Snapshot-API des Studios ab (dieselben KI-Artikel wie in
    /nachrichten dort). Gibt (items, fehlermeldung) zurück - wirft nie."""
    try:
        response = requests.get(settings.RADIO_NEWS_API_URL, timeout=5)
        response.raise_for_status()
        return response.json().get('items', []), None
    except (requests.RequestException, ValueError) as exc:
        logger.warning('Nachrichten-Abruf fehlgeschlagen: %s', exc)
        return [], 'Die aktuellen Nachrichten sind gerade nicht erreichbar. Bitte versuche es gleich erneut.'


# --- Öffentliche Seiten ---------------------------------------------------

def home(request):
    context = {
        'shows': Show.objects.all()[:3],
        'frequencies': FrequencyEntry.objects.all()[:4],
        'player_embed_url': settings.RADIO_PLAYER_EMBED_URL,
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
    listener_stats = None
    try:
        response = requests.get(settings.RADIO_LISTENER_STATS_API_URL, timeout=5)
        response.raise_for_status()
        listener_stats = response.json()
    except (requests.RequestException, ValueError) as exc:
        logger.warning('Zuhörer-Statistik-Abruf fehlgeschlagen: %s', exc)

    context = {
        'player_embed_url': settings.RADIO_PLAYER_EMBED_URL,
        'listener_stats': listener_stats,
    }
    return render(request, 'radio/live.html', context)


def verkehr(request):
    """Staus/Sperrungen und Blitzer-Meldungen, live vom Studio abgerufen (dieselben Daten wie
    on air). Wirft nie - ist das Studio gerade nicht erreichbar, zeigt die Seite einen Hinweis
    statt eines Fehlers."""
    traffic, blitzer, error = [], [], None
    try:
        response = requests.get(settings.RADIO_TRAFFIC_API_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        traffic = data.get('traffic', [])
        blitzer = data.get('blitzer', [])
    except (requests.RequestException, ValueError) as exc:
        logger.warning('Verkehrs-Übersicht-Abruf fehlgeschlagen: %s', exc)
        error = 'Die aktuellen Verkehrsdaten sind gerade nicht erreichbar. Bitte versuche es gleich erneut.'

    return render(request, 'radio/verkehr.html', {
        'traffic': traffic,
        'blitzer': blitzer,
        'error': error,
    })


def nachrichten(request):
    """Nachrichtenübersicht mit ausführlichen, von der KI im Studio geschriebenen Artikeln -
    gruppiert nach Region, wie auf der /nachrichten-Seite im Studio selbst."""
    items, error = _fetch_news()
    for item in items:
        item['slug'] = news_slug(item)

    by_region = {region: [] for region in NEWS_REGION_ORDER}
    for item in items:
        by_region.setdefault(item['region'], []).append(item)
    grouped = [
        {'region': region, 'items': by_region[region]}
        for region in NEWS_REGION_ORDER
        if by_region.get(region)
    ]

    return render(request, 'radio/nachrichten.html', {
        'grouped': grouped,
        'has_items': bool(items),
        'error': error,
    })


def nachrichten_detail(request, slug):
    """Einzelner Artikel mit eigener URL/eigenen Meta-Daten (SEO: pro Thema eine indexierbare
    Seite statt nur einer Sammelseite; GEO: strukturierte Daten + klarer Aufbau, damit
    KI-Suchsysteme den Artikel sauber zitieren können). Da die Artikel nur im Cache des Studios
    liegen (6h TTL) statt dauerhaft gespeichert zu sein, kann ein Artikel nach einiger Zeit aus
    der Rotation fallen - dann liefert die Seite bewusst 404 statt eines toten/leeren Artikels."""
    items, error = _fetch_news()

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
            ok, error = _submit_hotline_report(form.cleaned_data)
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
