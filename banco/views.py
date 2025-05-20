from datetime import datetime
from decimal import Decimal
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django import forms

from .models import UtilizadorDetalhes, Transferencia
from utils.crypto import encrypt, decrypt
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
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('conta')
        else:
            return render(request, 'banco/login.html', {
                'error_message': "Nome de usuário ou senha incorretos."
            })
    return render(request, 'banco/login.html')

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
        raw_nome = request.POST.get('nome')
        raw_nif = request.POST.get('nif')
        raw_data = request.POST.get('data_nascimento')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Esse nome de usuário já está em uso.")
            return redirect('registar')

        nome_enc = encrypt(raw_nome)
        nif_enc = encrypt(raw_nif)

        user = User.objects.create_user(username=username, password=password)
        UtilizadorDetalhes.objects.create(
            user=user,
            nome=nome_enc,
            nif=nif_enc,
            data_nascimento=raw_data,
            iban=generate_unique_iban(),
        )
        messages.success(request, "Registo efetuado com sucesso!")
        return redirect('home')

    return render(request, 'banco/registar.html')

def conta_view(request):
    detalhes = get_object_or_404(UtilizadorDetalhes, user=request.user)

    nome_plain = decrypt(detalhes.nome)
    nif_plain = decrypt(detalhes.nif)

    detalhes.nome = nome_plain
    detalhes.nif = nif_plain
    detalhes.data_nascimento = detalhes.data_nascimento

    return render(request, 'banco/conta.html', {
        'detalhes': detalhes
    })

def nova_transferencia(request):
    if request.method == 'POST':
        destino_iban = request.POST.get('destino_iban')
        valor_str = request.POST.get('valor')
        try:
            valor = Decimal(valor_str)
        except:
            messages.error(request, "Valor inválido.")
            return redirect('nova_transferencia')

        try:
            origem = UtilizadorDetalhes.objects.get(user=request.user)
        except UtilizadorDetalhes.DoesNotExist:
            messages.error(request, "Erro ao encontrar seus dados.")
            return redirect('nova_transferencia')

        try:
            destino = UtilizadorDetalhes.objects.get(iban=destino_iban)
        except UtilizadorDetalhes.DoesNotExist:
            messages.error(request, "IBAN de destino não encontrado.")
            return redirect('nova_transferencia')

        if origem == destino:
            messages.error(request, "Não pode transferir para si mesmo.")
            return redirect('nova_transferencia')

        if valor <= 0:
            messages.error(request, "O valor deve ser positivo.")
            return redirect('nova_transferencia')

        if origem.saldo < valor:
            messages.error(request, "Saldo insuficiente.")
            return redirect('nova_transferencia')

        try:
            transferencia = Transferencia(origem=origem, destino=destino, valor=valor)
            transferencia.save()
            messages.success(request, "Transferência realizada com sucesso.")
            return redirect('conta')
        except ValidationError as e:
            messages.error(request, str(e))
        except Exception:
            messages.error(request, "Erro inesperado ao processar a transferência.")

    return render(request, 'banco/nova_transferencia.html')
