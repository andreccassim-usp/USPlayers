from django.shortcuts import render, get_object_or_404, redirect
from .models import Atleta, Atletica
from django import forms


def index(request):
    context = {}
    return render(request, 'staticpages/index.html', context)


def about(request):
    context = {}
    return render(request, 'staticpages/about.html', context)

# FORMULÁRIOS (vamos usar depois nos perfis)
def perfil_atleta(request, pk):
    atleta = get_object_or_404(Atleta, pk=pk)

    if request.method == 'POST':
        form = AtletaForm(request.POST, instance=atleta)
        if form.is_valid():
            form.save()
            return redirect('perfil_atleta', pk=atleta.pk)
    else:
        form = AtletaForm(instance=atleta)

    return render(request, 'perfil_atleta.html', {'form': form, 'atleta': atleta})


def perfil_atletica(request, pk):
    atletica = get_object_or_404(Atletica, pk=pk)

    if request.method == 'POST':
        form = AtleticaForm(request.POST, instance=atletica)
        if form.is_valid():
            form.save()
            return redirect('perfil_atletica', pk=atletica.pk)
    else:
        form = AtleticaForm(instance=atletica)

    return render(request, 'perfil_atletica.html', {'form': form, 'atletica': atletica})


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
