# Painel Comercial — Dashboard de Vendas

Dashboard analítico construído no Power BI para acompanhamento de performance comercial de uma rede varejista de moda masculina com 12 lojas, abrangendo o período de 2019 a 2026.

## 1. Problema de Negócio

A rede varejista precisava de uma visão consolidada e dinâmica da operação comercial para responder perguntas como:

- Qual o faturamento líquido por período e como ele evolui mês a mês?
- Quais produtos concentram as maiores e menores receitas?
- O ticket médio está crescendo ou diminuindo ao longo do tempo?
- As metas de faturamento estão sendo atingidas? Qual o percentual de atingimento?
- Qual o crescimento anual da operação?
- Quais fatores mais influenciam o resultado das vendas?

Sem essa visão, as decisões de compra, precificação e gestão de portfólio ficavam baseadas em relatórios estáticos e percepções individuais dos gerentes.

## 2. Planejamento da Solução

### Estratégia Analítica

| Camada | Descrição |
|--------|-----------|
| **Descritiva** | KPIs de faturamento, custo, quantidade de vendas e ticket médio |
| **Diagnóstica** | Ranking de produtos (Top 10 maiores e menores), matriz temporal com % de atingimento e crescimento anual |
| **Preditiva** | Visual de Influenciadores-Chave (Key Drivers) para identificar fatores que impactam o resultado |

### Modelo de Dados (Star Schema)

```
              ┌──────────────┐
              │  dCalendario │
              │──────────────│
              │ Ano          │
              │ Mês          │
              └──────┬───────┘
                     │
  ┌──────────┐   ┌───┴────┐   ┌────────────┐
  │  fMetas  │───│fVendas │───│  dProduto  │
  │──────────│   │────────│   │────────────│
  │ Meta     │   │ID_Pedido│  │ produto    │
  │ Periodo  │   │Data     │  │ Marca      │
  └──────────┘   │Qtde     │  │ Grupo      │
                 │VlrUnit  │  │ SubGrupo   │
  ┌──────────┐   │VlrTotal │  └────────────┘
  │fDevoluções│──│Desconto │
  │──────────│   │VlrLiquid│
  │ ...      │   │CustoMed │
  └──────────┘   └─────────┘

          ┌──────────────┐
          │   Medidas    │
          │──────────────│
          │ Faturamento  │
          │ Fat. Líquido │
          │ Custo Unit.  │
          │ Qtd. Vendas  │
          │ Ticket Médio │
          │ % Atingimento│
          │ % Cresc Anual│
          └──────────────┘
```

**Tabelas Fato:** `fVendas` (570 mil+ registros), `fDevoluções`, `fMetas`

**Tabelas Dimensão:** `dCalendario`, `dProduto`

**Tabela de Medidas:** `Medidas` (tabela calculada exclusiva para métricas DAX)

### Ferramentas Utilizadas

| Ferramenta | Uso |
|------------|-----|
| **Power BI Desktop** | Modelagem, DAX e construção dos visuais |
| **Power Query (M)** | ETL — extração, transformação e carga dos dados |
| **Excel** | Fonte de dados original (.xlsx) |
| **DAX** | Medidas de faturamento, custos, metas e crescimento |

## 3. Execução

### ETL (Power Query)

- Importação da base `fVendas_1.xlsx` com 570.231 linhas e 18 colunas
- Tratamento de valores nulos nas colunas `Cor` (~17%) e `Fornecedor` (~17%)
- Tipagem de colunas (datas, inteiros, decimais)
- Criação da tabela calendário `dCalendario` com hierarquia Ano > Mês
- Separação em modelo Star Schema com tabelas fato e dimensão

### Medidas DAX

| Medida | Descrição |
|--------|-----------|
| `Faturamento` | Soma do valor total bruto de vendas |
| `Faturamento Liquido` | Soma do valor líquido (após descontos) |
| `Custo Unitário` | Soma do custo médio dos produtos vendidos |
| `Qtd. Vendas` | Contagem total de itens vendidos |
| `Ticket Médio` | Faturamento líquido dividido pela quantidade de pedidos |
| `% Atingimento` | Percentual de faturamento realizado vs. meta definida |
| `% Cresc Anual` | Variação percentual do faturamento em relação ao ano anterior |

### Páginas do Relatório

**Visão Geral** — Página principal com:
- **Cards de KPI:** Faturamento, Custo Unitário, Qtd. Vendas, Ticket Médio
- **Gráfico Combo (Coluna + Linha com Área):** Faturamento Líquido e Qtd. Vendas por mês
- **Gráfico de Barras:** Top 10 produtos com maior faturamento
- **Gráfico de Barras:** Top 10 produtos com menor faturamento
- **Matriz:** Detalhamento por Ano e Mês com Faturamento, Custo, Ticket Médio, % Atingimento e % Crescimento Anual
- **Segmentadores:** Ano (dropdown) e Mês (botões)

