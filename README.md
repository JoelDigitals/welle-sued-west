# Welle Süd-West – Django-Website

Eine vollständige Django-Website für den Radiosender **Welle Süd-West**:
Startseite, Programm, Musik, Empfang, Live-Player, Über uns, Kontaktformular,
Impressum & Datenschutz – inklusive eingebettetem Webplayer und einer
"Läuft gerade"-Anzeige, die live aus der Studio-API gefüttert wird.

## Seiten

| URL              | Inhalt                                             |
|-------------------|-----------------------------------------------------|
| `/`               | Startseite mit Hero, eingebettetem Player, Vorschau |
| `/programm/`      | Kompletter Sendeplan                                |
| `/musik/`         | Musikmix / Genres                                   |
| `/empfang/`       | Frequenzen & Empfangswege                           |
| `/live/`          | Großer Live-Player, MP3-Dauerstream, Technik-Infos  |
| `/ueber-uns/`     | Über den Sender                                     |
| `/kontakt/`       | Kontaktformular (speichert Nachrichten im Admin)    |
| `/impressum/`     | Impressum (Platzhalter – bitte anpassen!)           |
| `/datenschutz/`   | Datenschutzerklärung (Platzhalter – bitte anpassen!)|
| `/admin/`         | Django-Adminbereich zur Pflege der Inhalte          |
| `/api/nowplaying/`| Interner JSON-Proxy zur Studio-API (fürs Frontend)  |

## Der Player & die Studio-Anbindung

- Der Webplayer (`https://welle-sued-west-studio.onrender.com/player`) ist als
  `<iframe>` auf der Startseite und der Live-Seite eingebettet.
- Die "Läuft gerade"-Anzeige holt sich ihre Daten **nicht** direkt vom Studio,
  sondern über die eigene Route `/api/nowplaying/`
  (siehe `radio/views.py::nowplaying_proxy`). Diese ruft serverseitig
  `https://welle-sued-west-studio.onrender.com/api/public/nowplaying` ab und
  reicht die Antwort als JSON weiter. Das vermeidet mögliche CORS-Probleme
  beim direkten Abruf aus dem Browser.
- Das JavaScript dazu liegt in `radio/static/radio/js/nowplaying.js`. Da das
  genaue JSON-Format der Studio-API beim Bau dieser Seite nicht bekannt war,
  probiert das Script mehrere gängige Feldnamen durch (`title`/`artist`,
  `song.title`/`song.artist`, `now_playing...`). **Bitte einmal
  `https://welle-sued-west-studio.onrender.com/api/public/nowplaying` im
  Browser oder mit `curl` öffnen und bei Bedarf die Feldnamen in
  `extractNowPlayingText()` anpassen.**
- Der Dauer-Stream (`.../live-stream`) ist auf der Live-Seite als direkter
  Link verlinkt (abspielbar in VLC, Radio-Apps oder als Icecast-Quelle) und
  der Metadaten-Endpunkt (`.../api/public/nowplaying`) wird dort zusätzlich
  für Sendetechnik (Icecast/Shoutcast, RDS, DAB+ Dynamic Label) angezeigt.

## Lokale Installation

```bash
# 1. Virtuelle Umgebung anlegen und aktivieren
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Abhängigkeiten installieren
pip install -r requirements.txt

# 3. Datenbank anlegen
python manage.py migrate

# 4. Beispiel-Sendungen & Empfangswege einspielen (optional, aber empfohlen)
python manage.py seed_data

# 5. Admin-Zugang anlegen
python manage.py createsuperuser

# 6. Server starten
python manage.py runserver
```

Die Seite läuft danach unter `http://127.0.0.1:8000/`,
der Admin-Bereich unter `http://127.0.0.1:8000/admin/`.

Im Admin-Bereich lassen sich **Sendungen**, **Empfangswege** und
eingegangene **Kontaktnachrichten** verwalten, ohne Code anzufassen.

## Vor dem Live-Betrieb unbedingt beachten

- `SECRET_KEY` in `wellesuedwest/settings.py` durch einen eigenen, geheimen
  Wert ersetzen (z. B. über eine Umgebungsvariable laden statt hart zu
  codieren).
- `DEBUG = False` setzen und `ALLOWED_HOSTS` auf die eigene Domain
  einschränken.
- Impressum und Datenschutzerklärung sind aktuell Platzhalter – bitte durch
  echte, rechtsverbindliche Angaben ersetzen.
- Für den Produktivbetrieb empfiehlt sich ein WSGI-Server wie `gunicorn`
  sowie `python manage.py collectstatic` für die statischen Dateien.

## Projektstruktur

```
wellesuedwest/
├── manage.py
├── requirements.txt
├── wellesuedwest/          # Projekt-Settings, URLs
└── radio/                  # Die eigentliche App
    ├── models.py            # Show, FrequencyEntry, ContactMessage
    ├── views.py             # Seiten + Now-Playing-Proxy
    ├── forms.py             # Kontaktformular
    ├── admin.py
    ├── urls.py
    ├── management/commands/seed_data.py
    ├── templates/radio/     # Alle Seiten-Templates
    └── static/radio/        # CSS & JavaScript
```
