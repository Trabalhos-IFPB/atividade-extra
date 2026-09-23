from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Disciplina, Duvida


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username',)


class DuvidaCreateForm(forms.ModelForm):
    class Meta:
        model = Duvida
        fields = ('titulo', 'descricao', 'disciplina')
        widgets = {'descricao': forms.Textarea(attrs={'rows': 5})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['disciplina'].queryset = Disciplina.objects.filter(ativa=True).order_by('nome')


class RespostaForm(forms.ModelForm):
    class Meta:
        model = Duvida
        fields = ('resposta',)
        widgets = {'resposta': forms.Textarea(attrs={'rows': 5})}

    def clean_resposta(self):
        resposta = self.cleaned_data['resposta']
        if not resposta.strip():
            raise forms.ValidationError('A resposta não pode ficar em branco.')
        return resposta
