from celery import shared_task
from .services.AI.client import client as ai_client
from .services.AI.lerContrato import lerContrato
from .services.ler_extrair_infos_pdf import ler_pdf_modo_layout
from .models import Contrato


@shared_task
def processarContratoComIa(fileId):
    contrato = Contrato.objects.get(id=fileId)
    arquivoPath = contrato.arquivo
    string_contrato = ler_pdf_modo_layout(arquivoPath)
    
    agente = ai_client
    dados_contrato = lerContrato(string_contrato)
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
    


  
