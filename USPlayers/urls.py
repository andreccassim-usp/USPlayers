"""
URL configuration for USPlayers project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from staticpages import views  
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('buscar/', views.buscar, name='buscar'),
     path("atleta/<int:pk>/", views.perfil_atleta, name="perfil_atleta"),
    path("atleta/<int:pk>/editar/", views.editar_atleta, name="editar_atleta"),
    path("atletica/<int:pk>/", views.perfil_atletica, name="perfil_atletica"),
    path("atletica/<int:pk>/editar/", views.editar_atletica, name="editar_atletica"),
]
