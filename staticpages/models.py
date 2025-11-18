from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from django.db import models
class Atletica(models.Model):
    nome = models.CharField(max_length=100)
    universidade = models.CharField(max_length=100, blank=True)
    ano_fundacao = models.PositiveIntegerField(null=True, blank=True)
    descricao = models.TextField(blank=True)

    # dono da página (quem poderá editar quando o login existir)
    dono = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="atleticas",
        null=True,
        blank=True,   # por enquanto opcional
    )

    def __str__(self):
        return self.nome

class Atleta(models.Model):
    # no futuro: ligar com a conta do usuário
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="perfil_atleta",
        null=True,
        blank=True,
    )

    nome = models.CharField(max_length=100)
    ano_entrada = models.PositiveIntegerField()
    atletica = models.ForeignKey(
        Atletica,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="atletas",
    )
    modalidade = models.CharField(max_length=100)
    desempenho = models.TextField(
        blank=True,
        help_text="Descrição de desempenho que o atleta pode escrever.",
    )

    def __str__(self):
        return self.nome
