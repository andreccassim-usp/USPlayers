from django.urls import path

from . import views

urlpatterns = [
    path('about/', views.about, name='about'),
    path('', views.index, name='index'),
    path('buscar/', views.buscar, name='buscar'),
    path('comparacao/', views.comparacao, name='comparacao'),
    path('login/', views.login, name='login'),
    path('atleta/<int:pk>/', views.perfil_atleta, name='perfil_atleta'),
    path('atletica/<int:pk>/', views.perfil_atletica, name='perfil_atletica'),
]