from django.db import models


class Show(models.Model):
    """Eine Sendung im Programm (z. B. 'Der Südwest-Morgen', 06:00-10:00)."""

    titel = models.CharField('Titel', max_length=120)
    zeitraum = models.CharField(
        'Uhrzeit', max_length=60,
        help_text='z. B. "06:00 – 10:00" oder "Wochenende"'
    )
    beschreibung = models.TextField('Beschreibung', blank=True)
    reihenfolge = models.PositiveIntegerField(
        'Reihenfolge', default=0,
        help_text='Kleinere Zahl = weiter oben in der Liste'
    )

    class Meta:
        verbose_name = 'Sendung'
        verbose_name_plural = 'Sendungen'
        ordering = ['reihenfolge', 'id']

    def __str__(self):
        return f'{self.titel} ({self.zeitraum})'


class FrequencyEntry(models.Model):
    """Ein Empfangsweg an einem Ort (UKW, DAB+, App & Web ...)."""

    ort = models.CharField('Ort', max_length=120)
    frequenz = models.CharField(
        'Frequenz / Kanal', max_length=60,
        help_text='z. B. "98.5", "Kanal 9C" oder "App & Web"'
    )
    empfangsart = models.CharField('Empfangsart', max_length=120)
    reihenfolge = models.PositiveIntegerField('Reihenfolge', default=0)

    class Meta:
        verbose_name = 'Empfangsweg'
        verbose_name_plural = 'Empfangswege'
        ordering = ['reihenfolge', 'id']

    def __str__(self):
        return f'{self.ort} – {self.frequenz}'


class ContactMessage(models.Model):
    """Eine über das Kontaktformular eingegangene Nachricht."""

    name = models.CharField('Name', max_length=120)
    email = models.EmailField('E-Mail')
    nachricht = models.TextField('Nachricht')
    erstellt_am = models.DateTimeField('Eingegangen am', auto_now_add=True)
    gelesen = models.BooleanField('Gelesen', default=False)

    class Meta:
        verbose_name = 'Kontaktnachricht'
        verbose_name_plural = 'Kontaktnachrichten'
        ordering = ['-erstellt_am']

    def __str__(self):
        return f'{self.name} ({self.erstellt_am:%d.%m.%Y %H:%M})'
