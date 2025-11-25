from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from .models import Atleta, Atletica, ResultadoPartida
from .forms import AtletaForm, AtleticaForm, SignupForm, ResultadoPartidaForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth import login
from django.db.models import Q 
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.core import serializers
from django.contrib.auth.models import Group
from django.views.decorators.csrf import ensure_csrf_cookie

# --------- PERFIS (qualquer um pode ver) ----------
def index(request):
    context = {}
    return render(request, 'staticpages/index.html', context)


def about(request):
    context = {}
    return render(request, 'staticpages/about.html', context)



def buscar(request):
    return render(request, 'buscar.html')

def perfil_atleta(request, pk):
    atleta = get_object_or_404(Atleta, pk=pk)
    return render(request, "perfil_atleta.html", {"atleta": atleta})


def perfil_atletica(request, pk):
    atletica = get_object_or_404(Atletica, pk=pk)
    return render(request, "perfil_atletica.html", {"atletica": atletica})




@login_required
def editar_atleta(request, pk):
    atleta = get_object_or_404(Atleta, pk=pk)

    # segurança: só o dono do perfil pode editar
    if request.user != atleta.usuario:
        return HttpResponse("Você não pode editar o perfil de outro usuário.", status=403)

    if request.method == "POST":
        form = AtletaForm(request.POST, instance=atleta)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("perfil_atleta", args=[pk]))
    else:
        form = AtletaForm(instance=atleta)

    return render(request, "editar_atleta.html", {"form": form, "atleta": atleta})

@login_required
def editar_atletica(request, pk):
    atletica = get_object_or_404(Atletica, pk=pk)

    # Agora usando o campo CERTO do model:
    if atletica.dono and request.user != atletica.dono:
        return HttpResponse("Você não pode editar esta atlética")

    if request.method == "POST":
        form = AtleticaForm(request.POST, instance=atletica)
        if form.is_valid():
            form.save()
            return redirect("perfil_atletica", pk=pk)
    else:
        form = AtleticaForm(instance=atletica)

    return render(request, "editar_atletica.html", {"form": form, "atletica": atletica})


# PÁGINA DE BUSCA
def buscar_api(request):
    """
    Endpoint GET ?q=texto -> retorna JSON com atletas e atleticas que
    contêm 'q' no nome (case-insensitive).
    """
    q = request.GET.get('q', '').strip()
    atletas_qs = Atleta.objects.none()
    atleticas_qs = Atletica.objects.none()

    if q:
        atletas_qs = Atleta.objects.filter(nome__icontains=q).values(
            'pk', 'nome', 'modalidade', 'atletica__nome'
        )
        atleticas_qs = Atletica.objects.filter(nome__icontains=q).values(
            'pk', 'nome', 'universidade'
        )

    # transformar em listas para JSON
    atletas = list(atletas_qs)
    atleticas = list(atleticas_qs)

    return JsonResponse({'atletas': atletas, 'atleticas': atleticas})


@ensure_csrf_cookie
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save()

            group_name = form.cleaned_data['groups']  # string

            # busca o objeto Group
            try:
                group = Group.objects.get(name=group_name)
            except Group.DoesNotExist:
                form.add_error('groups', "Grupo não encontrado.")
                return render(request, 'signup.html', {'form': form})

            # adiciona o grupo ao usuário
            user.groups.add(group)

            # login automático
            login(request, user)

            # redirecionamento
            if group_name == "Atléticas":
                return redirect("criar_atletica")
            else:
                return redirect("criar_atleta")
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})
def comparacao(request):

    MODALIDADES = [
        "Futsal Masculino", "Futsal Feminino", 
        "Voleibol Masculino", "Voleibol Feminino", "Softbol"
    ]
    atleticas_disponiveis = Atletica.objects.all().order_by('nome')
    
    context = {
        'atleticas_disponiveis': atleticas_disponiveis,
        'modalidades_disponiveis': MODALIDADES,
        'resultado_comparacao': None,
        'mensagem_erro': None,
        'modalidade_selecionada': None,
    }

    atletica_id_1 = request.GET.get('atletica_1')
    atletica_id_2 = request.GET.get('atletica_2')
    modalidade_selecionada = request.GET.get('modalidade')

    context['modalidade_selecionada'] = modalidade_selecionada

    if atletica_id_1 and atletica_id_2 and modalidade_selecionada:
        try:
            atletica_1 = get_object_or_404(Atletica, pk=atletica_id_1)
            atletica_2 = get_object_or_404(Atletica, pk=atletica_id_2)
            
            if atletica_1.pk == atletica_2.pk:
                context['mensagem_erro'] = "Selecione duas atléticas diferentes."
                return render(request, 'comparacao.html', context)
            
            data_limite = timezone.now().date() - timedelta(days=2 * 365) #filtra os resultados dos últimos 2 anos 

            filtro_confronto = (
                (Q(atletica_1=atletica_1) & Q(atletica_2=atletica_2)) | 
                (Q(atletica_1=atletica_2) & Q(atletica_2=atletica_1))
            )

            confrontos_relevantes = ResultadoPartida.objects.filter(
                filtro_confronto,
                data_partida__gte=data_limite, # __gte é  a mesma coisa que >= 
                modalidade=modalidade_selecionada,
            )

            vitorias_1 = confrontos_relevantes.filter(atletica_vencedora=atletica_1).count()
            vitorias_2 = confrontos_relevantes.filter(atletica_vencedora=atletica_2).count()
          
            if vitorias_1 > vitorias_2:
                vencedora = atletica_1
                perdedora = atletica_2
            elif vitorias_2 > vitorias_1:
                vencedora = atletica_2
                perdedora = atletica_1
            else: #empate
                context['mensagem_erro'] = "Empate nos últimos 2 anos ou histórico de confrontos insuficiente."
                return render(request, 'comparacao.html', context)

            context['resultado_comparacao'] = {
                'vencedora': vencedora.nome,
                'vitorias_vencedora': max(vitorias_1, vitorias_2),
                'perdedora': perdedora.nome,
                'vitorias_perdedora': min(vitorias_1, vitorias_2),
            }

        except Atletica.DoesNotExist:
            context['mensagem_erro'] = "Uma das atléticas selecionadas não existe."
        except Exception as e:
             context['mensagem_erro'] = f"Ocorreu um erro ao processar a comparação: {e}"
            

    return render(request, 'comparacao.html', context)



