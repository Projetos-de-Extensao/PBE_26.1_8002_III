---
id: anexar_contrato
title: Anexar Contrato
---

### Anexar Contrato (Include)

- **Atores:**
    - Usuário
    - Sistema

- **Pré-Condições:**
    - Estar em um fluxo que exija envio de arquivo (Iniciar Processo ou Enviar Relatório).

- **Fluxo Básico:**
    1. Usuário clica no botão "Escolher Arquivo".
    2. Sistema operacional abre janela de seleção.
    3. Usuário seleciona um contrato `.pdf` e confirma.
    4. Sistema lê o cabeçalho do arquivo, valida sua extensão e tamanho.
    5. Sistema armazena o arquivo temporariamente na memória até a submissão final do formulário.

- **Fluxos Alternativos:**
    - **4a. Arquivo excede o tamanho máximo**
        - 4a1. Sistema rejeita o arquivo e emite erro: *"Tamanho máximo excedido (5MB)."*

- **Pós-condições:**
    - O arquivo fica pronto (em buffer) para ser enviado ao banco de dados/storage (ex: AWS S3).

- **Regras de Negócio:**
    - Tipos MIME estritamente limitados a `application/pdf`.