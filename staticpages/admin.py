from django.contrib import admin
from .models import Atleta, Atletica, ResultadoPartida

@admin.register(Atleta)
class AtletaAdmin(admin.ModelAdmin):
    list_display = ("nome", "ano_entrada", "atletica", "modalidade")
    search_fields = ("nome", "modalidade", "atletica__nome")


@admin.register(Atletica)
class AtleticaAdmin(admin.ModelAdmin):
    list_display = ("nome", "universidade", "ano_fundacao")
    search_fields = ("nome", "universidade")

admin.site.register(ResultadoPartida)
