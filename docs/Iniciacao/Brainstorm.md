---
id: brainstorm
title: Brainstorm
---

# 🧠 Brainstorming e Elicitação de Requisitos

---

## 🚀 Introdução
O brainstorming é uma técnica de elicitação de requisitos que consiste em reunir a equipe e discutir sobre diversos tópicos gerais do projeto apresentados no documento problema de negócio. No brainstorming o diálogo é incentivado e críticas são evitadas para possibilitar que todos colaborem com suas próprias ideias.

---

## 🛠️ Metodologia
A equipe se reuniu por chamada no **Discord** para debater ideias gerais sobre o projeto. A sessão começou com uma apresentação rápida do problema central — a gestão manual de documentos de estágio na Secretaria do Ibmec — e terminou com um conjunto claro de ideias e direções para o desenvolvimento. **Caio** atuou como moderador, direcionando a equipe com questões pré-elaboradas e transcrevendo as respostas para o documento.

---

## 💡 Ideias Levantadas
Durante a sessão livre, a equipe listou as seguintes funcionalidades e conceitos:

* **Marcador visual de erros:** Destacar em vermelho os campos incorretos ou ausentes no contrato.
* **Integração com IA (LLM):** Pesquisar o histórico da empresa e analisar automaticamente o contrato.
* **Notificações automáticas:** Disparo de e-mails para o aluno e a secretaria sobre o status do documento.
* **Painel de acompanhamento (Tracking):** Status visual do processo de estágio, similar ao rastreio de pedidos do Mercado Livre.
* **Upload remoto:** Envio de documentos diretamente pelo aluno via plataforma, eliminando a entrega presencial.
* **Fluxo de reenvio:** Botão dedicado para reenviar o contrato após reprovação, sem precisar abrir um novo processo do zero.
* **Busca otimizada:** Filtro de alunos por nome ou matrícula para facilitar o trabalho da secretaria.
* **Tela de avaliação exclusiva:** Painel da secretaria com opções ágeis de validar, reprovar e adicionar mensagens de aviso.
* **Documentação técnica:** Documentar todas as rotas da API para facilitar a manutenção futura.

---

## ❓ Perguntas Direcionadas

### 1. Qual o objetivo principal da aplicação?
* **Bernardo:** Deve ser uma plataforma onde alunos possam gerenciar e enviar contratos de estágio para validação.
* **Caio:** Fornecer o envio de contratos, a certificação de validação, o armazenamento dos documentos durante todo o curso e a visualização do contrato.
* **Daniel:** Gerenciar e validar contratos de estágio de forma centralizada.
* **Lucas:** A automação da validação básica dos contratos, reduzindo o trabalho manual e repetitivo da secretaria.
* **Otto:** Gerenciar o ciclo completo do documento, desde o envio pela empresa até a aprovação final pela secretaria.

### 2. Como o aluno vai submeter os documentos?
* **Bernardo:** Faz login com matrícula e senha e acessa a tela de documentos para fazer o upload diretamente pela plataforma.
* **Caio:** O processo deve ser simples: entrar na plataforma, anexar o arquivo e enviar. O aluno precisa acompanhar o status em tempo real.
* **Daniel:** O aluno deve poder reenviar o documento corrigido caso seja reprovado, sem precisar abrir um novo processo.
* **Lucas:** A tela deve mostrar claramente o status de cada envio (ex: "Em análise", "Aprovado", "Reprovado com justificativa").
* **Otto:** Precisa conseguir baixar o contrato validado após a aprovação, servindo como comprovante oficial.

### 3. Como a Secretaria vai validar os contratos?
* **Bernardo:** Acessa uma tela com os contratos pendentes, podendo aprovar ou reprovar, com opção de adicionar justificativa.
* **Caio:** A tela de avaliação deve ser uma extensão da tela de detalhes, com botões rápidos de validação e avisos.
* **Daniel:** A IA faria uma pré-análise antes de chegar na secretaria, marcando possíveis erros em vermelho para agilizar a revisão.
* **Lucas:** Precisam de uma busca para encontrar alunos por matrícula/nome e consultar o histórico de envios.
* **Otto:** Seria útil um histórico das empresas conveniadas, facilitando validações futuras da mesma instituição.

### 4. Quais telas o sistema precisa ter?
* **Bernardo:** Login com matrícula/senha (com recuperação de senha como funcionalidade desejável).
* **Caio:** Tela de documentos mostrando nome/status de cada contrato (com filtros como funcionalidade desejável).
* **Daniel:** Tela de detalhes do documento (validação, justificativas, download e reenvio).
* **Lucas:** Tela de perfil do usuário e um painel de avaliação exclusivo para a secretaria.
* **Otto:** Dashboard da secretaria para receber documentos e a tela de busca de alunos.

### 5. O que acontece se o contrato for reprovado?
* **Bernardo:** O aluno recebe notificação e vê na plataforma o motivo da reprovação e o que corrigir.
* **Caio:** Poder reenviar o contrato corrigido pelo mesmo fluxo original.
* **Daniel:** O sistema deve guardar o histórico de todas as versões (mesmo reprovadas) para garantir rastreabilidade.
* **Lucas:** A secretaria precisa ver quantas vezes um contrato foi reprovado para mapear problemas recorrentes.
* **Otto:** Um e-mail automático avisando o aluno da reprovação, já incluindo a justificativa da secretaria.

---

## ✅ Conclusão
Através da aplicação da técnica, foi possível elicitar as primeiras ideias e direções do projeto. A equipe chegou a um consenso sobre os principais fluxos da aplicação: o envio e validação de contratos de estágio, o acompanhamento do status pelo aluno e as ferramentas de gestão para a secretaria. Essas ideias servirão de base para as próximas etapas de elaboração e desenvolvimento.

---

## 📚 Referências Bibliográficas

> BARBOSA, S. D. J; DA SILVA, B. S. *Interação humano-computador*. Elsevier, 2010.

---

## 👥 Histórico de Versões

| Data | Versão | Descrição | Autor(es) |
|------|--------|-----------|-----------|
| 11/04/26 | 1.0 | Criação do documento | Lucas Jesus, Otto Balestrassi, Caio Ximenes, Bernardo Esteves e Daniel Alberto |