# Base de Conhecimento

> [!TIP]
> **Prompt usado para esta etapa:**
>
> Organize a base de conhecimento do agente **Amparo** usando os 4 arquivos da pasta `data/`. Explique pra que serve cada arquivo e monte um exemplo de contexto formatado que será enviado pro LLM. Preencha o template abaixo.

## Dados Utilizados

| Arquivo | Formato | Para que serve no Amparo? |
|---------|---------|---------------------------|
| `historico_analises.csv` | CSV | Armazena análises anteriores, dúvidas dos responsáveis e decisões já discutidas, permitindo continuidade no acompanhamento financeiro da ONG. |
| `perfil_ong.json` | JSON | Reúne os dados principais da ONG, como área de atuação, orçamento mensal, número de crianças atendidas e necessidades atuais. |
| `itens_prioritarios.json` | JSON | Lista os itens, serviços e necessidades que o agente pode considerar ao explicar prioridades de gasto e organização financeira. |
| `movimentacoes_ong.csv` | CSV | Registra entradas e saídas da ONG, permitindo identificar para onde o dinheiro está indo e quais categorias consomem mais recursos. |

---

## Adaptações nos Dados

> Você modificou ou expandiu os dados mockados? Descreva aqui.

Sim. Em vez de usar dados fictícios ligados a finanças pessoais e investimentos, a base foi adaptada para o contexto de uma ONG que atende crianças atípicas. A estrutura com 4 arquivos foi mantida, mas os conteúdos foram alterados para refletir a realidade institucional da organização.

As principais mudanças foram:

- `perfil_investidor.json` foi substituído por `perfil_ong.json`
- `produtos_financeiros.json` foi substituído por `itens_prioritarios.json`
- `transacoes.csv` foi substituído por `movimentacoes_ong.csv`
- `historico_atendimento.csv` foi substituído por `historico_analises.csv`

Com isso, o agente passa a trabalhar com:
- orçamento institucional
- doações e repasses
- despesas fixas e variáveis
- necessidades prioritárias da ONG
- histórico de análises anteriores

---

## Estratégia de Integração

### Como os dados são carregados?
> Descreva como seu agente acessa a base de conhecimento.

Os dados podem ser carregados via código, lendo os arquivos JSON e CSV da pasta `data/`.

```python
import pandas as pd
import json

perfil_ong = json.load(open('./data/perfil_ong.json', encoding='utf-8'))
movimentacoes = pd.read_csv('./data/movimentacoes_ong.csv')
historico = pd.read_csv('./data/historico_analises.csv')
itens_prioritarios = json.load(open('./data/itens_prioritarios.json', encoding='utf-8'))
```

### Como os dados são usados no prompt?
> Os dados vão no system prompt? São consultados dinamicamente?

Para uma versão inicial do projeto, os dados podem ser injetados diretamente no prompt, garantindo que o agente receba contexto suficiente para responder com coerência. Em versões futuras, o ideal é carregar e resumir os dados dinamicamente via código, evitando excesso de tokens e facilitando atualização da base.

