from rest_framework import serializers
from .models import *
from .validators import validar_email_institucional
from .enums import StatusProcesso

class NestedProcessoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Processo
        fields = ["id", "nome_empresa", "status"]


class AlunoSerializer(serializers.ModelSerializer):
    processos = NestedProcessoSerializer(source="matricula_aluno", many=True, read_only=True)

    class Meta:
        model = Aluno
        fields = ['nome', 'email', 'matricula', 'senha', 'cpf', 'is_ativo', 'unidade', 'periodo', 'curso', 'processos']

    def create(self, validated_data):
        return Aluno.objects.create(**validated_data)

    def update(self,instance,validated_data):
        instance.nome = validated_data.get("nome",instance.nome)
        instance.email = validated_data.get("email",instance.email)
        instance.matricula = validated_data.get("matricula",instance.matricula)
        instance.senha = validated_data.get("senha",instance.senha)
        instance.cpf = validated_data.get("cpf",instance.cpf)
        instance.is_ativo = validated_data.get("is_ativo",instance.is_ativo)
        instance.unidade = validated_data.get("unidade",instance.unidade)
        instance.save()
        return instance

class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = ["nome"]
        read_only_fields = ["id"]
        exclude = ["areaId"]


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ["nome"]
        read_only_fields = ["id"]

class ProcessoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Processo
        fields = ["status", "matricula_aluno", "nome_empresa"]
        read_only_fields = ["id", "data_criacao", "status"]
        extra_kwargs = {
            'nome_empresa': {
                'error_messages': {
                    'required': 'O campo Nome da Empresa é obrigatório.',
                    'blank': 'O campo Nome da Empresa não pode ser vazio.',
                }
            },
            'matricula_aluno': {
                'error_messages': {
                    'required': 'O campo Matrícula do Aluno é obrigatório.',
                    'does_not_exist': 'Aluno com esta matrícula não foi encontrado.',
                    'null': 'O campo Matrícula do Aluno não pode ser nulo.',
                }
            },
        }

    def validate(self, attrs):
        aluno = attrs.get('matricula_aluno')
        if aluno:
            STATUS_TERMINAL = [
                StatusProcesso.REPROVADO,
                StatusProcesso.CONCLUIDO,
                StatusProcesso.CANCELADO,
            ]
            processo_ativo = Processo.objects.filter(
                matricula_aluno=aluno
            ).exclude(status__in=STATUS_TERMINAL).first()

            if processo_ativo:
                raise serializers.ValidationError({
                    "matricula_aluno": (
                        f"Este aluno já possui um processo ativo "
                        f"(ID: {processo_ativo.id}, Status: {processo_ativo.get_status_display()}). "
                        f"Não é possível criar outro processo enquanto houver um em andamento."
                    )
                })
        return attrs

    def create(self, validated_data):
        return Processo.objects.create(**validated_data)
    

class ContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        fields = [
            "cnpj_empresa", "nome_empresa",
            "data_inicio", "data_termino", "apolice_seguro", "plano_atividade",
            "assinatura_aluno", "assinatura_empresa", "assinatura_faculdade",
            "processoId"
        ]
        read_only_fields = ["id", "arquivo", "data_upload"]



class CoordenadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordenador
        fields = ['nome', 'email', 'matricula', 'senha', 'unidade', 'areaId']
        read_only_fields = ['id']


class SecretariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Secretaria
        fields = ['nome', 'email', 'matricula', 'senha', 'unidade']
        read_only_fields = ['id']


class RelatorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relatorio
        fields = [
            'processo_id', 'arquivo', 'data_upload',
            'horas_trabalhadas', 'data_inicio', 'data_termino', 'status'
        ]
        read_only_fields = ['id', 'data_upload']


class HistoricoAvaliacaoRelatorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoAvaliacaoRelatorio
        fields = ['observacoes', 'data_avaliacao', 'veredito', 'avaliador', 'relatorio_id']
        read_only_fields = ['id', 'data_avaliacao']


class HistoricoAvaliacaoContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoAvaliacaoContrato
        fields = ['observacoes', 'data_avaliacao', 'veredito', 'avaliador', 'contrato_id']
        read_only_fields = ['id', 'data_avaliacao']
