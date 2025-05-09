from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone


class UtilizadorManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O email é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class Utilizador(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    nif = models.CharField(max_length=12)
    saldo = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    iban = models.CharField(max_length=34, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UtilizadorManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome', 'data_nascimento', 'nif']

    def __str__(self):
        return self.email

class Transferencia(models.Model):
    origem = models.ForeignKey(Utilizador, on_delete=models.CASCADE, related_name='transferencias_enviadas')
    destino = models.ForeignKey(Utilizador, on_delete=models.CASCADE, related_name='transferencias_recebidas')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.origem.email} → {self.destino.email}: €{self.valor}'

