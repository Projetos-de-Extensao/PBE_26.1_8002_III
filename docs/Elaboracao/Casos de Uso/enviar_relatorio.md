---
id: enviar_relatorio
title: Enviar Relatório de Horas
---

### Enviar Relatório de Horas

- **Atores:**
    - Aluno
    - Sistema

- **Pré-Condições:**
    - O Aluno deve estar logado.
    - O Aluno deve possuir um processo de estágio com status "Em Andamento".

- **Fluxo Básico:**
    1. Aluno acessa os detalhes do seu estágio ativo.
    2. Aluno clica em "Adicionar Relatório de Atividades".
    3. Sistema exibe formulário solicitando período de referência e horas cumpridas.
    4. Aluno preenche os campos e anexa o documento assinado (Ação: Anexar Documento).
    5. Aluno clica em "Enviar Relatório".
    6. Sistema salva o documento e muda o status do relatório para "Aguardando Validação".

- **Fluxos Alternativos:**
    - **4a. Relatório enviado fora do prazo**
        - 4a1. Sistema exibe alerta *"Envio fora do prazo regulamentar. Sujeito a penalização pedagógica."*
        - 4a2. Sistema permite a continuação do envio, mas o marca com flag de atraso.

- **Pós-condições:**
    - O relatório é anexado ao histórico do processo do aluno.

- **Regras de Negócio:**
    - O total de horas reportadas não pode exceder a carga horária estipulada no Termo de Compromisso (TCE).