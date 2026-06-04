from django.contrib import admin
from .models import (
    Aluno, Coordenador, Secretaria, Area, Curso,
    Processo, Contrato, Relatorio,
    HistoricoAvaliacaoRelatorio, HistoricoAvaliacaoContrato
)

# Register your models here.
admin.site.register(Coordenador)
admin.site.register(Secretaria)
admin.site.register(Area)
admin.site.register(Curso)
admin.site.register(Processo)
admin.site.register(Contrato)
admin.site.register(Relatorio)
admin.site.register(HistoricoAvaliacaoRelatorio)
admin.site.register(HistoricoAvaliacaoContrato)

class AlunoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'matricula', 'cpf', 'is_ativo')

admin.site.register(Aluno, AlunoAdmin)
