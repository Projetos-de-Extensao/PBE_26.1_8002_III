from celery import shared_task
from .services.AI.client import client as ai_client
from .services.AI.lerContrato import lerContrato
from .services.ler_extrair_infos_pdf import ler_pdf_modo_layout
from .models import *
from .services.validacao_sistema.validaGradeContrato import validarGradeContrato
from .exceptions import gradeHorariaIncompativelException
from . import email_tasks

@shared_task(bind=True, max_retries=3)
def processarContratoComIa(self, fileId):
    try:
        contrato = Contrato.objects.get(id=fileId)
        arquivoPath = contrato.arquivo
        string_contrato = ler_pdf_modo_layout(arquivoPath)
    except Exception as e:
        raise self.retry(exc=e, countdown=60)

    
    agente = ai_client
    try:
        dados_contrato = lerContrato(string_contrato)
    except Exception as e:
        raise self.retry(exc=e, countdown=60)
        
    contrato.cnpj_empresa = dados_contrato["cnpj_empresa"]
    contrato.nome_empresa = dados_contrato["nome_empresa"]
    contrato.data_inicio = dados_contrato["data_inicio"]
    contrato.data_termino = dados_contrato["data_termino"]
    contrato.apolice_seguro = dados_contrato["apolice_seguro"]
    contrato.plano_atividade = dados_contrato["plano_atividade"]
    contrato.assinatura_aluno = dados_contrato["assinatura_aluno"]
    contrato.assinatura_empresa = dados_contrato["assinatura_empresa"]
    contrato.assinatura_faculdade = dados_contrato["assinatura_faculdade"]
    contrato.save()

    # Atualiza o nome da empresa no processo para refletir o valor lido pela IA
    processo = contrato.processoId
    if dados_contrato.get("nome_empresa"):
        processo.nome_empresa = dados_contrato["nome_empresa"]
        processo.save()

    # Associa os horários de atividade extraídos ao contrato
    horarios_data = dados_contrato.get("horarios_atividade", [])
    if horarios_data:
        contrato.horarios_atividade.clear()
        for h in horarios_data:
            horario, _ = Horarios.objects.get_or_create(
                dia=h["dia"],
                turno=h["turno"],
            )
            contrato.horarios_atividade.add(horario)
            
    # Dispara a validação do contrato
    validarContrato.delay(contrato.id, contrato.processoId.aluno.id)
    
@shared_task
def validarContrato(fileId, alunoId):
    """
    Tarefa acionada logo após o processamento da IA. 
    Aplica as regras rígidas da Lei do Estágio (Lei 11.788) e políticas do Ibmec.
    Se alguma infração for detectada (ex: carga horária > 30h semanais, 
    sem apólice, contrato retroativo), reprova o contrato automaticamente.
    """
    contrato = Contrato.objects.get(id=fileId)
    aluno = Aluno.objects.get(id=alunoId)
    
    horarios_contrato = contrato.horarios_atividade.all()
    grade_aluno = aluno.grade.all()
    
    conflito = False
    for horario in horarios_contrato:
        if horario in grade_aluno:
            conflito = True
            break
            
    contrato.conflito_grade = conflito
    contrato.save()
    
    # --- Reprovação Automática baseada nas regras de negócio extraídas pela IA ---
    motivos_reprovacao = []
    
    from dateutil.relativedelta import relativedelta
    from django.utils import timezone
    if contrato.data_inicio and contrato.data_termino:
        # Limite legal de 24 meses
        limite_fim = contrato.data_inicio + relativedelta(months=24)
        if contrato.data_termino > limite_fim and not getattr(aluno, 'is_pcd', False):
            motivos_reprovacao.append("- Vigência supera 24 meses permitidos por lei.")
            
        # Previsão de Formatura
        meses_restantes_curso = (10 - aluno.periodo + 1) * 6
        limite_formatura = contrato.data_inicio + relativedelta(months=meses_restantes_curso)
        if contrato.data_termino > limite_formatura:
            motivos_reprovacao.append("- A data de término ultrapassa a previsão de formatura do aluno.")
            
        # Retroatividade: data_upload - data_inicio > 30 dias
        data_ref = contrato.data_upload or timezone.now().date()
        if (data_ref - contrato.data_inicio).days > 30:
            motivos_reprovacao.append("- O contrato foi iniciado há mais de 30 dias (retroatividade não permitida).")
            
    # Carga Horária: horas_diarias > 6 OU horas_semanais > 30
    horas_por_dia = {}
    total_semanal = 0
    for h in horarios_contrato:
        duracao = 4.0  # Cada turno/período dura cerca de 4 horas
        horas_por_dia[h.dia] = horas_por_dia.get(h.dia, 0) + duracao
        total_semanal += duracao
        
    excedeu_diario = False
    for dia, horas in horas_por_dia.items():
        if horas > 6:
            excedeu_diario = True
            
    dias_unicos = len(horas_por_dia.keys())
    if excedeu_diario or (dias_unicos * 6 > 30) or total_semanal > 30:
        motivos_reprovacao.append("- Carga horária semanal excede 30 horas ou diária excede 6 horas (violação da Lei 11.788).")
            
    if not contrato.apolice_seguro or not str(contrato.apolice_seguro).strip():
        motivos_reprovacao.append("- Apólice de seguros ausente ou inválida (Obrigatório).")
        
    if not contrato.plano_atividade:
        motivos_reprovacao.append("- Plano de atividades ausente.")
        
    if not contrato.assinatura_aluno or not contrato.assinatura_empresa:
        motivos_reprovacao.append("- Faltam assinaturas do aluno ou da empresa com carimbo.")
        
    if contrato.assinatura_faculdade:
        motivos_reprovacao.append("- O documento já contém assinatura da instituição (O IBMEC é a última a assinar).")
        
    if conflito:
        motivos_reprovacao.append("- Conflito detectado com a grade horária de aulas do aluno.")
        
    # Se houver motivos, reprova automaticamente sem bloquear o envio inicial
    if motivos_reprovacao:
        contrato.status = StatusContrato.REPROVADO
        contrato.save()
        
        processo = contrato.processoId
        processo.status = StatusProcesso.REPROVADO
        processo.save()
        
        justificativa_completa = "Reprovação Automática pelo Sistema:\n" + "\n".join(motivos_reprovacao)
        
        # Cria ou atualiza o histórico usando uma secretaria padrão/sistema
        secretaria_sistema = Secretaria.objects.first()
        if secretaria_sistema:
            HistoricoAvaliacaoContrato.objects.update_or_create(
                contrato_id=contrato,
                avaliador=secretaria_sistema,
                defaults={
                    'observacoes': justificativa_completa,
                    'veredito': Veredito.REPROVADO,
                    'justificativa': justificativa_completa
                }
            )
        
        # Notifica o aluno
        from core.services.email_service import EmailNotificationService
        EmailNotificationService.notificar_avaliacao(
            email_destino=aluno.email,
            nome_aluno=aluno.nome,
            status=Veredito.REPROVADO,
            observacoes=justificativa_completa
        )
    else:
        # Contrato passou em todas as validações do sistema
        secretaria_sistema = Secretaria.objects.first()
        if secretaria_sistema:
            HistoricoAvaliacaoContrato.objects.update_or_create(
                contrato_id=contrato,
                avaliador=secretaria_sistema,
                defaults={
                    'observacoes': "Validação Automática pelo Sistema: Contrato aprovado em todas as verificações.",
                    'veredito': Veredito.APROVADO,
                    'justificativa': "Nenhuma irregularidade detectada nas regras de negócio."
                }
            )

