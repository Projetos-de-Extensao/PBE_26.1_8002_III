---
id: analisar_contrato
title: Analisar/Visualizar Contrato
---

### Analisar Contrato (Visualização)

- **Atores:**
    - Secretaria
    - Sistema

- **Pré-Condições:**
    - O processo deve ter um arquivo PDF válido anexado.

- **Fluxo Básico:**
    1. Secretaria clica no nome do contrato anexado pelo aluno.
    2. Sistema renderiza o PDF em um visualizador integrado dentro do navegador (iframe/canvas).
    3. Secretaria faz a leitura do contrato sem precisar baixar.

- **Fluxos Alternativos:**
    - **2a. Navegador não suporta visualização nativa**
        - 2a1. Sistema força o download automático do arquivo.

- **Pós-condições:**
    - Contrato exibido em tela.

- **Regras de Negócio:**
    - O visualizador deve permitir controle de zoom e rolagem para conferência minuciosa de assinaturas.