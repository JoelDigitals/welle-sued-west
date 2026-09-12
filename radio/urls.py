from django.urls import path

from . import views

app_name = 'radio'

urlpatterns = [
    path('', views.home, name='home'),
    path('programm/', views.programm, name='programm'),
    path('musik/', views.musik, name='musik'),
    path('empfang/', views.empfang, name='empfang'),
    path('live/', views.live, name='live'),
    path('verkehr/', views.verkehr, name='verkehr'),
    path('hotline/', views.hotline, name='hotline'),
    path('werbung/', views.werbung, name='werbung'),
    path('ueber-uns/', views.ueber_uns, name='ueber_uns'),
    path('kontakt/', views.kontakt, name='kontakt'),
    path('impressum/', views.impressum, name='impressum'),
    path('datenschutz/', views.datenschutz, name='datenschutz'),

    # JSON-Endpunkt, den das Frontend per JavaScript abfragt
    path('api/nowplaying/', views.nowplaying_proxy, name='nowplaying_proxy'),
]
