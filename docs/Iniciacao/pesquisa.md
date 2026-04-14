# 🔍 Pesquisa: Legislação e Referências

---

## ⚖️ Base Legal e Normativas
Nesta seção, consolidamos as regras que regem o estágio a nível nacional.

### 📜 Legislação Trabalhista (Lei 11.788/08)
O estágio é um ato educativo escolar supervisionado. Para sua validade jurídica, deve cumprir:

**Requisitos Formais:**

* **Matrícula e Frequência:** O aluno deve estar ativo em curso de ensino superior, técnico ou médio.
* **Termo de Compromisso de Estágio (TCE):** Contrato assinado pelo aluno, pela instituição de ensino e pela empresa.
* **Compatibilidade:** As atividades devem ser estritamente ligadas à grade curricular do curso.

**Jornada de Atividade:**

* **6h diárias / 30h semanais:** Regra geral para ensino superior e médio regular.
* **4h diárias / 20h semanais:** Para educação especial ou EJA.
* **Redução de Carga:** Em semanas de prova, a carga horária pode ser reduzida à metade para fins de estudo, conforme previsto no TCE.

**Direitos e Benefícios:**

* **Bolsa-auxílio e Auxílio-transporte:** Obrigatórios apenas para estágios não-obrigatórios.
* **Recesso Remunerado:** Direito a 30 dias a cada 12 meses (preferencialmente nas férias escolares) ou proporcional ao período estagiado.
* **Seguro:** Apólice de seguro contra acidentes pessoais obrigatória sob responsabilidade da empresa.

### 🎓 Legislação MEC e DCNs
Enquanto a Lei do Estágio dita as regras contratuais, as Diretrizes Curriculares Nacionais (DCNs) e o MEC focam no valor pedagógico:

* **Integração Curricular:** O estágio deve constar no Projeto Pedagógico do Curso (PPC) como extensão do aprendizado.
* **Supervisão:**
    * **Orientador Acadêmico:** Professor da faculdade que valida os relatórios.
    * **Supervisor de Campo:** Profissional da empresa (com formação na área) que limita-se a orientar no máximo 10 estagiários simultaneamente.
* **Avaliação:** Entrega obrigatória de relatórios de atividades em períodos não superiores a 6 meses.

---

## 🏛️ Normas Acadêmicas e Processos Internos
Regras específicas para alunos da instituição e o ecossistema YDUQS, alinhadas aos processos diários da Secretaria.

* **Documentação Obrigatória:** O processo inicia com a validação do TCE e do Plano de Atividades, contendo dados da Concedente, Interveniente e Estagiário.
* **Prazos e Retroatividade:** A instituição não assina documentos com mais de 30 dias retroativos ao início do estágio.
* **Ordem de Assinatura:** O fluxo de validação exige que a instituição de ensino seja a última a assinar o termo, precedida pelo aluno e pela empresa (com carimbo obrigatório).
* **Ética e Compliance:** O estagiário deve aderir ao Código de Ética e Anticorrupção da YDUQS.
* **LGPD (Lei Geral de Proteção de Dados):** Todo tratamento de dados pessoais de alunos e representantes das empresas segue a Lei 13.709/2018, garantindo sigilo e finalidade específica para a gestão do estágio.
* **Rescisão:** Pode ocorrer a qualquer momento por ambas as partes via aviso prévio ou automaticamente ao término/trancamento do curso.

**Desafios Operacionais (Descobertas via Entrevistas):**

O levantamento de requisitos com a Secretaria revelou gargalos que o sistema deve solucionar:

* **Trabalho Manual:** Alta incidência de tarefas simples e repetitivas, gerando fadiga e margem para erros humanos.
* **Gestão de Versionamento:** Dificuldade no controle de diferentes versões de documentos submetidos por um grande volume de estudantes, resultando em invalidações equivocadas.

---

## ⚙️ Regras de Negócio e Validação (Backend)
Esta seção descreve como a API RESTful automatiza a conformidade jurídica e os processos mapeados com a Secretaria. O sistema implementa as seguintes travas e validações:

| Requisito | Regra de Validação na API | Ação do Sistema |
| :--- | :--- | :--- |
| **Carga Horária** | `horas_diarias > 6` OU `horas_semanais > 30` | Bloquear submissão e alertar violação da Lei 11.788. |
| **Conflito de Grade** | `horario_estagio` intercede `horario_aula` | Sinalizar conflito de horários para análise manual. |
| **Duração Contratual** | `data_fim - data_inicio > 24 meses` | Impedir aprovação (exceto flag `is_PCD = true`). |
| **Limite de Formatura** | `data_fim > data_previsao_formatura` | Bloquear aprovação, pois o aluno deixa de ter vínculo. |
| **Retroatividade** | `data_atual - data_inicio > 30 dias` | Rejeitar TCE submetido fora do prazo institucional. |
| **Dados do Aluno** | Match de CPF, Matrícula e Status (Ativo) | Rejeitar contrato se o aluno não estiver matriculado na disciplina de Estágio. |
| **Integridade Documental e Assinaturas** | Validação sequencial: 1º Aluno ➔ 2º Empresa (c/ carimbo) ➔ 3º Ibmec | Bloquear fluxo caso falte assinatura prévia de aluno ou empresa. |
| **Controle de Versão** | `novo_upload` no mesmo `id_estagio` | Arquivar documento anterior (`status = obsoleto`) e atualizar `versão_atual`. |

### 🔑 Mapeamento de Atores e Permissões
Com base no fluxo operacional levantado, o sistema segmenta as responsabilidades para reduzir a sobrecarga e descentralizar o processo:

* 👤 **Aluno:** Inicia o processo, submete o TCE assinado e os relatórios de horas.
* 👥 **Secretaria:** Foca na validação burocrática (dados, assinaturas, seguro e versionamento).
* 👨‍🏫 **Coordenação:** Foca exclusivamente na validação pedagógica (área de conhecimento e carga horária alinhada ao curso).
* 🏢 **Carreiras:** Utiliza os dados consolidados para controle interno, gestão da reputação das empresas e ofertas de vagas.

### 🤖 Integração com Inteligência Artificial
Para combater a validação manual e repetitiva (maior dor relatada pela Secretaria), o sistema incorpora IA para atuar na primeira camada de triagem. A IA será responsável por:

* Analisar a extração de dados dos contratos de forma automatizada.
* Produzir insights preditivos para o departamento de Carreiras sobre tendências de contratação.

---

## 🔍 Benchmarking (Pesquisa de Aplicativos)
Análise de soluções existentes no mercado que serviram de referência para o projeto:

* **Zuna:** Foco em desburocratização e conexão direta entre talentos e empresas.
* **Facilcon:** Especializada em gestão de documentos e conformidade legal de estágios.
* **Rade Estágio:** Plataforma focada no controle de relatórios e integração entre faculdade e empresa.