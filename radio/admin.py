from django.contrib import admin

from .models import ContactMessage, FrequencyEntry, Show


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ('titel', 'zeitraum', 'reihenfolge')
    list_editable = ('reihenfolge',)
    ordering = ('reihenfolge',)
    search_fields = ('titel', 'beschreibung')


@admin.register(FrequencyEntry)
class FrequencyEntryAdmin(admin.ModelAdmin):
    list_display = ('ort', 'frequenz', 'empfangsart', 'reihenfolge')
    list_editable = ('reihenfolge',)
    ordering = ('reihenfolge',)
    search_fields = ('ort', 'frequenz', 'empfangsart')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'erstellt_am', 'gelesen')
    list_editable = ('gelesen',)
    list_filter = ('gelesen',)
    search_fields = ('name', 'email', 'nachricht')
    readonly_fields = ('name', 'email', 'nachricht', 'erstellt_am')
    ordering = ('-erstellt_am',)
