# 📋 Levantamento de Tasks — API de Gestão de Estágios

> Extraído dos **11 documentos de caso de uso** e dos documentos de **Iniciação** (5W2H, Brainstorm, Pesquisa).

---

## Resumo do Projeto

A API gerencia toda a burocracia na relação **IES ↔ Aluno** para validação do **estágio obrigatório**. Utiliza **Python/Django**, banco relacional, armazenamento de PDFs e integração com IA para pré-análise de contratos (TCE) e relatórios.

**Atores:** Aluno, Secretaria, Coordenação (e futuramente Carreiras)

> **Legenda:**
> 📌 - Task já adicionada como Issue no GitHub Project.

---

## 🔐 Módulo 1 — Autenticação & Segurança
*Fonte: [fazer_login.md](file:///home/caio/Documentos/projetos/PBE_26.1_8002_III/docs/Elaboracao/Casos%20de%20Uso/fazer_login.md)*

| # | Task | Detalhes |
|---|------|----------|
| 1.1 | 📌 **Criar modelo `Usuario` (abstrato)** | Campos: `matricula`, `nome`, `email`, `senha`, `unidade` (Enum). Classes filhas: `Aluno`, `Secretaria`, `Coordenacao`. |
| 1.2 | 📌 **Endpoint `POST /auth/login`** | Autentica via e-mail institucional (ou matrícula) + senha. Retorna token JWT. |
| 1.3 | **Validar credenciais no banco** | Verificar se o cadastro está ativo. |
| 1.4 | **Bloqueio após 5 tentativas** | Implementar rate-limiting ou lockout temporário após 5 falhas consecutivas. |
| 1.5 | **Criptografia de senhas** | Hash com bcrypt/argon2 no armazenamento e tráfego via HTTPS. |
| 1.6 | **Fluxo de primeiro acesso** | Redirecionar para redefinição de senha obrigatória no primeiro login. |
| 1.7 | **Middleware de autenticação** | Validar JWT em todas as rotas protegidas. |
| 1.8 | **Middleware de autorização por perfil** | Separar permissões: Aluno, Secretaria, Coordenação. |

---

## 👨‍🎓 Módulo 2 — Gestão de Alunos (CRUD)
*Fonte: [cadastrar_aluno.md](file:///home/caio/Documentos/projetos/PBE_26.1_8002_III/docs/Elaboracao/Casos%20de%20Uso/cadastrar_aluno.md)*

| # | Task | Detalhes |
|---|------|----------|
| 2.1 | 📌 **Criar modelo `Aluno`** | Campos: `nome`, `matricula`, `cpf`, `curso`, `email`, `periodo`, `processoAtual` (0..1). Herda de `Usuario`. |
| 2.2 | 📌 **Endpoint `POST /alunos`** | Cadastro de novo aluno (ator: Secretaria). |
| 2.3 | **Validação de unicidade** | CPF e Matrícula únicos no banco. |
| 2.4 | **Validação de CPF** | Algoritmo padrão da Receita Federal. |
| 2.5 | **Validação de e-mail** | Formato válido (contém `@` e domínio). |
| 2.6 | **Endpoint `GET /alunos/:id`** | Detalhes de um aluno específico + histórico de estágios. |

---

## 🔄 Módulo 3 — Processo de Estágio
*Fonte: [iniciar_processo.md](file:///home/caio/Documentos/projetos/PBE_26.1_8002_III/docs/Elaboracao/Casos%20de%20Uso/iniciar_processo.md)*

| # | Task | Detalhes |
|---|------|----------|
| 3.1 | 📌 **Criar modelo `Processo`** | Campos: `processoId`, `dataCriacao`, `status` (Enum StatusProcesso), FK para `Aluno`. |
| 3.2 | **Criar Enum `StatusProcesso`** | Valores: `ABERTO`, `EM_ANALISE_SECRETARIA`, `EM_ANALISE_COORDENACAO`, `PENDENTE_AJUSTE`, `APROVADO`, `REPROVADO`, `CONCLUIDO`, `CANCELADO`. |
| 3.3 | **Endpoint `POST /processos`** | Cria novo processo. Recebe CNPJ da empresa, datas, carga horária e arquivo TCE. |
| 3.4 | **Validar conflito de processos** | Aluno não pode ter dois processos "Em Andamento" conflitantes (restrição 0..1). |
| 3.5 | **Validar formato de arquivo** | Somente `.pdf`, deve ter limitação de tamanho. |
| 3.6 | **Validar campos obrigatórios** | Destacar campos faltantes no retorno de erro. |
| 3.7 | **Status inicial = `PENDENTE DE ANÁLISE`** | Setar automaticamente ao criar. |
| 3.8 | **Endpoint para Secretaria criar processo em nome do aluno** | Se ator = Secretaria, exigir seleção de matrícula do aluno. |
| 3.9 | **Validar data de término** | Não pode ultrapassar a previsão de formatura do aluno. |

---

## 📎 Módulo 4 — Upload & Armazenamento de Documentos
*Fonte: [anexar_contrato.md](file:///home/caio/Documentos/projetos/PBE_26.1_8002_III/docs/Elaboracao/Casos%20de%20Uso/anexar_contrato.md)*

| # | Task | Detalhes |
|---|------|----------|
| 4.1 | 📌 **Criar modelo `Contrato`** | Campos: `dataInicio`, `dataTermino`, `cnpjEmpresa`, `nomeEmpresa`, `apoliceSeguro`, `planoAtividade`, `assinaturaAluno`, `assinaturaEmpresa`, `assinaturaFaculdade`, `arquivoUrl`, `versao`. |
| 4.2 | **Serviço de upload de PDF** | Validar MIME type (`application/pdf`) e tamanho (≤Limite). |
| 4.3 | **Integrar storage (ex: AWS S3)** | Armazenar PDFs com URLs protegidas. |
| 4.4 | **Controle de versionamento de documentos** | Ao receber novo upload no mesmo processo: arquivar anterior (`status = obsoleto`) e incrementar `versão_atual`. |
| 4.5 | **Buffer temporário pré-submissão** | Arquivo em memória até submissão final do formulário. |

---

## 📊 Módulo 5 — Acompanhamento de Status
*Fonte: [acompanhar_status.md](file:///home/caio/Documentos/projetos/PBE_26.1_8002_III/docs/Elaboracao/Casos%20de%20Uso/acompanhar_status.md)*

| # | Task | Detalhes |
|---|------|----------|
| 5.1 | **Endpoint `GET /processos` (Aluno)** | Listar processos do aluno autenticado com status atualizado. |
| 5.2 | **Endpoint `GET /processos` (Secretaria)** | Listar processos de todos os alunos (filtros por status, matrícula, etc). |
| 5.3 | **Endpoint `GET /processos/:id`** | Detalhes completos + histórico de movimentações do processo. |
| 5.4 | **Filtro de permissão** | Aluno vê apenas seus processos; Secretaria vê todos. |
| 5.5 | **Resposta para "sem processos"** | Retornar mensagem adequada quando não há processos. |

---

## 📝 Módulo 6 — Relatórios de Horas
*Fonte: [enviar_relatorio.md](file:///home/caio/Documentos/projetos/PBE_26.1_8002_III/docs/Elaboracao/Casos%20de%20Uso/enviar_relatorio.md)*

| # | Task | Detalhes |
|---|------|----------|
| 6.1 | **Criar modelo `Relatorio`** | Campos: `horasTrabalhadas`, `periodoReferencia`, `aprovadoPelaEmpresa` (boolean), `arquivoUrl`, FK para `Processo`. |
| 6.2 | **Endpoint `POST /processos/:id/relatorios`** | Aluno envia relatório com período, horas e PDF assinado. |
| 6.3 | **Pré-condição: processo "Em Andamento"** | Validar que o processo está ativo antes de permitir envio. |
| 6.4 | **Validar horas vs. TCE** | Total de horas reportadas não pode exceder o estipulado no contrato. |
| 6.5 | **Flag de envio fora do prazo** | Marcar relatórios atrasados com flag, mas permitir envio com alerta. |
| 6.6 | **Status do relatório = "Aguardando Validação"** | Setar automaticamente ao criar. |

---

## ⬇️ Módulo 7 — Download de Documentos
*Fonte: [fazer_download.md](file:///home/caio/Documentos/projetos/PBE_26.1_8002_III/docs/Elaboracao/Casos%20de%20Uso/fazer_download.md)*

| # | Task | Detalhes |
|---|------|----------|
| 7.1 | **Endpoint `GET /documentos/:id/download`** | Stream do PDF para o dispositivo do usuário. |
| 7.2 | **URL protegida** | Tokens temporários ou validação de sessão para evitar acesso público. |
| 7.3 | **Tratamento de arquivo indisponível** | Retornar erro 404 com mensagem clara se arquivo corrompido ou ausente. |

---

## 🔍 Módulo 8 — Pesquisa de Alunos
*Fonte: [pesquisar_alunos.md](file:///home/caio/Documentos/projetos/PBE_26.1_8002_III/docs/Elaboracao/Casos%20de%20Uso/pesquisar_alunos.md)*

| # | Task | Detalhes |
|---|------|----------|
| 8.1 | **Endpoint `GET /alunos/search`** | Busca por nome, CPF ou matrícula. |
| 8.2 | **Busca parcial/fonética** | Implementar buscas parciais (ex: apenas primeiro nome) e aproximações fonéticas. |
| 8.3 | **Restrição de acesso** | Apenas perfil Secretaria ou Coordenação. |
| 8.4 | **Resposta para "nenhum resultado"** | Mensagem clara + sugestão de limpar filtros. |

---

## 👁️ Módulo 9 — Análise/Visualização de Contratos
*Fonte: [analisar_contrato.md](file:///home/caio/Documentos/projetos/PBE_26.1_8002_III/docs/Elaboracao/Casos%20de%20Uso/analisar_contrato.md)*

| # | Task | Detalhes |
|---|------|----------|
| 9.1 | **Endpoint `GET /contratos/:id/preview`** | Retornar PDF para renderização in-browser (iframe/canvas). |
| 9.2 | **Fallback para download** | Se o navegador não suportar visualização nativa, forçar download. |
| 9.3 | **Suporte a zoom e rolagem** | Garantir que a API forneça o PDF de forma otimizada para visualização detalhada. |

---

## ✅ Módulo 10 — Validação de Contratos
*Fonte: [validar_contrato.md](file:///home/caio/Documentos/projetos/PBE_26.1_8002_III/docs/Elaboracao/Casos%20de%20Uso/validar_contrato.md)*

| # | Task | Detalhes |
|---|------|----------|
| 10.1 | **Endpoint `GET /processos?status=pendente`** | Listar fila de contratos pendentes de análise. |
| 10.2 | **Endpoint `PATCH /processos/:id/aprovar`** | Secretaria aprova o contrato → status = `APROVADO`. |
| 10.3 | **Registrar avaliador e timestamp** | Gravar quem avaliou e quando no histórico do processo. |
| 10.4 | **Notificar Aluno na aprovação** | Disparar notificação ao aluno quando contrato for aprovado. |
| 10.5 | **Restrição de perfil** | Apenas Secretaria ou superior podem alterar status. |

---

## ❌ Módulo 11 — Reprovação de Contratos
*Fonte: [reprovar_contrato.md](file:///home/caio/Documentos/projetos/PBE_26.1_8002_III/docs/Elaboracao/Casos%20de%20Uso/reprovar_contrato.md)*

| # | Task | Detalhes |
|---|------|----------|
| 11.1 | **Endpoint `PATCH /processos/:id/reprovar`** | Secretaria reprova o contrato → status = `REPROVADO`. Requer campo `justificativa`. |
| 11.2 | **Validar justificativa obrigatória** | Bloquear reprovação se justificativa em branco. |
| 11.3 | **Registrar justificativa imutável** | Justificativa fica no histórico e não pode ser apagada (princípio de auditoria). |
| 11.4 | **Notificar Aluno na reprovação** | Disparar notificação com a justificativa da secretaria. |
| 11.5 | **Fluxo de reenvio pós-reprovação** | Permitir que o aluno reenvie contrato corrigido pelo mesmo fluxo, sem abrir novo processo. |

---

## ⚙️ Módulo 12 — Regras de Negócio / Validações Automáticas
*Fonte: [pesquisa.md](file:///home/caio/Documentos/projetos/PBE_26.1_8002_III/docs/Iniciacao/pesquisa.md) — Seção "Regras de Negócio e Validação (Backend)"*

| # | Task | Detalhes |
|---|------|----------|
| 12.1 | **Validar carga horária** | Bloquear se `horas_diarias > 6` OU `horas_semanais > 30`. Alertar violação da Lei 11.788. |
| 12.2 | **Detectar conflito de grade** | Se `horario_estagio` intercede `horario_aula` → sinalizar para análise manual. |
| 12.3 | **Validar duração contratual** | `data_fim - data_inicio > 24 meses` → impedir aprovação (exceto PCD). |
| 12.4 | **Validar limite de formatura** | `data_fim > data_previsao_formatura` → bloquear. |
| 12.5 | **Validar retroatividade** | `data_atual - data_inicio > 30 dias` → rejeitar TCE. |
| 12.6 | **Validar dados do aluno** | Match de CPF, Matrícula e Status Ativo. Rejeitar se não matriculado em disciplina de estágio. |
| 12.7 | **Validar integridade documental (assinaturas)** | Ordem: 1º Aluno → 2º Empresa (c/ carimbo) → 3º Ibmec. Bloquear se faltar assinatura. |
| 12.8 | **Controle de versão automático** | Novo upload no mesmo `id_estagio` → arquivar anterior, incrementar versão. |

---

## 🤖 Módulo 13 — Integração com IA
*Fonte: [pesquisa.md](file:///home/caio/Documentos/projetos/PBE_26.1_8002_III/docs/Iniciacao/pesquisa.md) + [brainstorm.md](file:///home/caio/Documentos/projetos/PBE_26.1_8002_III/docs/Iniciacao/brainstorm.md)*

| # | Task | Detalhes |
|---|------|----------|
| 13.1 | **Serviço de pré-análise de contratos via IA** | Extrair dados do PDF automaticamente e verificar conformidade com as regras. |
| 13.2 | **Marcação visual de erros** | Destacar campos incorretos ou ausentes para a Secretaria. |
| 13.3 | **Pesquisa de histórico da empresa** | IA analisa histórico da empresa concedente. |
| 13.4 | **Insights preditivos para Carreiras** | Gerar tendências de contratação para o departamento de Carreiras. |

---

## 🔔 Módulo 14 — Notificações
*Fonte: [brainstorm.md](file:///home/caio/Documentos/projetos/PBE_26.1_8002_III/docs/Iniciacao/brainstorm.md) + [reprovar_contrato.md](file:///home/caio/Documentos/projetos/PBE_26.1_8002_III/docs/Elaboracao/Casos%20de%20Uso/reprovar_contrato.md)*

| # | Task | Detalhes |
|---|------|----------|
| 14.1 | **Serviço de notificações por e-mail** | Disparo automático de e-mails para aluno e secretaria sobre mudanças de status. |
| 14.2 | **Notificação de aprovação** | E-mail ao aluno quando contrato aprovado. |
| 14.3 | **Notificação de reprovação** | E-mail ao aluno com justificativa da reprovação. |
| 14.4 | **Notificação de novo envio** | E-mail à secretaria quando aluno submeter novo documento. |

---

## 🏗️ Módulo 15 — Infraestrutura Transversal

| # | Task | Detalhes |
|---|------|----------|
| 15.1 | 📌 **Configurar projeto Django** | Setup inicial com estrutura de apps, settings, URLs. |
| 15.2 | 📌 **Configurar banco de dados relacional** | Migrations, modelos, conexões. |
| 15.3 | 📌 **Criar Enums globais** | `StatusProcesso`, `Unidade` (BARRA, CENTRO, BH, BRASILIA), `Periodo` (P1 a P10). |
| 15.4 | 📌 **Criar modelos `Curso` e `Area`** | Estrutura acadêmica: Aluno → Curso → Área → Coordenação. |
| 15.5 | **Sistema de logs/auditoria** | Registrar todas as ações e trâmites em sistema de eventos separado. |
| 15.6 | **Paginação e filtros padrão** | Implementar paginação e filtros reutilizáveis nas listagens. |
| 15.7 | **Documentação da API (Swagger/OpenAPI)** | Documentar todas as rotas conforme mencionado no brainstorm. |
| 15.8 | **LGPD — Proteção de dados** | Garantir sigilo e finalidade específica no tratamento de dados pessoais. |
| 15.9 | **Deploy em Cloud** | Configurar infraestrutura cloud para aplicação, banco e storage. |

---

## 📈 Resumo Quantitativo

| Módulo | Qtd Tasks |
|--------|-----------|
| 1. Autenticação & Segurança | 8 |
| 2. Gestão de Alunos | 7 |
| 3. Processo de Estágio | 9 |
| 4. Upload & Armazenamento | 5 |
| 5. Acompanhamento de Status | 5 |
| 6. Relatórios de Horas | 6 |
| 7. Download de Documentos | 3 |
| 8. Pesquisa de Alunos | 4 |
| 9. Análise/Visualização | 3 |
| 10. Validação de Contratos | 5 |
| 11. Reprovação de Contratos | 5 |
| 12. Regras de Negócio | 8 |
| 13. Integração com IA | 4 |
| 14. Notificações | 4 |
| 15. Infraestrutura | 9 |
| **TOTAL** | **85** |

---

> [!IMPORTANT]
> Este levantamento é uma **primeira versão** baseada exclusivamente na documentação existente. Algumas tasks podem ser subdivididas ou agrupadas dependendo da granularidade desejada pela equipe no GitHub Projects.
