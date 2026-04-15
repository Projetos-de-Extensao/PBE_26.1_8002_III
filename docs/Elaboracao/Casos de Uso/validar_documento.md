---
id: validar_documento
title: Validar Documento
---

### Validar Documento

- **Atores:**
    - Secretaria
    - Sistema

- **Pré-Condições:**
    - O Usuário deve estar logado no sistema.
    - Deve existir pelo menos um processo com status "Pendente de Análise".

- **Fluxo Básico:**
    1. Secretaria acessa a fila de documentos pendentes.
    2. Sistema lista os processos aguardando avaliação.
    3. Secretaria seleciona um processo específico.
    4. Sistema exibe os detalhes do aluno, da empresa e o PDF do contrato (Ação: Analisar Documento).
    5. Secretaria verifica as assinaturas, datas e apólices.
    6. Secretaria clica no botão "Aprovar".
    7. Sistema atualiza o status para "Aprovado" e notifica o Aluno.

- **Fluxos Alternativos:**
    - **5a. Documento possui erros burocráticos (Ação: Reprovar com Justificativa)**
        - 5a1. Secretaria clica em "Reprovar".
        - 5a2. Sistema exige o preenchimento de um campo de justificativa.
        - 5a3. Secretaria escreve o motivo (ex: *"Falta carimbo da empresa"*) e confirma.
        - 5a4. Sistema atualiza o status para "Reprovado" e notifica o Aluno com a justificativa.

- **Pós-condições:**
    - O status do documento é alterado para "Aprovado" ou "Reprovado".
    - O registro da avaliação (quem avaliou e quando) é salvo no histórico do processo.

- **Regras de Negócio:**
    - Apenas usuários com perfil "Secretaria" ou superior podem alterar o status de validação de um documento.
    - A justificativa é de preenchimento obrigatório sempre que um documento for reprovado.