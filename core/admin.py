from django.contrib import admin
from .models import (
    Aluno, Coordenador, Secretaria, Area, Curso,
    Processo, Contrato, Relatorio,
    HistoricoAvaliacaoRelatorio, HistoricoAvaliacaoContrato,
    FeatureFlag
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


class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_enabled', 'updated_at', 'updated_by']
    readonly_fields = ['updated_at', 'updated_by']

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


admin.site.register(FeatureFlag, FeatureFlagAdmin)