```text
DADOS DA ONG (data/perfil_ong.json):
{
  "nome": "Instituto Caminho Azul",
  "cidade": "João Pessoa - PB",
  "area_atuacao": "Apoio a crianças atípicas",
  "criancas_atendidas": 28,
  "orcamento_mensal_medio": 12000.00,
  "saldo_atual": 4200.00,
  "despesas_fixas_mensais": 7900.00,
  "principais_necessidades": [
    "materiais pedagógicos",
    "cadeiras adaptadas",
    "alimentação",
    "transporte",
    "computadores para atividades educativas"
  ],
  "objetivo_principal": "Organizar os recursos da ONG e melhorar a priorização dos gastos",
  "restricoes": [
    "não comprometer despesas essenciais",
    "não usar o saldo total em gastos não urgentes"
  ]
}

MOVIMENTAÇÕES DA ONG (data/movimentacoes_ong.csv):
data,descricao,categoria,valor,tipo
2026-03-01,Doação mensal recorrente,doacoes,3000.00,entrada
2026-03-02,Conta de energia,infraestrutura,420.00,saida
2026-03-03,Compra de alimentos,alimentacao,950.00,saida
2026-03-05,Repasse de parceiro local,parcerias,2500.00,entrada
2026-03-06,Material pedagógico,pedagogico,680.00,saida
2026-03-08,Transporte para atendimentos,transporte,390.00,saida
2026-03-10,Internet,infraestrutura,120.00,saida
2026-03-12,Compra de cadeiras plásticas,mobiliario,540.00,saida
2026-03-15,Evento beneficente,eventos,1800.00,entrada
2026-03-18,Medicamentos pontuais,saude,310.00,saida

HISTÓRICO DE ANÁLISES (data/historico_analises.csv):
data,tema,resumo,orientacao_gerada,resolvido
2026-02-10,Prioridade de compra,Análise sobre compra de materiais pedagógicos antes de itens decorativos,Priorizar materiais usados diretamente no atendimento,sim
2026-02-18,Despesas fixas,Levantamento das despesas mensais essenciais da ONG,Separar custos fixos e variáveis para melhor controle,sim
2026-02-25,Uso de doação pontual,Dúvida sobre destinar verba extra para computadores ou evento,Analisar urgência e impacto direto nas crianças,sim
2026-03-04,Organização financeira,Pedido de ajuda para entender categorias de gasto,Padronizar categorias para facilitar leitura do orçamento,sim
2026-03-09,Saldo disponível,Dúvida sobre quanto do saldo pode ser usado com segurança,Evitar comprometer reserva para despesas fixas,sim

ITENS PRIORITÁRIOS (data/itens_prioritarios.json):
[
  {
    "nome": "Alimentação das crianças",
    "categoria": "essencial",
    "nivel_prioridade": "alta",
    "impacto": "direto",
    "descricao": "Gasto recorrente que impacta diretamente o bem-estar diário das crianças"
  },
  {
    "nome": "Materiais pedagógicos",
    "categoria": "educacional",
    "nivel_prioridade": "alta",
    "impacto": "direto",
    "descricao": "Itens usados nas atividades de aprendizagem e desenvolvimento"
  },
  {
    "nome": "Transporte para atendimentos",
    "categoria": "logistica",
    "nivel_prioridade": "alta",
    "impacto": "direto",
    "descricao": "Permite deslocamento para atendimentos, eventos e apoio às famílias"
  },
  {
    "nome": "Computadores para atividades educativas",
    "categoria": "infraestrutura_educacional",
    "nivel_prioridade": "media",
    "impacto": "medio",
    "descricao": "Melhora as atividades educativas, mas pode depender do orçamento do mês"
  },
  {
    "nome": "Itens decorativos",
    "categoria": "ambientacao",
    "nivel_prioridade": "baixa",
    "impacto": "indireto",
    "descricao": "Podem melhorar o ambiente, mas não são prioridade diante de necessidades essenciais"
  }
]
```

---

## Exemplo de Contexto Montado

> Mostre um exemplo de como os dados são formatados para o agente.

O exemplo abaixo resume os dados mais relevantes da base, reduzindo volume de tokens sem perder o contexto necessário para respostas úteis e coerentes.

```text
DADOS DA ONG:
- Nome: Instituto Caminho Azul
- Cidade: João Pessoa - PB
- Área de atuação: Apoio a crianças atípicas
- Crianças atendidas: 28
- Orçamento mensal médio: R$ 12.000,00
- Saldo atual: R$ 4.200,00
- Despesas fixas mensais: R$ 7.900,00
- Objetivo principal: Organizar os recursos da ONG e melhorar a priorização dos gastos

RESUMO DAS MOVIMENTAÇÕES RECENTES:
- Entradas:
  - Doação mensal recorrente: R$ 3.000,00
  - Repasse de parceiro local: R$ 2.500,00
  - Evento beneficente: R$ 1.800,00
- Saídas:
  - Alimentação: R$ 950,00
  - Infraestrutura: R$ 540,00
  - Pedagógico: R$ 680,00
  - Transporte: R$ 390,00
  - Mobiliário: R$ 540,00
  - Saúde: R$ 310,00

HISTÓRICO RELEVANTE:
- Em análises anteriores, o agente já orientou a priorizar materiais pedagógicos antes de gastos decorativos.
- Também já recomendou separar despesas fixas e variáveis para melhorar o controle financeiro.
- Há orientação prévia para não comprometer o saldo com gastos não urgentes.

ITENS QUE O AGENTE PODE CONSIDERAR NA EXPLICAÇÃO:
- Alimentação das crianças (prioridade alta)
- Materiais pedagógicos (prioridade alta)
- Transporte para atendimentos (prioridade alta)
- Computadores para atividades educativas (prioridade média)
- Itens decorativos (prioridade baixa)
```

---

## Observação Final

A base de conhecimento do Amparo foi estruturada para apoiar respostas explicativas, organizadas e transparentes. O agente não toma decisões sozinho, mas ajuda os responsáveis pela ONG a entender melhor o orçamento, visualizar padrões de gasto e refletir sobre prioridades com base nos dados disponíveis.
