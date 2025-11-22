from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from .models import Atleta, Atletica
from .forms import AtletaForm, AtleticaForm


# --------- PERFIS (qualquer um pode ver) ----------

def perfil_atleta(request, pk):
    atleta = get_object_or_404(Atleta, pk=pk)
    return render(request, "perfil_atleta.html", {"atleta": atleta})


def perfil_atletica(request, pk):
    atletica = get_object_or_404(Atletica, pk=pk)
    return render(request, "perfil_atletica.html", {"atletica": atletica})


# --------- EDIÇÃO (apenas dono – login virá depois) ----------

def editar_atleta(request, pk):
    atleta = get_object_or_404(Atleta, pk=pk)

    # TODO: substituir isso por autenticação real
    # Exemplo futuro:
    # if not request.user.is_authenticated or request.user != atleta.usuario:
    #     return HttpResponseForbidden("Você não pode editar este perfil.")

    if request.method == "POST":
        form = AtletaForm(request.POST, instance=atleta)
        if form.is_valid():
            form.save()
            return redirect("perfil_atleta", pk=atleta.pk)
    else:
        form = AtletaForm(instance=atleta)

    return render(request, "editar_atleta.html", {"form": form, "atleta": atleta})


def editar_atletica(request, pk):
    atletica = get_object_or_404(Atletica, pk=pk)

    # TODO: autenticação real no futuro
    # if not request.user.is_authenticated or request.user != atletica.dono:
    #     return HttpResponseForbidden("Você não pode editar esta atlética.")

    if request.method == "POST":
        form = AtleticaForm(request.POST, instance=atletica)
        if form.is_valid():
            form.save()
            return redirect("perfil_atletica", pk=atletica.pk)
    else:
        form = AtleticaForm(instance=atletica)

    return render(request, "editar_atletica.html", {"form": form, "atletica": atletica})



def index(request):
    context = {}
    return render(request, 'staticpages/index.html', context)


def about(request):
    context = {}
    return render(request, 'staticpages/about.html', context)

def comparacao(request):
    context = {}
    return render(request, 'comparacao.html', context)

def login(request):
    context = {}
    return render(request, 'login.html', context)


# PÁGINA DE BUSCA
def buscar(request):
    termo = request.GET.get('q', '')

    atletas = Atleta.objects.all()
    atleticas = Atletica.objects.all()

    if termo:
        atletas = atletas.filter(nome__icontains=termo)
        atleticas = atleticas.filter(nome__icontains=termo)

    context = {
        'termo': termo,
        'atletas': atletas,
        'atleticas': atleticas,
    }
    return render(request, 'buscar.html', context)
