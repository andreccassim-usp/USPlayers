from django.db import models

# Create your models here.
from django.db import models

class Atletica(models.Model):
    nome = models.CharField(max_length=100)
    curso = models.CharField(max_length=100, blank=True)
    universidade = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome


class Atleta(models.Model):
    nome = models.CharField(max_length=100)
    esporte = models.CharField(max_length=100)
    curso = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)

    # opcional: relacionar com uma atlética
    atletica = models.ForeignKey(
        Atletica,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='atletas'
    )

    def __str__(self):
        return self.nome
