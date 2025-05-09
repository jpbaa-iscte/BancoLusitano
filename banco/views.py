from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Utilizador
from .forms import RegistoForm
from django import forms
from .models import Transferencia

def home(request):
    return render(request, 'banco/home.html')

class TransferenciaForm(forms.Form):
    iban_destino = forms.CharField(max_length=25)
    valor = forms.DecimalField(max_digits=10, decimal_places=2)

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('conta')
        else:
            messages.error(request, "Email ou palavra-passe inválidos.")
    return render(request, 'banco/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def registar_view(request):
    if request.method == 'POST':
        form = RegistoForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # protege a password
            user.save()
            login(request, user)
            return redirect('home')  # redireciona após criar conta
    else:
        form = RegistoForm()
    return render(request, 'banco/registar.html', {'form': form})

def conta_view(request):
    # Simulação de autenticação — normalmente usarias request.user
    utilizador_id = request.session.get('utilizador_id')  # ou como estás a armazenar o login
    if not utilizador_id:
        return redirect('login')  # Redireciona para login se não estiver autenticado

    utilizador = Utilizador.objects.get(id=utilizador_id)

    if request.method == 'POST':
        form = TransferenciaForm(request.POST)
        if form.is_valid():
            transferencia = form.save(commit=False)
            transferencia.origem = utilizador

            if transferencia.valor > utilizador.saldo:
                messages.error(request, 'Saldo insuficiente.')
            elif transferencia.destino == utilizador:
                messages.error(request, 'Não pode transferir para si mesmo.')
            else:
                # Atualiza saldos
                utilizador.saldo -= transferencia.valor
                transferencia.destino.saldo += transferencia.valor
                utilizador.save()
                transferencia.destino.save()
                transferencia.save()
                messages.success(request, 'Transferência realizada com sucesso.')
                return redirect('conta')
    else:
        form = TransferenciaForm()

    transferencias = Transferencia.objects.filter(origem=utilizador)

    context = {
        'utilizador': utilizador,
        'form': form,
        'transferencias': transferencias
    }
    return render(request, 'banco/conta.html', context)
