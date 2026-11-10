
from django import forms
from django.contrib.auth.models import User
from . import models


class PerfilForm(forms.ModelForm):
    class Meta:
        model = models.Perfil
        exclude = ('usuario',)


class UserForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
        label='Senha'
    )

    password2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
        label='Confirmação Senha'
    )

    def __init__(self, usuario=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'password',
            'password2',
            'email'
        ]

    def clean(self):
        cleaned = super().clean()

        username_data = cleaned.get('username')
        password_data = cleaned.get('password')
        password2_data = cleaned.get('password2')

        if username_data:
            usuario_db = User.objects.filter(
                username=username_data
            ).exclude(pk=self.instance.pk).first()

            if usuario_db:
                self.add_error(
                    'username',
                    'Este nome de usuário já existe.'
                )

        # Cadastro de novo usuário
        if not self.usuario:
            if not password_data:
                self.add_error(
                    'password',
                    'A senha é obrigatória.'
                )

            if not password2_data:
                self.add_error(
                    'password2',
                    'Confirme sua senha.'
                )

        # Verifica se as senhas são iguais
        if password_data and password2_data:
            if password_data != password2_data:
                self.add_error(
                    'password2',
                    'As senhas não coincidem.'
                )

        return cleaned
