from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

class UtilizadorDetalhes(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    nif = models.BigIntegerField()  # or CharField(max_length=12) if needed
    data_nascimento = models.DateField()
    saldo = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    iban = models.CharField(max_length=34, unique=True)

    def __str__(self):
        return self.nome

class Transferencia(models.Model):
    origem = models.ForeignKey(UtilizadorDetalhes, on_delete=models.CASCADE, related_name='transferencias_enviadas')
    destino = models.ForeignKey(UtilizadorDetalhes, on_delete=models.CASCADE, related_name='transferencias_recebidas')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.origem.iban} → {self.destino.iban}: {self.valor}€"

    def save(self, *args, **kwargs):
        if self.origem.saldo < self.valor:
            raise ValidationError(f"Saldo insuficiente em {self.origem.iban}")
        # Subtrai da origem e adiciona ao destino
        self.origem.saldo -= self.valor
        self.origem.save()
        self.destino.saldo += self.valor
        self.destino.save()
        super().save(*args, **kwargs)