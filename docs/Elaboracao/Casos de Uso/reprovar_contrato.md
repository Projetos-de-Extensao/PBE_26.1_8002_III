---
id: reprovar_contrato
title: Reprovar Contrato com Justificativa
---

### Reprovar Contrato com Justificativa (Extend)

- **Atores:**
    - Secretaria
    - Sistema

- **Pré-Condições:**
    - Estar dentro do fluxo de "Validar Contrato".

- **Fluxo Básico:**
    1. Ao constatar um erro, a Secretaria clica no botão "Reprovar Contrato".
    2. Sistema exibe um modal de texto obrigatório.
    3. Secretaria redige o que o aluno precisa corrigir no arquivo.
    4. Secretaria clica em "Confirmar Reprovação".
    5. Sistema salva a justificativa e dispara notificação automática.

- **Fluxos Alternativos:**
    - **3a. Justificativa em branco**
        - 3a1. Sistema bloqueia o botão de confirmação.

- **Pós-condições:**
    - O status do contrato vai para "Reprovado".

- **Regras de Negócio:**
    - A justificativa fica registrada no histórico e não pode ser apagada posteriormente (princípio de auditoria).