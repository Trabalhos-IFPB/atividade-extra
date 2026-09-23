from django.contrib.auth.models import User
from django.db import models


class Disciplina(models.Model):
    nome = models.CharField(max_length=120)
    codigo = models.CharField(max_length=20, unique=True)
    ativa = models.BooleanField(default=True)
    monitores = models.ManyToManyField(User, blank=True, related_name='disciplinas_monitoradas')

    def __str__(self):
        return f'{self.codigo} - {self.nome}'


class Duvida(models.Model):
    class Situacao(models.TextChoices):
        ABERTA = 'ABERTA', 'Aberta'
        EM_ATENDIMENTO = 'EM_ATENDIMENTO', 'Em atendimento'
        RESPONDIDA = 'RESPONDIDA', 'Respondida'
        ENCERRADA = 'ENCERRADA', 'Encerrada'

    titulo = models.CharField(max_length=150)
    descricao = models.TextField()
    disciplina = models.ForeignKey(Disciplina, on_delete=models.PROTECT, related_name='duvidas')
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='duvidas_abertas')
    monitor_responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='duvidas_assumidas',
        null=True,
        blank=True,
    )
    resposta = models.TextField(blank=True)
    situacao = models.CharField(max_length=20, choices=Situacao.choices, default=Situacao.ABERTA)
    abertura_em = models.DateTimeField(auto_now_add=True)
    atualizacao_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-atualizacao_em',)

    def __str__(self):
        return self.titulo

    def pode_assumir(self, user):
        return self.situacao == self.Situacao.ABERTA and self.disciplina.monitores.filter(pk=user.pk).exists()

    def pode_responder(self, user):
        return self.situacao == self.Situacao.EM_ATENDIMENTO and self.monitor_responsavel_id == user.id

    def pode_encerrar(self, user):
        return (
            self.situacao == self.Situacao.RESPONDIDA
            and self.autor_id == user.id
            and bool(self.resposta.strip())
        )
