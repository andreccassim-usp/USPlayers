from django import forms
from .models import Atleta, Atletica, ResultadoPartida
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.forms import ModelForm


class AtletaForm(forms.ModelForm):
    class Meta:
        model = Atleta
        fields = ["nome", "ano_entrada", "atletica", "modalidade", "desempenho"]


class AtleticaForm(forms.ModelForm):
    class Meta:
        model = Atletica
        fields = ["nome", "universidade", "ano_fundacao", "descricao"]

class SignupForm(UserCreationForm):
    username = forms.CharField(max_length=64)
    email = forms.EmailField(max_length=64)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    groups = forms.ChoiceField(
    choices=[
        ("Atleta", "Atleta"),
        ("Atléticas", "Atlética"),
    ]
)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'groups']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()
        return user
    
# Seu forms.py, substituindo o bloco ResultadoPartidaForm
# forms.py

# ... (outras classes)

## forms.py

from django import forms
from django.forms import ModelForm
# Certifique-se de que ResultadoPartida e Atletica estão importados no topo
from .models import ResultadoPartida, Atletica 

class ResultadoPartidaForm(ModelForm):
    # 1. Definir as opções fixas para o campo Modalidade
    MODALIDADES_CHOICES = [
        ("Futsal Masculino", "Futsal Masculino"),
        ("Futsal Feminino", "Futsal Feminino"),
        ("Voleibol Masculino", "Voleibol Masculino"),
        ("Voleibol Feminino", "Voleibol Feminino"),
        ("Softbol", "Softbol"),
    ]
    
    # Sobrescrever o campo Modalidade para ser um Dropdown com Choices fixos
    modalidade = forms.ChoiceField(choices=MODALIDADES_CHOICES)

    class Meta:
        model = ResultadoPartida
        # Inclui todos os campos do modelo (mesmo os que serão removidos/preenchidos)
        fields = ['atletica_1', 'atletica_2', 'atletica_vencedora', 'data_partida', 'modalidade', 'registrado_por']
        
        labels = {
            'atletica_2': 'Atlética Adversária',
            'atletica_vencedora': 'Atlética Vencedora',
            'data_partida': 'Data da Partida (AAAA-MM-DD)',
        }
        
    def __init__(self, *args, **kwargs):
        # 1. Retira a variável 'dono_atletica' dos kwargs para usá-la nos filtros internos
        # Usamos 'None' como default para evitar um KeyError se o form for instanciado sem esse parâmetro
        dono_atletica = kwargs.pop('dono_atletica', None)
        
        super().__init__(*args, **kwargs)
        
        # 2. Oculta os campos que serão preenchidos automaticamente na View
        # Isso impede o usuário de manipular o dono e a Atlética 1
        if 'atletica_1' in self.fields:
             del self.fields['atletica_1']
        if 'registrado_por' in self.fields:
             del self.fields['registrado_por']
        
        # 3. Aplica o filtro de exclusão na Atlética Adversária (Atlética 2)
        if dono_atletica:
             # Garante que a Atlética 2 (Adversária) não pode ser a Atlética do dono
             self.fields['atletica_2'].queryset = Atletica.objects.exclude(pk=dono_atletica.pk)