---
id: brainstorm
title: Brainstorm
---

## 🚀 Introdução

O brainstorming é uma técnica de elicitação de requisitos que consiste em reunir a equipe e discutir sobre diversos tópicos gerais do projeto apresentados no documento problema de negócio. No brainstorming o diálogo é incentivado e críticas são evitadas para permitir que todos colaborem com suas próprias ideias.

---

## 🛠️ Metodologia

A equipe se reuniu por chamada no **Discord** para debater ideias gerais sobre o projeto. A sessão começou com uma apresentação rápida do problema central — a gestão manual de documentos de estágio na Secretaria do Ibmec — e terminou com um conjunto claro de ideias e direções para o desenvolvimento. **Caio** foi o moderador, direcionando a equipe com questões pré-elaboradas, e transcrevendo as respostas para o documento.

---

## 🧠 Brainstorm

- Marcador visual de erros no contrato, destacando em vermelho os campos incorretos ou ausentes
- Integração com LLM para pesquisar o histórico da empresa e analisar automaticamente o contrato
- Notificações automáticas por e-mail para o aluno e a secretaria sobre o status do documento
- Painel de acompanhamento do processo de estágio com status visual, similar ao rastreio de pedidos do Mercado Livre
- Upload de documentos diretamente pelo aluno via plataforma, sem precisar ir presencialmente
- Botão de reenvio do contrato após reprovação, sem precisar abrir novo processo
- Busca de alunos por nome ou matrícula para facilitar o trabalho da secretaria
- Tela de avaliação exclusiva para a secretaria com opções de validar, reprovar e adicionar mensagem de aviso
- Documentar todas as rotas da API para facilitar a manutenção futura

---

## 📋 Versão 1.0

---

## ❓ Perguntas

### 1. Qual o objetivo principal da aplicação?

**Bernardo** - Deve ser uma plataforma onde alunos possam **gerenciar e enviar** contratos de estágio para validação pela Secretaria do Ibmec.

**Caio** - A plataforma deve fornecer o envio de contratos, a **certificação de validação**, o **armazenamento dos documentos** durante todo o período do aluno e a visualização do contrato.

**Daniel** - O objetivo da aplicação é **gerenciar e validar** contratos de estágio de forma centralizada.

**Lucas** - O principal objetivo da aplicação é a **automação** da validação básica dos contratos, reduzindo o trabalho manual e repetitivo da secretaria.

**Otto** - A plataforma deve gerenciar o ciclo completo do documento, desde o envio pela empresa até a aprovação final pela secretaria.

---

### 2. Como o aluno vai submeter os documentos?

**Bernardo** - O aluno faz login com matrícula e senha e acessa a tela de documentos para fazer o upload do contrato diretamente pela plataforma.

**Caio** - O processo deve ser simples: entrar na plataforma, anexar o arquivo e enviar. O aluno precisa conseguir acompanhar o status do contrato em tempo real.

**Daniel** - O aluno deve poder reenviar o documento corrigido caso ele seja reprovado, sem precisar abrir um novo processo do zero.

**Lucas** - A tela de documentos deve mostrar claramente o status de cada envio, como "Em análise", "Aprovado" ou "Reprovado com justificativa".

**Otto** - O aluno precisa conseguir baixar o contrato validado depois que for aprovado, como comprovante oficial do estágio.

---

### 3. Como a Secretaria vai validar os contratos?

**Bernardo** - A secretaria acessa uma tela com todos os contratos pendentes e pode aprovar ou reprovar cada um, com a opção de adicionar uma mensagem explicando o motivo caso reprove.

**Caio** - A tela de avaliação deve ser uma extensão da tela de detalhes do documento, com os botões de validar, reprovar e adicionar mensagem de aviso opcional.

**Daniel** - A IA pode fazer uma pré-análise automática do contrato antes de chegar para a secretaria, marcando possíveis erros em vermelho para agilizar a revisão.

**Lucas** - A secretaria precisa de uma tela de busca para encontrar alunos por nome ou matrícula e consultar o histórico de documentos de cada um.

**Otto** - Seria útil ter um histórico das empresas que já enviaram contratos, para facilitar validações futuras de contratos da mesma empresa.

---

### 4. Quais telas o sistema precisa ter?

**Bernardo** - Tela de login com matrícula e senha, com opção de recuperação de senha como funcionalidade desejável.

**Caio** - Tela de documentos mostrando nome e status de cada contrato enviado, com filtro por status como funcionalidade desejável.

**Daniel** - Tela de detalhes do documento com todas as informações da validação, justificativa em caso de erro, botão de download e botão de reenvio.

**Lucas** - Tela de perfil com as informações do usuário e tela de avaliação exclusiva para a secretaria.

**Otto** - Tela da secretaria para receber documentos das empresas estagiárias e tela de busca de alunos por nome ou matrícula.

---

### 5. O que acontece se o contrato for reprovado?

**Bernardo** - O aluno recebe uma notificação e consegue ver na plataforma o motivo da reprovação com o que precisa corrigir.

**Caio** - O aluno deve poder reenviar o contrato corrigido pelo mesmo fluxo, sem abrir um novo chamado.

**Daniel** - O sistema deve guardar o histórico de todas as versões enviadas, mesmo as reprovadas, para ter rastreabilidade completa do processo.

**Lucas** - A secretaria precisa conseguir ver quantas vezes um contrato foi reprovado para identificar problemas recorrentes com determinados alunos ou empresas.

**Otto** - Um e-mail automático avisando o aluno da reprovação, com a justificativa incluída, ajudaria muito a agilizar a correção.

---

## ✅ Conclusão

Através da aplicação da técnica, foi possível elicitar as primeiras ideias e direções do projeto. A equipe chegou a um consenso sobre os principais fluxos da aplicação: o envio e validação de contratos de estágio, o acompanhamento do status pelo aluno e as ferramentas de gestão para a secretaria. Essas ideias servirão de base para as próximas etapas de elaboração e desenvolvimento.

---

## 📚 Referências Bibliográficas

> BARBOSA, S. D. J; DA SILVA, B. S. *Interação humano-computador*. Elsevier, 2010.

---

## 👥 Autor(es)

| Data | Versão | Descrição | Autor(es) |
|------|--------|-----------|-----------|
| 11/04/26 | 1.0 | Criação do documento | Lucas Jesus, Otto Balestrassi, Caio Ximenes, Bernardo Esteves e Daniel Alberto |
