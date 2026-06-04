from pypdf import PdfReader



def ler_pdf_modo_layout(caminho_pdf):
    """
    Lê um arquivo PDF e extrai o texto da primeira página preservando
    o layout visual (tabelas, colunas e espaçamentos).
    
    Args:
        caminho_pdf (str): O caminho para o arquivo PDF no sistema.
        
    Returns:
        str: O texto extraído da primeira página ou None se ocorrer erro.
    """
    reader = PdfReader(caminho_pdf)
    
    for idx, pagina in enumerate(reader.pages):
        texto = pagina.extract_text(extraction_mode="layout")
        return texto




def extrair_data(campo_data):
    """
    Extrai e formata as datas de início e término contidas em uma string.
    
    Espera uma string com padrão 'Duração.De[DataInicio]a[DataFim]' (ex: '12meses.De01072025a3006/2026')
    e retorna uma tupla com as datas devidamente formatadas no padrão DD/MM/AAAA.
    
    Args:
        campo_data (str): String contendo as datas de vigência do contrato.
        
    Returns:
        tuple: (data_inicio, data_termino) no formato "DD/MM/AAAA" ou ("","") em caso de erro.
    """
    if not campo_data or not isinstance(campo_data, str):
        return "", ""
        
    # Encontra o ponto separador do período
    divisao = campo_data.find('.')
    if divisao == -1:
        return campo_data
    else:
        inicio_e_fim = campo_data[divisao:]
        
    # Busca a letra 'a' que serve de divisória entre a data de início e término
    index_divisoria_datas = inicio_e_fim.find('a')
    if index_divisoria_datas == -1:
        return "", ""
        
    index_comeco_das_datas = 3  # Pula os caracteres '.De'
    try:
        numero_data_inicio = inicio_e_fim[index_comeco_das_datas:index_divisoria_datas].replace('/', '')
        numero_data_termino = inicio_e_fim[index_divisoria_datas+1:].replace('/', '')
    except:
        return "", ""
    
    # Valida e formata a data de início caso tenha o tamanho mínimo de 8 caracteres
    if len(numero_data_inicio) >= 8:
        data_inicio = numero_data_inicio[:2] + '/' + numero_data_inicio[2:4] + '/' + numero_data_inicio[4:8]
    else:
        data_inicio = numero_data_inicio
        
    # Valida e formata a data de término
    if len(numero_data_termino) >= 8:
        data_termino = numero_data_termino[:2] + '/' + numero_data_termino[2:4] + '/' + numero_data_termino[4:8]
    else:
        data_termino = numero_data_termino
        
    return data_inicio, data_termino
    

def separar_apolice_seguradora(string):
    """
    Separa o número da apólice do nome da seguradora de uma string aglutinada.
    
    Procura o último dígito numérico da string (de trás para frente) e realiza a divisão
    naquele ponto.
    
    Args:
        string (str): String aglutinada (ex: 'APL-2025-00987654PortoSeguroS.A.')
        
    Returns:
        tuple: (numero_apolice, nome_seguradora). Caso não ache números, assume toda a string como seguradora.
    """
    if not string or not isinstance(string, str):
        return "", ""
        
    # Procuramos o último dígito numérico da string (de trás para frente)
    # range(..., -1, -1) garante que o índice 0 também seja verificado
    for i in range(len(string)-1, -1, -1):
        if string[i].isdigit():
            indice = i
            numero_apolice = string[0:indice+1]
            seguradora = string[indice+1:]
            return numero_apolice, seguradora
            
    # Caso não encontre nenhum número, retorna vazio para a apólice e a string original para a seguradora
    # Evita retornar None e quebrar o código com TypeError
    return "", string



def extrair_infos(pdf):
    """
    Analisa o texto de layout do PDF, remove os cabeçalhos/rótulos do contrato
    e retorna os dados essenciais limpos em formato de dicionário.
    
    Args:
        pdf (str): O texto bruto extraído da página do PDF em modo layout.
        
    Returns:
        dict: Dicionário contendo os campos do modelo Contrato:
              "nome_empresa", "cnpj_empresa", "data_inicio", "data_termino", "apolice_seguro" e "seguradora".
    """
    if not pdf or not isinstance(pdf, str):
        return {}
        
    # Lista de rótulos do contrato que devem ser removidos para sobrar apenas os valores inseridos
    campos_contrato = ['.emConselho','CONCEDENTEDOESTÁGIO(EMPRESA)','CNPJ ou CPF e Registro', 'Endereço','CEP', 'E-mail', 'Tel.','Representante','Cargo','Local do Estágio (setor ou endereço do estágio)','INTERVENIENTE (INSTITUIÇÃO DE ENSINO)','CNPJ','ENDEREÇO', 'REPRESENTANTES DA INSTITUIÇÃO DE ENSINO','CARGO','UNIDADE/POLO DO ALUNO','NOME DO(A) ESTAGIÁRIO(A)','MATRÍCULA','CPF','CEP','CURSO','DURAÇÃO / PERÍODO DO ESTÁGIO','NÚMERO DA APÓLICE DE SEGURO','SEGURADORA','IBMECCARREIRAS','TERMODECOMPROMISSODEESTÁGIO']
    
    # Normalização inicial: remove espaços simples, converte quebras em espaços e remove parênteses vazios
    strings_tratadas = pdf.replace(' ', '').replace('\n', ' ').replace('()',''   )
    
    # Remove as informações de checkboxes e do rodapé do documento cortando tudo a partir de '['
    separacao_checkbox = strings_tratadas.find('[')
    if separacao_checkbox != -1:
        strings_tratadas = strings_tratadas[:separacao_checkbox]
        
    # Remove todos os rótulos de campos removendo espaços para coincidir com a normalização
    for campo in campos_contrato:
        strings_tratadas = strings_tratadas.replace(campo.replace(' ',''),'')
    
    # Divide a string em uma lista, separando por espaço (que representava a quebra de linha original)
    respostas = strings_tratadas.split(' ')
    respostas = [resposta for resposta in respostas if resposta.strip() != '']  
    
    # Criando o dicionário com os campos do modelo Contrato
    contrato_dict = {}
    
    # Preenchimento seguro validando a existência do índice para evitar IndexError
    if len(respostas) > 0:
        contrato_dict["nome_empresa"] = respostas[0]
    if len(respostas) > 1:
        contrato_dict["cnpj_empresa"] = respostas[1]
        
    if len(respostas) > 15:
        data_ini, data_fim = extrair_data(respostas[15])
        contrato_dict["data_inicio"] = data_ini
        contrato_dict["data_termino"] = data_fim
        
    if len(respostas) > 16:
        apolice, seguradora = separar_apolice_seguradora(respostas[16])
        contrato_dict["apolice_seguro"] = apolice
        contrato_dict["seguradora"] = seguradora
        
    return contrato_dict





        
            
            
            
            
            