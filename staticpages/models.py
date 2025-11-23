from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Atletica(models.Model):
    nome = models.CharField(max_length=100)
    universidade = models.CharField(max_length=100, blank=True)
    ano_fundacao = models.PositiveIntegerField(null=True, blank=True)
    descricao = models.TextField(blank=True)

    # Dono da página (controle de edição)
    dono = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="atleticas",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.nome


class Atleta(models.Model):
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


class ResultadoPartida(models.Model):
    atletica_1 = models.ForeignKey(
        Atletica,
        on_delete=models.CASCADE,
        related_name="partidas_como_1",
        verbose_name="Atlética 1",
    )
    atletica_2 = models.ForeignKey(
        Atletica,
        on_delete=models.CASCADE,
        related_name="partidas_como_2",
        verbose_name="Atlética 2",
    )
    atletica_vencedora = models.ForeignKey(
        Atletica,
        on_delete=models.CASCADE,
        related_name="vitorias",
        verbose_name="Atlética Vencedora",
    )

    data_partida = models.DateField(default=timezone.now)
    modalidade = models.CharField(max_length=100)

    registrado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="atleticas_diferentes",
                check=~models.Q(atletica_1=models.F("atletica_2")),
            )
        ]

    def __str__(self):
        return (
            f"{self.atletica_vencedora.nome} venceu "
            f"{self.atletica_1.nome} vs {self.atletica_2.nome} "
            f"({self.modalidade})"
        )