@shared_task(bind=True, max_retries=3)
def processarRelatorioComIa(self, relatorio_id):
    from core.services.AI.lerRelatorio import lerRelatorio

    try:
        relatorio = Relatorio.objects.get(id=relatorio_id)
        if not relatorio.arquivo:
            return
            
        string_relatorio = ler_pdf_modo_layout(relatorio.arquivo)
        
        dados = lerRelatorio(string_relatorio)
    except Exception as e:
        raise self.retry(exc=e, countdown=60)
        
    relatorio.titulo = dados.get("titulo") or ""
    relatorio.corpo = dados.get("corpo") or ""
    relatorio.save()
    
    if FeatureFlag.objects.is_active("report_evaluation_ai"):
        avaliarRelatorioComIa.delay(relatorio.id)

@shared_task(bind=True, max_retries=3)
def avaliarRelatorioComIa(self, relatorio_id):
    from core.services.AI.lerRelatorio import avaliarRelatorio, carregar_ementa_curso
    from core.services.email_service import EmailNotificationService

    try:
        relatorio = Relatorio.objects.select_related(
            'processo_id__aluno__curso'
        ).get(id=relatorio_id)
        curso = relatorio.processo_id.aluno.curso
        
        # Roteamento Dinâmico de Ementas com fallback para o banco de dados
        try:
            ementa_texto = carregar_ementa_curso(curso.nome)
        except FileNotFoundError:
            if curso.ementa_md:
                ementa_texto = curso.ementa_md.read().decode("utf-8")
            else:
                return

        resultado = avaliarRelatorio(relatorio.corpo, ementa_texto)
    except Exception as e:
        raise self.retry(exc=e, countdown=60)

    justificativa = resultado.get("justificativa", "")
    coordenador = Coordenador.objects.first()

    is_aprovado = resultado.get("status") == "APROVADO" if "status" in resultado else resultado.get("compativel", True)

    if is_aprovado:
        relatorio.status = StatusRelatorio.APROVADO
        relatorio.save()

        processo = relatorio.processo_id
        processo.status = StatusProcesso.CONCLUIDO
        processo.save()

        if coordenador:
            HistoricoAvaliacaoRelatorio.objects.create(
                observacoes=f"Avaliação Automática por IA: {justificativa}",
                veredito=Veredito.APROVADO,
                avaliador=coordenador,
                relatorio_id=relatorio,
                justificativa=justificativa,
            )

        aluno = relatorio.processo_id.aluno
        EmailNotificationService.notificar_avaliacao(
            email_destino=aluno.email,
            nome_aluno=aluno.nome,
            status=Veredito.APROVADO,
            observacoes=f"Relatório aprovado automaticamente: {justificativa}",
        )
    else:
        relatorio.status = StatusRelatorio.REPROVADO
        relatorio.save()

        processo = relatorio.processo_id
        processo.status = StatusProcesso.CANCELADO
        processo.save()

        if coordenador:
            HistoricoAvaliacaoRelatorio.objects.create(
                observacoes=f"Avaliação Automática por IA: {justificativa}",
                veredito=Veredito.REPROVADO,
                avaliador=coordenador,
                relatorio_id=relatorio,
                justificativa=justificativa or "Atividades incompatíveis com o curso.",
            )

        aluno = relatorio.processo_id.aluno
        EmailNotificationService.notificar_avaliacao(
            email_destino=aluno.email,
            nome_aluno=aluno.nome,
            status=Veredito.REPROVADO,
            observacoes=f"Relatório reprovado automaticamente: {justificativa}",
        )

