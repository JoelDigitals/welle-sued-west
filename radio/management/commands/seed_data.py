from django.core.management.base import BaseCommand

from radio.models import FrequencyEntry, Show


class Command(BaseCommand):
    help = 'Füllt die Datenbank mit Beispiel-Sendungen und Empfangswegen.'

    def handle(self, *args, **options):
        shows = [
            (0, 'Der Südwest-Morgen', '06:00 – 10:00',
             'Guter-Laune-Start mit Kaffee, Verkehr und den größten Pop-Hits des Tages.'),
            (1, 'Mittagssonne', '10:00 – 14:00',
             'Entspannter Popmix für den Vormittag – mit offenem Fenster und Gute-Laune-Garantie.'),
            (2, 'Südwest-Popcharts', '14:00 – 18:00',
             'Die meistgehörten Songs der Region, live gezählt und gemeinsam mitgesungen.'),
            (3, 'Feierabend-Welle', '18:00 – 22:00',
             'Ruhiger Ausklang mit Pop-Balladen, Hörergeschichten und einem Gläschen Wein aus der Region.'),
            (4, 'Nachtlicht', '22:00 – 00:00',
             'Leise, warm und ehrlich – für alle, die noch wach sind und gute Musik brauchen.'),
            (5, 'Südwest am Sonntag', 'Wochenende',
             'Brunch-Playlist, Gartentipps und der große Rückblick auf die Woche.'),
        ]
        for reihenfolge, titel, zeitraum, beschreibung in shows:
            Show.objects.get_or_create(
                titel=titel,
                defaults={
                    'zeitraum': zeitraum,
                    'beschreibung': beschreibung,
                    'reihenfolge': reihenfolge,
                },
            )

        frequencies = [
            (0, 'Saarbrücken', '98.5', 'UKW'),
            (1, 'Trier', '97.2', 'UKW'),
            (2, 'Kaiserslautern', '95.8', 'UKW'),
            (3, 'Karlsruhe', '101.3', 'UKW'),
            (4, 'Freiburg', '99.6', 'UKW'),
            (5, 'Überall im Südwesten', 'Kanal 9C', 'Digitalradio (DAB+)'),
            (6, 'Weltweit', 'App & Web', 'Live-Stream'),
        ]
        for reihenfolge, ort, frequenz, empfangsart in frequencies:
            FrequencyEntry.objects.get_or_create(
                ort=ort,
                defaults={
                    'frequenz': frequenz,
                    'empfangsart': empfangsart,
                    'reihenfolge': reihenfolge,
                },
            )

        self.stdout.write(self.style.SUCCESS(
            'Beispieldaten für Sendungen und Empfangswege wurden angelegt.'
        ))
