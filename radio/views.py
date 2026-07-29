import logging

import requests
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render

from .forms import ContactForm
from .models import FrequencyEntry, Show

logger = logging.getLogger(__name__)


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
    context = {
        'player_embed_url': settings.RADIO_PLAYER_EMBED_URL,
    }
    return render(request, 'radio/live.html', context)


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
            form.save()
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
