# Manual do Usuário — Portal de Gestão de Estágios Ibmec

Este manual descreve todas as funcionalidades do portal de **Gestão de Estágios do Ibmec**. O sistema foi concebido para automatizar e otimizar o fluxo de envio, validação e acompanhamento de Termos de Compromisso de Estágio (TCE) e Relatórios de Atividades.

O portal possui três perfis de acesso (**Aluno**, **Secretaria** e **Coordenador**) com fluxos integrados ao backend Django e validações inteligentes.

---

## Sumário
1. [Acesso à Plataforma e Login](#1-acesso-a-plataforma-e-login)
2. [Fluxo do Aluno](#2-fluxo-do-aluno)
    - [Painel Principal (Sem Estágio Ativo)](#painel-principal-sem-estagio-ativo)
    - [Iniciar Novo Processo (Upload de TCE)](#iniciar-novo-processo-upload-de-tce)
    - [Painel Principal (Com Estágio Ativo)](#painel-principal-com-estagio-ativo)
    - [Detalhes do Contrato](#detalhes-do-contrato)
    - [Enviar Relatório de Atividades](#enviar-relatorio-de-atividades)
    - [Detalhes do Relatório](#detalhes-do-relatorio)
    - [Perfil do Aluno](#perfil-do-aluno)
3. [Fluxo da Secretaria](#3-fluxo-da-secretaria)
    - [Caixa de Entrada de Avaliação de Contratos](#caixa-de-entrada-de-avaliacao-de-contratos)
    - [Aprovação e Reprovação de Contratos](#aprovacao-e-reprovacao-de-contratos)
    - [Gestão de Alunos (Listagem e Cadastro)](#gestao-de-alunos-listagem-e-cadastro)
4. [Fluxo do Coordenador](#4-fluxo-do-coordenador)
    - [Fila de Pendências e Avaliação de Relatórios](#fila-de-pendencias-e-avaliacao-de-relatorios)
    - [Histórico do Coordenador](#historico-do-coordenador)
5. [Recursos de Integração e Segurança](#5-recursos-de-integracao-e-seguranca)

---

## 1. Acesso à Plataforma e Login

A página inicial do portal exibe a tela de login unificada da demonstração. Aqui o usuário pode escolher entre os três perfis disponíveis. O sistema realiza a autenticação gerando tokens JWT no backend e direciona o usuário para o seu painel específico.

### Onde tirar o print:
> **Instrução para Print 1:** Tire um print da tela inicial de login (caminho `/`), mostrando o painel esquerdo com a logo do Ibmec ("Da entrega manual à validação em poucos cliques") e o painel direito com os três botões grandes de seleção de perfil ("Entrar como Aluno", "Entrar como Secretaria" e "Entrar como Coordenador").
>
> **[INSERIR PRINT 1: Tela de Login Unificada]**

### Como acessar:
1. Acesse o endereço principal do sistema (ex: `http://localhost:5173/`).
2. Clique no perfil desejado para simular o login e carregar as permissões adequadas.
3. Se desejar limpar a demonstração e recomeçar, utilize o botão **"Resetar dados da demo"** localizado no rodapé da página.

---

## 2. Fluxo do Aluno

O perfil do Aluno é voltado para o envio de documentos de estágio e para o monitoramento transparente das fases do processo.

### Painel Principal (Sem Estágio Ativo)
Caso o aluno ainda não tenha um estágio em andamento no sistema, ele verá uma tela convidando-o a iniciar um processo.

#### Onde tirar o print:
> **Instrução para Print 2:** Logue como Aluno. Com a base de dados zerada (sem processos), tire um print da tela principal do dashboard (`/dashboard/aluno`), evidenciando a mensagem central "Você não possui processos de estágio ativos" e o botão azul "Iniciar Processo".
>
> **[INSERIR PRINT 2: Painel do Aluno Sem Processos]**

---

### Iniciar Novo Processo (Upload de TCE)
Para registrar um novo estágio, o aluno clica no botão "Iniciar Processo". Um pop-up (modal) solicita os dados necessários:
- **Nome da empresa concedente**: Nome da empresa onde será realizado o estágio.
- **Termo de Compromisso (TCE)**: Arquivo em PDF correspondente ao contrato.

#### Onde tirar o print:
> **Instrução para Print 3:** Clique em "Iniciar Processo" no painel do Aluno. Tire um print do modal aberto mostrando o campo de digitação da empresa concedente e a área pontilhada de drag-and-drop para arrastar o PDF do contrato.
>
> **[INSERIR PRINT 3: Modal de Início de Processo]**

---

### Painel Principal (Com Estágio Ativo)
Após iniciar o processo, a tela principal do aluno é atualizada para exibir:
1. **Card Superior de Destaque**: Contém o nome da empresa, curso, número do processo e status geral (Ex: *Pendente*, *Em Andamento*, *Aprovado*, *Reprovado*).
2. **Linha do Tempo (Timeline)**: Mostra as fases do estágio (Processo iniciado $\rightarrow$ Contrato enviado $\rightarrow$ Validação da Secretaria $\rightarrow$ Estágio em andamento $\rightarrow$ Relatórios entregues $\rightarrow$ Estágio concluído). As fases concluídas ficam destacadas em azul (ou vermelho se houver pendências).
3. **Seção "Contratos do Estágio"**: Exibe um card clicável para o contrato enviado, detalhando o status de análise da Secretaria.
4. **Seção "Relatórios do Estágio"**: Exibe a lista de relatórios de atividades enviados ou a opção de envio (bloqueada até que o contrato seja aprovado).
5. **Histórico do Processo**: Linha do tempo textual com o log de todos os eventos cronológicos do processo.

#### Onde tirar o print:
> **Instrução para Print 4:** Após o envio do contrato, tire um print do dashboard atualizado do aluno (`/dashboard/aluno`). Mostre a timeline do processo e o card do contrato recém-enviado com o status "Pendente".
>
> **[INSERIR PRINT 4: Dashboard do Aluno com Estágio Ativo]**

---

### Detalhes do Contrato
Ao clicar no card do contrato, o aluno é direcionado para a página de detalhes, onde visualiza:
- Uma pré-visualização completa em PDF (via *iframe* integrado).
- Um painel lateral com dados extraídos do documento (Empresa concedente, Data de envio, Data de início, Número de apólice de seguro).
- Histórico de avaliações próprio do documento.
- Caso o contrato seja **Reprovado**, um card vermelho em destaque exibe a **justificativa da reprovação** redigida pela Secretaria para que o aluno saiba o que precisa corrigir.

#### Onde tirar o print:
> **Instrução para Print 5:** Acesse a rota de detalhe do contrato do aluno (`/dashboard/aluno/contrato/[id]`). Capture a tela mostrando a pré-visualização do PDF na esquerda e a barra lateral de metadados à direita.
>
> **[INSERIR PRINT 5: Detalhes do Contrato com Preview PDF]**

---

### Enviar Relatório de Atividades
Uma vez que o contrato é aprovado pela Secretaria, o status do processo muda para **"Em Andamento"**. Isso habilita o botão **"Adicionar Relatório"** na seção correspondente. O aluno pode então preencher o modal informando:
- **Título do relatório** (Ex: Relatório Bimestral 1).
- **Arquivo PDF** com as atividades realizadas.

#### Onde tirar o print:
> **Instrução para Print 6:** Com o estágio em status "Em Andamento", clique em "Adicionar Relatório". Tire um print do modal aberto mostrando o campo de título e o componente de upload de PDF.
>
> **[INSERIR PRINT 6: Modal de Envio de Relatório]**

---

### Detalhes do Relatório
Assim como no contrato, o aluno pode clicar no card do relatório para abrir uma tela de detalhamento com o preview do arquivo físico, dados de prazo (no prazo ou com atraso), e o parecer/histórico de avaliações do Coordenador.

#### Onde tirar o print:
> **Instrução para Print 7:** Abra a tela de detalhe do relatório (`/dashboard/aluno/relatorio/[procId]/[relatId]`). Tire um print mostrando a tela com a pré-visualização do relatório.
>
> **[INSERIR PRINT 7: Detalhes do Relatório com Preview PDF]**

---

### Perfil do Aluno
Na barra lateral, ao clicar no nome do aluno, abre-se a página de perfil (`/perfil`). Esta página exibe dados organizados em três seções:
- **Informações Pessoais**: Nome completo, matrícula, CPF, e-mail e unidade (campus).
- **Informações Acadêmicas**: Curso atual, período letivo, status da matrícula e grade horária.
- **Status da Conta**: Termo de aceite da LGPD/Uso e status de redefinição de senha.
- **Ações Rápidas**: Atalhos para visualizar processos, grade horária ou atualizar senha.

#### Onde tirar o print:
> **Instrução para Print 8:** Navegue para a tela de Perfil do Aluno (`/perfil`). Tire um print exibindo a organização dos cards de informações pessoais, acadêmicas e as ações rápidas.
>
> **[INSERIR PRINT 8: Perfil do Aluno]**

---

## 3. Fluxo da Secretaria

O perfil da Secretaria realiza a validação documental inicial dos estágios (aprovação/reprovação de contratos) e faz a gestão dos registros dos alunos.

### Caixa de Entrada de Avaliação de Contratos
Ao entrar como Secretaria, o usuário é direcionado para a Caixa de Entrada. O painel é dividido em duas colunas:
1. **Coluna Esquerda (Fila de Trabalho)**:
    - **Filtros superiores**: Permite alternar a visualização entre "Todos", "Pendente", "Em Andamento", "Aprovado" e "Reprovado".
    - **Aba Fila / Aba Meu Histórico**: Alterna entre os processos pendentes gerais e o log pessoal de decisões tomadas pelo usuário logado.
    - **Barra de Busca**: Campo de pesquisa de alunos por nome ou matrícula.
2. **Coluna Direita (Visualização de Detalhes)**:
    - Exibe o nome do aluno selecionado, matrícula, curso e empresa.
    - Traz o arquivo de contrato (com visualização mockada ou download do PDF real do backend).
    - Metadados do contrato e a timeline específica de logs do processo selecionado.

#### Onde tirar o print:
> **Instrução para Print 9:** Logue como Secretaria e acesse a Caixa de Entrada (`/inbox/avaliador`). Tire um print da interface em duas colunas, destacando a lista de processos na esquerda e a visualização do contrato selecionado na direita.
>
> **[INSERIR PRINT 9: Caixa de Entrada da Secretaria]**

---

### Aprovação e Reprovação de Contratos
No painel de detalhes da Secretaria (na coluna da direita), caso o contrato selecionado esteja com status **"Pendente"**, botões de ação são disponibilizados no rodapé:
- **Aprovar**: Altera o status do contrato para "Aprovado" e inicia oficialmente o estágio do aluno (status do processo vai para "Em Andamento"). O aluno recebe uma notificação por e-mail automaticamente.
- **Reprovar / Solicitar Ajuste**: Ao clicar, um campo de texto é exibido para que a Secretaria justifique os motivos da rejeição (Ex: "Assinatura da testemunha ausente"). O status muda para "Reprovado", e o aluno é notificado para que providencie as correções necessárias.

#### Onde tirar o print:
> **Instrução para Print 10:** Selecione um processo pendente como Secretaria. Tire um print da parte inferior do painel lateral mostrando os botões "Aprovar" e "Reprovar / Solicitar Ajuste".
>
> **[INSERIR PRINT 10: Botões de Ação de Avaliação]**

> **Instrução para Print 11:** Clique em "Reprovar / Solicitar Ajuste". Capture a tela exibindo a caixa de texto "Justificativa da reprovação" aberta, pronta para digitação do parecer.
>
> **[INSERIR PRINT 11: Campo de Justificativa de Reprovação]**

---

### Gestão de Alunos (Listagem e Cadastro)
A Secretaria tem acesso exclusivo ao menu **"Gestão de Alunos"** (`/alunos`). Nesta tela, é possível:
1. **Visualizar a tabela de alunos**: Lista todos os alunos cadastrados com colunas de Nome, Matrícula, Curso e E-mail.
2. **Consultar detalhes individuais**: Através das opções de ações de cada linha da tabela (ícone de três pontos), pode-se abrir o modal de "Detalhes do Aluno" ou "Processos do Aluno" (histórico de estágios e relatórios vinculados àquele CPF/matrícula).
3. **Cadastrar Novo Aluno**: Abre um modal de formulário completo com validação de campos (incluindo algoritmo oficial da Receita Federal para validação do CPF).

#### Onde tirar o print:
> **Instrução para Print 12:** Navegue até a página de Gestão de Alunos (`/alunos`). Tire um print da tabela de listagem de alunos cadastrados, mostrando a barra de busca e o botão "Novo Aluno".
>
> **[INSERIR PRINT 12: Tela de Gestão de Alunos]**

> **Instrução para Print 13:** Clique no botão "Novo Aluno" no topo direito da tabela. Tire um print do modal aberto exibindo o formulário de cadastro de dados do aluno.
>
> **[INSERIR PRINT 13: Modal de Cadastro de Novo Aluno]**

---

## 4. Fluxo do Coordenador

O perfil do Coordenador é focado na avaliação acadêmica técnica. O coordenador analisa relatórios de atividades para validar se a experiência de estágio condiz com o curso.

### Fila de Pendências e Avaliação de Relatórios
Diferente da Secretaria (que tem acesso irrestrito a todos os status), a Caixa de Entrada do Coordenador (`/inbox/coordenador`) exibe por padrão **apenas os processos que possuem documentos pendentes de análise**.
- O fluxo de avaliação de relatórios é análogo ao de contratos: o Coordenador revisa o PDF do relatório, checa os dados de prazo (se o aluno entregou no prazo correto), e decide no rodapé pela **Aprovação** (conclui o estágio com sucesso) ou **Reprovação/Solicitação de Ajuste** (cancela ou retorna o processo ao aluno com a devida justificativa).

#### Onde tirar o print:
> **Instrução para Print 14:** Logue como Coordenador e exiba a página de Fila de Pendências (`/inbox/coordenador`). Tire um print demonstrando a interface limpa, focada apenas nos processos que exigem ação imediata.
>
> **[INSERIR PRINT 14: Fila de Pendências do Coordenador]**

---

### Histórico do Coordenador
Na mesma tela, o Coordenador pode alternar para a aba **"Meu Histórico"** para consultar relatórios anteriormente validados por ele, registrando a data e o veredito emitido para fins de auditoria acadêmica.

#### Onde tirar o print:
> **Instrução para Print 15:** Na tela do Coordenador, clique na aba "Meu Histórico" na coluna esquerda. Capture a tela exibindo os registros das avaliações passadas executadas pela coordenação.
>
> **[INSERIR PRINT 15: Histórico de Avaliações do Coordenador]**

---

## 5. Recursos de Integração e Segurança

A plataforma conta com mecanismos de retaguarda essenciais descritos a seguir:

1. **Prevenção de Vulnerabilidade BOLA (Broken Object Level Authorization)**:
   O backend Django possui verificações rígidas de permissão. Se um Aluno tentar forçar um ID de processo na URL que pertence a outro estudante, o sistema bloqueia o acesso imediatamente, retornando código `403 Forbidden`. A Secretaria tem acesso completo, e os Coordenadores são limitados apenas a alunos de seus respectivos cursos vinculados.
2. **Integração com IA Generativa (Celery background tasks)**:
   Ao enviar documentos, o backend aciona tarefas em segundo plano (`async_contract_ai` e `async_report_ai`) que realizam a pré-leitura automática do PDF para auxiliar os avaliadores.
3. **Serviço de Notificações por E-mail**:
   A cada upload de documento ou alteração de veredito (Aprovado/Reprovado), e-mails automáticos de notificação são disparados aos envolvidos no processo para reduzir o tempo de espera.
