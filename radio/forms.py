from django import forms

from .models import ContactMessage


# Muss exakt zum Schema von /api/public/hotline im Studio passen (siehe
# src/routes/api/public/hotline.ts im welle-sued-west-studio-Repo).
HOTLINE_TYPES = [
    ('verkehr', 'Verkehr (Stau, Unfall, Sperrung)'),
    ('blitzer', 'Blitzer'),
    ('wetter', 'Wetter'),
    ('gruss', 'Grüße'),
    ('musikwunsch', 'Musikwunsch'),
    ('lob_kritik', 'Lob & Kritik'),
    ('sonstiges', 'Sonstiges'),
]

HOTLINE_REGIONS = [
    ('Saarland', 'Saarland'),
    ('Rheinland-Pfalz', 'Rheinland-Pfalz'),
]


class HotlineForm(forms.Form):
    type = forms.ChoiceField(
        choices=HOTLINE_TYPES, label='Was möchtest du melden?',
        widget=forms.Select(attrs={'class': 'field-input'}),
    )
    region = forms.ChoiceField(
        choices=HOTLINE_REGIONS, label='Region',
        widget=forms.Select(attrs={'class': 'field-input'}),
    )
    place = forms.CharField(
        label='Ort', max_length=80, required=False,
        widget=forms.TextInput(attrs={'class': 'field-input', 'placeholder': 'z. B. Saarbrücken'}),
    )
    road = forms.CharField(
        label='Straße / Autobahn', max_length=40, required=False,
        widget=forms.TextInput(attrs={'class': 'field-input', 'placeholder': 'z. B. A6'}),
    )
    # Bei Blitzer optional: der Ort allein reicht inzwischen (siehe blitzerOrtPhrase im Studio -
    # die Nachricht selbst fließt dort gar nicht mehr in die Ansage ein), eine leere Nachricht wird
    # in der View durch einen Platzhalter ersetzt, bevor sie ans Studio geht.
    message = forms.CharField(
        label='Nachricht', max_length=400, required=False,
        widget=forms.Textarea(attrs={'class': 'field-input', 'rows': 5}),
    )
    caller = forms.CharField(
        label='Dein Name', max_length=60, required=False,
        widget=forms.TextInput(attrs={'class': 'field-input', 'placeholder': 'Optional'}),
    )
    contact = forms.CharField(
        label='Rückruf-Kontakt', max_length=120, required=False,
        widget=forms.TextInput(attrs={'class': 'field-input', 'placeholder': 'Optional, z. B. Telefon oder E-Mail'}),
    )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('type') in ('verkehr', 'blitzer') and len(cleaned.get('place', '')) < 2:
            self.add_error('place', 'Bitte Ort angeben.')
        # Nur bei Blitzer optional (siehe message-Feld oben) - bei allen anderen Meldungsarten
        # bleibt eine echte Nachricht Pflicht, sonst gibt es inhaltlich nichts zu melden.
        if cleaned.get('type') != 'blitzer' and not cleaned.get('message', '').strip():
            self.add_error('message', 'Bitte eine Nachricht angeben.')
        return cleaned


# Muss exakt zum Schema von /api/public/ad-requests im Studio passen (siehe
# src/routes/api/public/ad-requests.ts im welle-sued-west-studio-Repo).
class WerbungForm(forms.Form):
    advertiser = forms.CharField(
        label='Firma / Werbekunde', min_length=2, max_length=80,
        widget=forms.TextInput(attrs={'class': 'field-input', 'placeholder': 'z. B. Autohaus Kern, Neunkirchen'}),
    )
    contact = forms.CharField(
        label='Kontakt', max_length=120, required=False,
        widget=forms.TextInput(attrs={'class': 'field-input', 'placeholder': 'E-Mail oder Telefon'}),
    )
    text = forms.CharField(
        label='Spot-Text', min_length=10, max_length=600,
        widget=forms.Textarea(attrs={
            'class': 'field-input', 'rows': 6,
            'placeholder': 'Werbetext, den unsere KI-Stimme sprechen soll…',
        }),
    )
    per_hour = forms.IntegerField(
        label='Gewünschte Spots pro Stunde', min_value=1, max_value=4, initial=1,
        widget=forms.NumberInput(attrs={'class': 'field-input'}),
    )


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'nachricht']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'field-input',
                'placeholder': 'Dein Name',
                'autocomplete': 'name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'field-input',
                'placeholder': 'deine@email.de',
                'autocomplete': 'email',
            }),
            'nachricht': forms.Textarea(attrs={
                'class': 'field-input',
                'placeholder': 'Was möchtest du uns sagen?',
                'rows': 6,
            }),
        }
        labels = {
            'name': 'Name',
            'email': 'E-Mail',
            'nachricht': 'Nachricht',
        }
