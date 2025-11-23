from django import forms
from .models import Atleta, Atletica
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group


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