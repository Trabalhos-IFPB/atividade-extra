from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView, ListView, RedirectView, UpdateView

from .forms import DuvidaCreateForm, RespostaForm, SignUpForm
from .models import Duvida


class HomeRedirectView(RedirectView):
    pattern_name = 'duvida-lista'


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'monitoria/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        grupo, _ = Group.objects.get_or_create(name='Aluno')
        self.object.groups.add(grupo)
        return response


class DuvidaListView(LoginRequiredMixin, ListView):
    model = Duvida
    template_name = 'monitoria/duvida_list.html'
    context_object_name = 'duvidas'

    def get_queryset(self):
        user = self.request.user
        base_qs = Duvida.objects.select_related('disciplina', 'autor', 'monitor_responsavel').prefetch_related(
            'disciplina__monitores'
        )
        if user.groups.filter(name='Professor').exists():
            return base_qs
        if user.groups.filter(name='Aluno').exists():
            return base_qs.filter(autor=user)
        return base_qs.filter(disciplina__monitores=user).distinct()


class DuvidaCreateView(LoginRequiredMixin, CreateView):
    model = Duvida
    form_class = DuvidaCreateForm
    template_name = 'monitoria/duvida_form.html'
    success_url = reverse_lazy('duvida-lista')

    def form_valid(self, form):
        form.instance.autor = self.request.user
        form.instance.situacao = Duvida.Situacao.ABERTA
        messages.success(self.request, 'Dúvida aberta com sucesso.')
        return super().form_valid(form)


class AssumirDuvidaView(LoginRequiredMixin, View):
    def post(self, request, pk):
        duvida = get_object_or_404(Duvida.objects.select_related('disciplina'), pk=pk)
        if not duvida.disciplina.monitores.filter(pk=request.user.pk).exists():
            raise PermissionDenied
        if duvida.situacao != Duvida.Situacao.ABERTA or duvida.monitor_responsavel_id is not None:
            messages.error(request, 'Esta dúvida não pode mais ser assumida.')
            return redirect('duvida-lista')
        duvida.monitor_responsavel = request.user
        duvida.situacao = Duvida.Situacao.EM_ATENDIMENTO
        duvida.save(update_fields=['monitor_responsavel', 'situacao', 'atualizacao_em'])
        messages.success(request, 'Atendimento assumido com sucesso.')
        return redirect('duvida-lista')


class ResponderDuvidaView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Duvida
    form_class = RespostaForm
    template_name = 'monitoria/responder_duvida.html'
    success_url = reverse_lazy('duvida-lista')

    def test_func(self):
        duvida = self.get_object()
        return duvida.pode_responder(self.request.user)

    def handle_no_permission(self):
        raise PermissionDenied

    def form_valid(self, form):
        form.instance.situacao = Duvida.Situacao.RESPONDIDA
        messages.success(self.request, 'Resposta registrada com sucesso.')
        return super().form_valid(form)


class EncerrarDuvidaView(LoginRequiredMixin, View):
    def post(self, request, pk):
        duvida = get_object_or_404(Duvida, pk=pk)
        if duvida.autor_id != request.user.id:
            raise PermissionDenied
        if not duvida.pode_encerrar(request.user):
            messages.error(request, 'Esta dúvida ainda não pode ser encerrada.')
            return redirect('duvida-lista')
        duvida.situacao = Duvida.Situacao.ENCERRADA
        duvida.save(update_fields=['situacao', 'atualizacao_em'])
        messages.success(request, 'Dúvida encerrada com sucesso.')
        return redirect('duvida-lista')


@method_decorator(login_required, name='dispatch')
class BaseConhecimentoView(ListView):
    model = Duvida
    template_name = 'monitoria/base_conhecimento.html'
    context_object_name = 'duvidas'

    def get_queryset(self):
        termo = self.request.GET.get('q', '').strip()
        queryset = Duvida.objects.select_related('disciplina').filter(
            situacao__in=[Duvida.Situacao.RESPONDIDA, Duvida.Situacao.ENCERRADA]
        )
        if termo:
            queryset = queryset.filter(Q(titulo__icontains=termo) | Q(descricao__icontains=termo))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '').strip()
        return context
