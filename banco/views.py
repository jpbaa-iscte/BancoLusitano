from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UtilizadorDetalhes
from django import forms
from .models import Transferencia
from django.utils.crypto import get_random_string

def home(request):
    return render(request, 'banco/home.html')

class TransferenciaForm(forms.Form):
    iban_destino = forms.CharField(max_length=25)
    valor = forms.DecimalField(max_digits=10, decimal_places=2)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Autenticar o usuário
        user = authenticate(request, username=username, password=password)

        if user is not None:  # Usuário autenticado com sucesso
            login(request, user)  # Faz login do usuário
            return redirect('conta')  # Redireciona para a página da conta
        else:
            error_message = "Nome de usuário ou senha incorretos."
            return render(request, 'banco/login.html', {'error_message': error_message})
    return render(request, 'banco/login.html')  # Exibe a tela de login

def logout_view(request):
    logout(request)
    return redirect('home')

def generate_unique_iban():
    while True:
        iban = 'PT50' + get_random_string(25, allowed_chars='0123456789')
        if not UtilizadorDetalhes.objects.filter(iban=iban).exists():
            return iban

def registar_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        nome = request.POST.get('nome')
        nif = request.POST.get('nif')
        data_nascimento = request.POST.get('data_nascimento')

        user = User.objects.create_user(username=username, password=password)

        UtilizadorDetalhes.objects.create(
            user=user,
            nome=nome,
            nif=nif,
            data_nascimento=data_nascimento,
            iban=generate_unique_iban(),
        )

        return redirect('home')

    return render(request, 'banco/registar.html')

def conta_view(request):
    detalhes = get_object_or_404(UtilizadorDetalhes, user=request.user)
    return render(request, 'banco/conta.html',  {'detalhes': detalhes})