**Influenciadores** — Página com visual de Influenciadores-Chave (Key Drivers) para análise automatizada de fatores que mais impactam as vendas.

**Tooltip** — Página de tooltip personalizada para enriquecer a experiência de hover nos visuais.

### Design

- **Tema:** Indigo Aurora (dark mode)
- **Paleta principal:** Fundo escuro (`#232B45`), texto claro (`#F5F6FB`), destaque indigo (`#6366F1`)
- **Tipografia:** Calibri / Segoe UI
- **Resolução:** 1920 × 1080

## 4. Geração de Insights

Principais descobertas extraídas do painel:

1. **Concentração de receita:** O ranking Top 10 revela quais produtos são responsáveis pela maior fatia do faturamento líquido, permitindo decisões de reposição e negociação com fornecedores.

2. **Sazonalidade:** O gráfico combo mensal evidencia padrões sazonais de venda e volume, úteis para planejamento de estoque e campanhas.

3. **Atingimento de metas:** A matriz com `% Atingimento` permite acompanhar mês a mês se as metas comerciais estão sendo cumpridas e em quais períodos houve desvio.

4. **Crescimento anual:** O `% Cresc Anual` na matriz possibilita identificar tendências de crescimento ou retração da operação ao longo dos anos.

5. **Produtos de baixo desempenho:** O Top 10 de menores vendas sinaliza itens candidatos a descontinuação ou ações promocionais focadas.

6. **Fatores influenciadores:** A página de Key Drivers identifica automaticamente quais variáveis (loja, marca, grupo, período) mais contribuem para aumentar ou reduzir o faturamento.

## 5. Resultado Final

O painel entrega uma visão completa da operação comercial:

- **Visão consolidada** de faturamento, custos e margens em uma única tela
- **Análise temporal** com drill-down de Ano para Mês
- **Ranking de produtos** que facilita a tomada de decisão sobre portfólio
- **Acompanhamento de metas** com indicador percentual de atingimento
- **Análise inteligente** com Influenciadores-Chave do Power BI

## 6. Retorno sobre o Investimento

| Antes | Depois |
|-------|--------|
| Relatórios estáticos em planilhas, gerados manualmente | Dashboard interativo atualizado automaticamente |
| Análise restrita a períodos fixos | Filtros dinâmicos por ano e mês com interação cruzada |
| Sem visibilidade de metas vs. realizado | % de Atingimento visível na matriz temporal |
| Decisões baseadas em percepção individual | Decisões apoiadas por dados e análise de influenciadores |
| Identificação manual de tendências | Crescimento anual calculado automaticamente |

## 7. Próximos Passos

- [ ] Adicionar página de análise por **loja** com mapa ou ranking por unidade
- [ ] Incluir análise de **margem de contribuição** (Faturamento Líquido - Custo)
- [ ] Criar página de **devoluções** com taxa de devolução por produto e período
- [ ] Implementar **alertas condicionais** (formatação condicional) na matriz para metas não atingidas
- [ ] Publicar no **Power BI Service** com atualização agendada
- [ ] Adicionar medida de **LTV** (Lifetime Value) por cliente/loja

---

## Estrutura do Projeto

```
PROJETO 16 - Painel Comercial/
├── PROJETO 16 - Painel Comercial.pbix   # Arquivo principal do Power BI
├── fVendas_1.xlsx                        # Base de dados de vendas (570k+ registros)
├── README.md                             # Esta documentação
└── execution/                            # Scripts auxiliares de análise
    ├── analyze_projeto_16.py
    ├── extract_pbi_metadata.py
    ├── summarize_results.py
    ├── read_dax_and_compare.py
    ├── test_dm_terms.py
    └── inspect_dm_header.py
```

## Dados

| Atributo | Valor |
|----------|-------|
| **Registros** | 570.231 linhas |
| **Período** | Janeiro/2019 a Dezembro/2026 |
| **Lojas** | 12 unidades |
| **Produtos** | 24 itens |
| **Marcas** | 4 marcas |
| **Grupos** | 8 categorias (Bermuda, Blazer, Costume, Calçado, etc.) |
| **Subgrupos** | 11 subcategorias |

## Autor

**Nilvan Felipe** — Analista de Dados / Power BI Developer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/nilvanfelipe/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/nilvanfelipe)
