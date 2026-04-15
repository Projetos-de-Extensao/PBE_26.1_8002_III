---
id: diagrama_de_classes
title: Diagrama de Classes
---

## Diagrama de Classes

O Diagrama de Classes descreve a estrutura estática do sistema, mostrando suas classes, atributos, métodos e os relacionamentos entre os objetos. No contexto do Sistema de Gestão de Estágios, ele detalha como as entidades como Aluno, Contrato, Relatório e Processo interagem.

![Diagrama de Classes](../assets/Diagramas/out/diagrama_de_classes.svg)

## 🏷️ Enumerações (Enums)

Os Enums garantem a integridade dos atributos de controle no sistema, evitando erros de preenchimento.

| Enum | Propósito | Valores Aceitos |
| :--- | :--- | :--- |
| **`StatusProcesso`** | Regula o ciclo de vida do estágio. | `ABERTO`, `EM_ANALISE_SECRETARIA`, `EM_ANALISE_COORDENACAO`, `PENDENTE_AJUSTE`, `APROVADO`, `REPROVADO`, `CONCLUIDO`, `CANCELADO` |
| **`Unidade`** | Define o campus do usuário. | `BARRA`, `CENTRO`, `BH`, `BRASILIA` |
| **`Periodo`** | Representa o semestre atual do aluno. | `P1` ao `P10` |

---

## 👥 Usuários e Perfis

> [!NOTE]
> Todos os perfis do sistema herdam da classe abstrata **`Usuario`**, compartilhando credenciais essenciais como `matricula`, `nome`, `email`, `senha`, `unidade` e centralizando o método `login()`.

### 👨‍🎓 Aluno
O ator principal. Inicia o processo de estágio e reporta o progresso.
- **Relacionamentos:** Pertence a 1 `Curso` e 1 `Periodo`. Possui *apenas um* `processoAtual`.
- **Ações Principais:** `iniciarProcesso()`, `anexarContrato()`, `anexarRelatorio()`.

### 👩‍💼 Secretaria
Responsável pelo fluxo administrativo e validação inicial de documentos.
- **Ações Principais:** `validarContrato()`, `validarRelatorio()`, `pesquisarAlunos()`, `listarProcessosPendentes()`.

### 👨‍🏫 Coordenação
Decisor acadêmico. Avalia se o estágio está alinhado às diretrizes do curso.
- **Relacionamentos:** Supervisiona toda a sua `Area` específica.
- **Ações Principais:** `validarEstagio()`.

---

## 📑 Processo e Documentação

### 🔄 Processo
O coração do sistema. Ele encapsula o ciclo do estágio conectando `Aluno`, `Secretaria` e `Coordenacao`.
- **Atributos:** `processoId`, `dataCriacao`, `status`.
- **Composições:** Contém instâncias de `Contrato` (1..*) e `Relatorio` (0..*). Se o processo é extinto, os documentos associados também perdem o vínculo estrutural.
- **Transições:** Gerenciado internamente pelos métodos de validação e por `atualizarStatus()`.

### 📝 Contrato
O termo de compromisso formal de início.
- **Dados Relevantes:** Vigência (`dataInicio`, `dataTermino`), dados do prestador (`cnpjEmpresa`, `nomeEmpresa`).
- **Validações:** Requer `apoliceSeguro`, `planoAtividade` válidos e verificação boolean de todas as assinaturas (`assinaturaAluno`, `assinaturaEmpresa`, `assinaturaFaculdade`).

### 📊 Relatório
Submissão periódica para contabilização de atividades e horas.
- **Dados Relevantes:** `horasTrabalhadas`, `periodoReferencia`.
- **Validação:** Necessita do marcador de triagem externa `aprovadoPelaEmpresa`.

---

## 🏫 Estrutura Acadêmica

| Classe | Descrição | Relacionamentos |
| :--- | :--- | :--- |
| **`Curso`** | Identificação do programa de graduação do aluno. | Um aluno possui **1** Curso. Múltiplos cursos compõem **1** Área. |
| **`Area`** | Agrupamento taxonômico de cursos correlatos. | Possui de **0 a Muitos** Cursos, provendo os alunos daquela gestão para referenciar **1** Coordenação. |

---

## 💡 Considerações de Arquitetura e Design

> [!TIP]
> **Boas Práticas Adotadas:** Empregar tipos fortes (via Enums) em toda comunicação crítica minimiza a fragilidade das *magic strings* e garante estabilidade ao longo do crescimento do workflow.

1. **Auditoria Externa (Logs)**: O histórico meticuloso de ações e trâmites processuais deverá ser implementado fora do objeto relacional primário (em um sistema de *eventos/logs* à parte), assegurando leveza de payload e performance nas APIs do sistema nativo.
2. **Restrição por Modelagem (1:1)**: Um `Aluno` está inflexivelmente mapeado para a restrição de possuir um `processoAtual` por vez `(0..1)`. Isso inibe concorrências sistêmicas desleais com os tramites na central de estágios.
3. **Independência Documental Estratégica**: O `Contrato` atua formalmente na admissão enquanto o `Relatorio` age como controle sequencial; ao tratar-los como entidades apartadas — unificadas puramente pela amarração do Processo —  evita-se a sobreposição de complexidade na manutenção.
