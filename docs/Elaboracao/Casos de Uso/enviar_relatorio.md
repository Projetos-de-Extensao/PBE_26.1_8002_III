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
    3. Sistema exibe formulário para o envio do arquivo PDF do relatório.
    4. Aluno anexa o documento assinado (Ação: Anexar Documento).
    5. Aluno clica em "Enviar Relatório".
    6. Sistema salva o documento e muda o status do relatório para "Aguardando Validação".
    7. Sistema extrai título e corpo via Inteligência Artificial e realiza a validação semântica do conteúdo contra a ementa do curso correspondente.

- **Fluxos Alternativos:**
    - **4a. Relatório enviado fora do prazo**
        - 4a1. Sistema exibe alerta *"Envio fora do prazo regulamentar. Sujeito a penalização pedagógica."*
        - 4a2. Sistema permite a continuação do envio, mas o marca com flag de atraso.
    - **7a. Feature Flag de Inteligência Artificial Inativa**
        - 7a1. O sistema não processa o relatório automaticamente.
        - 7a2. A extração dos dados (título e corpo) e a validação/aprovação do conteúdo ficam pendentes da análise manual e preenchimento pela Coordenação.

- **Pós-condições:**
    - O relatório é anexado ao histórico do processo do aluno.

- **Regras de Negócio:**
    - A aprovação ou reprovação automática do relatório depende do resultado da análise da IA cruzado com o arquivo `ementa_md` associado ao Curso do aluno (condicionado à Feature Flag ativada).