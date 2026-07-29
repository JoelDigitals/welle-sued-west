from django import forms

from .models import ContactMessage


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
