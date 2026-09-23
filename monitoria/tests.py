from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from .models import Disciplina, Duvida


class MonitoriaFlowTests(TestCase):
    def setUp(self):
        self.aluno_group, _ = Group.objects.get_or_create(name='Aluno')
        self.prof_group, _ = Group.objects.get_or_create(name='Professor')

        self.aluno1 = User.objects.create_user(username='aluno1', password='Senha@123456')
        self.aluno2 = User.objects.create_user(username='aluno2', password='Senha@123456')
        self.monitor = User.objects.create_user(username='monitor', password='Senha@123456')
        self.professor = User.objects.create_user(username='professor', password='Senha@123456')

        self.aluno1.groups.add(self.aluno_group)
        self.aluno2.groups.add(self.aluno_group)
        self.professor.groups.add(self.prof_group)

        self.disciplina1 = Disciplina.objects.create(nome='RAD', codigo='RAD101', ativa=True)
        self.disciplina2 = Disciplina.objects.create(nome='POO', codigo='POO101', ativa=True)
        self.disciplina1.monitores.add(self.monitor)

        self.duvida_rad = Duvida.objects.create(
            titulo='Erro de template',
            descricao='Nao renderiza',
            disciplina=self.disciplina1,
            autor=self.aluno1,
        )
        self.duvida_poo = Duvida.objects.create(
            titulo='Lista encadeada',
            descricao='Duvida em ponteiro',
            disciplina=self.disciplina2,
            autor=self.aluno2,
        )

    def test_signup_assigns_aluno_group(self):
        response = self.client.post(
            reverse('signup'),
            {
                'username': 'novoaluno',
                'password1': 'Senha@123456789',
                'password2': 'Senha@123456789',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        novo = User.objects.get(username='novoaluno')
        self.assertTrue(novo.groups.filter(name='Aluno').exists())

    def test_role_based_list_visibility(self):
        self.client.login(username='aluno1', password='Senha@123456')
        response = self.client.get(reverse('duvida-lista'))
        self.assertContains(response, 'Erro de template')
        self.assertNotContains(response, 'Lista encadeada')

        self.client.login(username='monitor', password='Senha@123456')
        response = self.client.get(reverse('duvida-lista'))
        self.assertContains(response, 'Erro de template')
        self.assertNotContains(response, 'Lista encadeada')

        self.client.login(username='professor', password='Senha@123456')
        response = self.client.get(reverse('duvida-lista'))
        self.assertContains(response, 'Erro de template')
        self.assertContains(response, 'Lista encadeada')

    def test_assumir_requires_disciplina_monitor(self):
        self.client.login(username='monitor', password='Senha@123456')
        response = self.client.post(reverse('duvida-assumir', args=[self.duvida_rad.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.duvida_rad.refresh_from_db()
        self.assertEqual(self.duvida_rad.monitor_responsavel, self.monitor)
        self.assertEqual(self.duvida_rad.situacao, Duvida.Situacao.EM_ATENDIMENTO)

        self.duvida_poo.refresh_from_db()
        response = self.client.post(reverse('duvida-assumir', args=[self.duvida_poo.id]))
        self.assertEqual(response.status_code, 403)

    def test_responder_and_encerrar_permissions(self):
        self.duvida_rad.monitor_responsavel = self.monitor
        self.duvida_rad.situacao = Duvida.Situacao.EM_ATENDIMENTO
        self.duvida_rad.save()

        self.client.login(username='aluno1', password='Senha@123456')
        response = self.client.post(reverse('duvida-responder', args=[self.duvida_rad.id]), {'resposta': 'x'})
        self.assertEqual(response.status_code, 403)

        self.client.login(username='monitor', password='Senha@123456')
        response = self.client.post(reverse('duvida-responder', args=[self.duvida_rad.id]), {'resposta': '   '})
        self.assertContains(response, 'A resposta não pode ficar em branco.')

        response = self.client.post(
            reverse('duvida-responder', args=[self.duvida_rad.id]),
            {'resposta': 'Use include e extends.'},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.duvida_rad.refresh_from_db()
        self.assertEqual(self.duvida_rad.situacao, Duvida.Situacao.RESPONDIDA)

        self.client.login(username='aluno2', password='Senha@123456')
        response = self.client.post(reverse('duvida-encerrar', args=[self.duvida_rad.id]))
        self.assertEqual(response.status_code, 403)

        self.client.login(username='aluno1', password='Senha@123456')
        response = self.client.post(reverse('duvida-encerrar', args=[self.duvida_rad.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.duvida_rad.refresh_from_db()
        self.assertEqual(self.duvida_rad.situacao, Duvida.Situacao.ENCERRADA)

    def test_base_conhecimento_filters_status_and_search(self):
        self.duvida_rad.situacao = Duvida.Situacao.RESPONDIDA
        self.duvida_rad.resposta = 'Resolvido'
        self.duvida_rad.save()

        self.client.login(username='aluno2', password='Senha@123456')
        response = self.client.get(reverse('base-conhecimento'))
        self.assertContains(response, 'Erro de template')
        self.assertNotContains(response, 'Lista encadeada')

        response = self.client.get(reverse('base-conhecimento') + '?q=template')
        self.assertContains(response, 'Erro de template')