@login_required
def criar_atleta(request):
    if request.method == "POST":
        form = AtletaForm(request.POST)
        if form.is_valid():
            atleta = form.save(commit=False)
            atleta.usuario = request.user  # vincula o dono
            atleta.save()
            return redirect("perfil_atleta", pk=atleta.pk)
    else:
        form = AtletaForm()

    return render(request, "criar_atleta.html", {"form": form})

@login_required
def criar_atletica(request):
    if request.method == "POST":
        form = AtleticaForm(request.POST)
        if form.is_valid():
            atletica = form.save(commit=False)
            atletica.dono = request.user
            atletica.save()
            return redirect("perfil_atletica", pk=atletica.pk)
    else:
        form = AtleticaForm()

    return render(request, "criar_atletica.html", {"form": form})


# Adicione esta importação no topo:
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.urls import reverse_lazy # Para usar a URL de redirecionamento no sucesso

# ... (outras views)
@login_required 
def adicionar_resultado(request, pk):
    # 1. AUTORIZAÇÃO: Verifica se o usuário logado é o dono da atlética (pk)
    dono_atletica = get_object_or_404(Atletica, pk=pk)
    
    # Restrição de acesso: Apenas o dono pode adicionar resultados para esta atlética
    if request.user != dono_atletica.dono:
        return HttpResponseForbidden("Você não tem permissão para adicionar resultados para esta atlética.")
    
    # O objeto 'dono_atletica' será passado para o formulário para filtrar as opções
    
    if request.method == 'POST':
        # 2. PROCESSAMENTO POST: Recebe dados do formulário
        form = ResultadoPartidaForm(request.POST, dono_atletica=dono_atletica) 
        
        if form.is_valid():
            # Cria a instância do modelo, mas não salva no banco ainda (commit=False)
            resultado = form.save(commit=False) 
            
            # 3. ATRIBUIÇÃO AUTOMÁTICA E IMUTÁVEL (os dados mais sensíveis)
            
            # a) Registrado por: Preenche com o ID do usuário logado
            resultado.registrado_por = request.user
            
            # b) Atlética 1: Preenche com a atlética do dono (que não estava visível no form)
            resultado.atletica_1 = dono_atletica 
            
            # Verifica se o resultado é válido (se Atletica 1 não é igual a Atletica 2 e Atletica Vencedora é uma das duas)
            # O clean do form ou as constraints do model devem lidar com isso, mas é uma boa prática garantir:
            if resultado.atletica_1.pk == resultado.atletica_2.pk:
                form.add_error(None, "Atlética Adversária não pode ser a própria atlética.")
                return render(request, 'criar_resultado.html', {'form': form, 'atletica': dono_atletica})
            
            resultado.save() # Salva a instância completa no banco
            
            # 4. REDIRECIONAMENTO: Volta para o perfil da atlética
            return redirect('perfil_atletica', pk=dono_atletica.pk)
            
    else:
        # 5. CARREGAMENTO GET: Cria um formulário vazio
        form = ResultadoPartidaForm(dono_atletica=dono_atletica)

    # Renderiza o template de criação
    return render(request, 'criar_resultado.html', {'form': form, 'atletica': dono_atletica})