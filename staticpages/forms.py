from django import forms
from .models import Atleta, Atletica, ResultadoPartida
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.forms import ModelForm
from datetime import date 


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
 
class ResultadoPartidaForm(forms.ModelForm):
    MODALIDADES_CHOICES = [
        ("Futsal Masculino", "Futsal Masculino"),
        ("Futsal Feminino", "Futsal Feminino"),
        ("Voleibol Masculino", "Voleibol Masculino"),
        ("Voleibol Feminino", "Voleibol Feminino"),
        ("Softbol", "Softbol"),
    ]
    
    modalidade = forms.ChoiceField(choices=MODALIDADES_CHOICES)
    class Meta:
        model = ResultadoPartida
        fields = ['atletica_2', 'atletica_vencedora', 'data_partida', 'modalidade']


    class Meta:
        model = ResultadoPartida
        fields = [
            'atletica_1',
            'atletica_2',
            'atletica_vencedora',
            'data_partida',
            'modalidade',
            'registrado_por'
        ]

        labels = {
            'atletica_2': 'Atlética Adversária',
            'atletica_vencedora': 'Vencedora da Partida',
            'data_partida': 'Data da Partida (AAAA-MM-DD)',
        }

    def __init__(self, *args, **kwargs):
        dono_atletica = kwargs.pop('dono_atletica', None)
        super().__init__(*args, **kwargs)
        
        #campos que serão preenchidos automaticamente
        del self.fields['atletica_1']
        del self.fields['registrado_por']
        

        #exclui a atlética do dono da lista de opções
        if 'dono_atletica' in kwargs:
             dono_atletica = kwargs.pop('dono_atletica')
             self.fields['atletica_2'].queryset = Atletica.objects.exclude(pk=dono_atletica.pk)
             self.fields['atletica_vencedora'].queryset = Atletica.objects.all()
    def clean_data_partida(self):
        # 1. Obtém o valor do campo data_partida
        data = self.cleaned_data.get('data_partida')
        
        # 2. Obtém a data atual (sem componente de tempo)
        hoje = date.today() 
        
        # 3. Validação: Checa se a data fornecida é futura
        if data and data > hoje:
            # Levanta uma exceção de validação que anexa o erro ao campo
            raise forms.ValidationError("Data da partida inválida: não é possível registrar resultados para o futuro.")
            
        return data