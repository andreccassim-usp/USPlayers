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
 
class ResultadoPartidaForm(ModelForm):
    class Meta:
        model = ResultadoPartida
        # Inclui todos os campos, exceto os que serão preenchidos automaticamente/escondidos:
        # registrado_por e atletica_1 serão removidos/tratados na view, mas devem ser incluídos para validação
        fields = ['atletica_1', 'atletica_2', 'atletica_vencedora', 'data_partida', 'modalidade', 'registrado_por']
        
        labels = {
            'atletica_2': 'Atlética Adversária',
            'atletica_vencedora': 'Vencedora da Partida',
            'data_partida': 'Data da Partida (AAAA-MM-DD)',
        }
        
    def __init__(self, *args, **kwargs):
        # Chama a inicialização padrão do formulário
        super().__init__(*args, **kwargs)
        
        # Oculta campos que serão preenchidos automaticamente na view (por segurança e UX)
        # Removendo estes campos do fields original (Meta) permite que eles sejam tratados separadamente
        del self.fields['atletica_1']
        del self.fields['registrado_por']
        
        # Configurações para campos de seleção (Dropdowns)
        # Garante que Atletica 2 e Vencedora não podem ser a atlética do dono (a ser passada na view)
        
        # Filtra opções para Atletica Adversária: 
        # Exclui a atlética do dono da lista de opções (se a atlética do dono for passada no kwargs)
        if 'dono_atletica' in kwargs:
             dono_atletica = kwargs.pop('dono_atletica')
             self.fields['atletica_2'].queryset = Atletica.objects.exclude(pk=dono_atletica.pk)
             self.fields['atletica_vencedora'].queryset = Atletica.objects.all()

        # O campo 'modalidade' já é um CharField, o Django irá renderizá-lo como campo de texto.
        # Se preferir um dropdown com opções fixas, use widgets:
        # MODALIDADES = [("Futsal Masculino", "Futsal Masculino"), ...]
        # self.fields['modalidade'] = forms.ChoiceField(choices=MODALIDADES)