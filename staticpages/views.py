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

#@login_required
#def registrar_partida(request, pk):
#    dono_atletica = get_object_or_404(Atletica, pk=pk)
 #   if request.user != dono_atletica.dono:
  #      return HttpResponseForbidden("Você não tem permissão para adicionar resultados para esta atlética.")
   # if request.method == 'POST':
    #    form = ResultadoPartidaForm(request.POST, dono_atletica=dono_atletica)
     #   if form.is_valid():
      #      resultado = form.save(commit=False)
       #     resultado.registrado_por = request.user
        #    resultado.atletica_1 = dono_atletica
         #   if resultado.atletica_1.pk == resultado.atletica_2.pk:
          #      form.add_error(None, "Atlética Adversária não pode ser a própria atlética.")
           #     return render(request, 'registrar_partida.html', {'form': form, 'atletica': dono_atletica})
#            #resultado.save()
 #           return redirect('perfil_atletica', pk=dono_atletica.pk)
  #  else:
   #     form = ResultadoPartidaForm(dono_atletica=dono_atletica)
 #   return render(request, 'registrar_partida.html', {'form': form, 'atletica': dono_atletica})
 # Seu views.py, substituindo o bloco registrar_partida
# views.py

# Adicione esta importação no topo:
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.urls import reverse_lazy # Para usar a URL de redirecionamento no sucesso

# ... (outras views)

class RegistrarPartidaView(LoginRequiredMixin, CreateView):
    # Modelo a ser usado
    model = ResultadoPartida
    
    # Formulário customizado
    form_class = ResultadoPartidaForm 
    
    # Template para renderizar o formulário
    template_name = 'criar_resultado.html' 
    
    # URL de redirecionamento após sucesso (usaremos o método get_success_url)
    success_url = reverse_lazy('index') 

    # Sobrescreve para injetar a atlética do dono no formulário (para filtros)
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        pk = self.kwargs.get('pk')
        dono_atletica = get_object_or_404(Atletica, pk=pk)
        kwargs['dono_atletica'] = dono_atletica
        kwargs['atletica'] = dono_atletica # Passa a atlética para o contexto do template
        return kwargs
    
    # Sobrescreve para passar a atlética para o contexto de renderização
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        context['atletica'] = get_object_or_404(Atletica, pk=pk)
        return context

    # 🚨 LÓGICA DE AUTOMAÇÃO E SEGURANÇA (POST)
    def form_valid(self, form):
        pk = self.kwargs.get('pk')
        dono_atletica = get_object_or_404(Atletica, pk=pk)

        # 1. AUTORIZAÇÃO: Verifica se o usuário logado é o dono
        if self.request.user != dono_atletica.dono:
            # Não é a maneira mais limpa de bloquear, mas garante segurança
            return HttpResponseForbidden("Você não tem permissão para registrar resultados para esta atlética.")

        # 2. ATRIBUIÇÃO AUTOMÁTICA
        resultado = form.save(commit=False)
        resultado.registrado_por = self.request.user
        resultado.atletica_1 = dono_atletica
        
        # 3. VALIDAÇÃO EXTRA (se a lógica de forms não pegar)
        if resultado.atletica_1.pk == resultado.atletica_2.pk:
             form.add_error(None, "Atlética Adversária não pode ser a própria atlética.")
             return self.form_invalid(form) # Retorna erro
        
        resultado.save()
        return super().form_valid(form)

    # 4. Define o redirecionamento para o perfil da atlética recém-editada
    def get_success_url(self):
        pk = self.kwargs.get('pk')
        return reverse('perfil_atletica', kwargs={'pk': pk})