from django.urls import path

from . import views

urlpatterns = [
    path('about/', views.about, name='about'),
    path('', views.index, name='index'),
    path('buscar/', views.buscar, name='buscar'),
    path('comparacao/', views.comparacao, name='comparacao'),
    path('atleta/<int:pk>/', views.perfil_atleta, name='perfil_atleta'),
    path('atletica/<int:pk>/', views.perfil_atletica, name='perfil_atletica'),
    path('signup/', views.signup, name='signup'),
    path('criar-atleta/', views.criar_atleta, name='criar_atleta'),
    path('criar-atletica/', views.criar_atletica, name='criar_atletica'),
    # urls.py
# Mude esta linha:
    path('atletica/<int:pk>/adicionar_resultado/', views.RegistrarPartidaView.as_view(), name='registrar_partida_clean'),
]