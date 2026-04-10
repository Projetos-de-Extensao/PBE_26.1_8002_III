# Pesquisa: Legislação e Referências

---

## ⚖️ Base Legal e Normativas
Nesta seção, consolidamos as regras que regem o estágio a nível nacional.

### Legislação Trabalhista (Lei 11.788/08)
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

### Legislação MEC e DCNs
Enquanto a Lei do Estágio dita as regras contratuais, as Diretrizes Curriculares Nacionais (DCNs) e o MEC focam no valor pedagógico:

* **Integração Curricular:** O estágio deve constar no Projeto Pedagógico do Curso (PPC) como extensão do aprendizado.
* **Supervisão:**
    * **Orientador Acadêmico:** Professor da faculdade que valida os relatórios.
    * **Supervisor de Campo:** Profissional da empresa (com formação na área) que limita-se a orientar no máximo 10 estagiários simultaneamente.
* **Avaliação:** Entrega obrigatória de relatórios de atividades em períodos não superiores a 6 meses.

---

## 🏛️ Normas Acadêmicas Ibmec
Regras específicas para alunos da instituição e o ecossistema YDUQS.

* **Documentação Obrigatória:** O processo inicia com a validação do TCE e do Plano de Atividades, contendo dados da Concedente, Interveniente e Estagiário.
* **Ética e Compliance:** O estagiário deve aderir ao Código de Ética e Anticorrupção da YDUQS.
* **LGPD (Lei Geral de Proteção de Dados):** Todo tratamento de dados pessoais de alunos e representantes das empresas segue a Lei 13.709/2018, garantindo sigilo e finalidade específica para a gestão do estágio.
* **Rescisão:** Pode ocorrer a qualquer momento por ambas as partes via aviso prévio ou automaticamente ao término/trancamento do curso.

---

## ⚙️ Regras de Negócio e Validação (Backend)
Esta seção descreve como o sistema automatiza a conformidade jurídica. O backend deve implementar as seguintes travas lógicas baseadas na Lei 11.788/08:

| Requisito | Regra de Validação | Ação do Sistema |
| :--- | :--- | :--- |
| **Carga Horária** | `horas_diarias > 6` OU `horas_semanais > 30` | Bloquear submissão do formulário. |
| **Duração Contratual** | `data_fim - data_inicio > 24 meses` | Impedir aprovação (exceto para PCD). |
| **Integridade de Arquivos** | `Extensão de arquivo ≠ .pdf` | Rejeitar upload de documentos. |
| **Ciclo de Vida** | Estados: `Pendente` ➔ `Em Análise` ➔ `Aprovado` | Automatizar fluxo de status no DB. |
| **Segurança** | Criptografia em repouso (AES-256) | Proteção de dados sensíveis conforme LGPD. |

---

## 🔍 Benchmarking (Pesquisa de Aplicativos)
Análise de soluções existentes no mercado que serviram de referência para o projeto:

* **Zuna:** Foco em desburocratização e conexão direta entre talentos e empresas.
* **Facilcon:** Especializada em gestão de documentos e conformidade legal de estágios.
* **Rade Estágio:** Plataforma focada no controle de relatórios e integração entre faculdade e empresa.