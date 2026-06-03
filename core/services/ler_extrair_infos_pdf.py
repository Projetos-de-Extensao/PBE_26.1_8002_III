from pypdf import PdfReader



def ler_pdf_modo_layout(caminho_pdf):
    reader = PdfReader(caminho_pdf)
    
    for idx, pagina in enumerate(reader.pages, start=1):
        print(f"\n--- PÁGINA {idx} (Modo Layout) ---")
        
        # O segredo está no extraction_mode="layout"
        # Ele preserva o espaçamento visual das tabelas do contrato
        texto = pagina.extract_text(extraction_mode="layout")
        return texto

# Execute
pdf = ler_pdf_modo_layout('./core/services/TCE_preenchido.pdf')



def extrair_infos(pdf):
    campos_contrato = ['CONCEDENTEDOESTÁGIO(EMPRESA)','CNPJ ou CPF e Registro', 'Endereço','CEP', 'E-mail', 'Tel.','Representante','Cargo','Local do Estágio (setor ou endereço do estágio)','INTERVENIENTE (INSTITUIÇÃO DE ENSINO)','CNPJ','ENDEREÇO', 'REPRESENTANTES DA INSTITUIÇÃO DE ENSINO','CARGO','UNIDADE/POLO DO ALUNO','NOME DO(A) ESTAGIÁRIO(A)','MATRÍCULA','CPF','CEP','CURSO','DURAÇÃO / PERÍODO DO ESTÁGIO','NÚMERO DA APÓLICE DE SEGURO','SEGURADORA','IBMECCARREIRAS','TERMODECOMPROMISSODEESTÁGIO']
    strings_tratadas = pdf.replace(' ', '').replace('\n', ' ').replace('()',''   )
    separacao_checkbox = strings_tratadas.find('[')
    strings_tratadas = strings_tratadas[:separacao_checkbox]
    for campo in campos_contrato:
        strings_tratadas = strings_tratadas.replace(campo.replace(' ',''),'')
    
    
    respostas = strings_tratadas.split(' ')
    respostas = [resposta for resposta in respostas if resposta != '']  
    
    # Criando o dicionário com os campos do modelo Contrato
    contrato_dict = {}
    if len(respostas) >= 17:
        contrato_dict = {
            "nome_empresa": respostas[0],
            "cnpj_empresa": respostas[1],
            "data_inicio": respostas[15],  # Requer tratamento posterior para extrair a data exata (ex: 01/07/2025)
            "data_termino": respostas[15], # Requer tratamento posterior para extrair a data exata (ex: 30/06/2026)
            "apolice_seguro": respostas[16],
        }
        
    return contrato_dict





   


lista_tratada = extrair_infos(pdf)


        
            
            
            
            
            