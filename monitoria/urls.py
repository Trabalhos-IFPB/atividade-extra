from django.urls import path

from .views import (
    AssumirDuvidaView,
    BaseConhecimentoView,
    DuvidaCreateView,
    DuvidaListView,
    EncerrarDuvidaView,
    HomeRedirectView,
    ResponderDuvidaView,
    SignUpView,
)

urlpatterns = [
    path('', HomeRedirectView.as_view(), name='home'),
    path('cadastro/', SignUpView.as_view(), name='signup'),
    path('duvidas/', DuvidaListView.as_view(), name='duvida-lista'),
    path('duvidas/nova/', DuvidaCreateView.as_view(), name='duvida-criar'),
    path('duvidas/<int:pk>/assumir/', AssumirDuvidaView.as_view(), name='duvida-assumir'),
    path('duvidas/<int:pk>/responder/', ResponderDuvidaView.as_view(), name='duvida-responder'),
    path('duvidas/<int:pk>/encerrar/', EncerrarDuvidaView.as_view(), name='duvida-encerrar'),
    path('base-conhecimento/', BaseConhecimentoView.as_view(), name='base-conhecimento'),
]
