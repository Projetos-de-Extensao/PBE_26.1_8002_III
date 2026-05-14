from django.contrib import admin
from .models import *
from .models import Aluno

# Register your models here.
admin.site.register(Contrato)
admin.site.register(Processo)
admin.site.register(Area)
admin.site.register(Curso)

# Conseguimos adicionar os alunos diretamente aos usuarios do Django Admin
@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'matricula', 'cpf', 'is_ativo')
