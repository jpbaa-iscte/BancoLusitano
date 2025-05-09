from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registar/', views.registar_view, name='registar'),
    path('conta/', views.conta_view, name='conta'),
]
