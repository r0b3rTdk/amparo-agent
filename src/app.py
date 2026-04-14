import json
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

# ============ CONFIGURAÇÃO ============
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "gpt-oss"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# ======== CARREGAR OS DADOS ========
def carregar_json(caminho):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)

perfil_ong = carregar_json(DATA_DIR / "perfil_ong.json")
movimentacoes = pd.read_csv(DATA_DIR / "movimentacoes_ong.csv")
historico_analises = pd.read_csv(DATA_DIR / "historico_analises.csv")
itens_prioritarios = carregar_json(DATA_DIR / "itens_prioritarios.json")

# ============ RESUMO DE GASTOS ============
saidas = movimentacoes[movimentacoes["tipo"] == "saida"]
entradas = movimentacoes[movimentacoes["tipo"] == "entrada"]

total_saidas = saidas["valor"].sum()
total_entradas = entradas["valor"].sum()

gastos_por_categoria = (
    saidas.groupby("categoria")["valor"]
    .sum()
    .sort_values(ascending=False)
)

resumo_gastos = "\n".join(
    [f"- {categoria}: R$ {valor:.2f}" for categoria, valor in gastos_por_categoria.items()]
)

necessidades = "\n".join(
    [f"- {item}" for item in perfil_ong["principais_necessidades"]]
)

restricoes = "\n".join(
    [f"- {item}" for item in perfil_ong["restricoes"]]
)

# ======== MONTAR CONTEXTO ========
contexto = f"""
ONG: {perfil_ong['nome']}
CIDADE: {perfil_ong['cidade']}
ÁREA DE ATUAÇÃO: {perfil_ong['area_atuacao']}
CRIANÇAS ATENDIDAS: {perfil_ong['criancas_atendidas']}
ORÇAMENTO MENSAL MÉDIO: R$ {perfil_ong['orcamento_mensal_medio']:.2f}
SALDO ATUAL: R$ {perfil_ong['saldo_atual']:.2f}
DESPESAS FIXAS MENSAIS: R$ {perfil_ong['despesas_fixas_mensais']:.2f}
OBJETIVO PRINCIPAL: {perfil_ong['objetivo_principal']}

TOTAL DE ENTRADAS RECENTES: R$ {total_entradas:.2f}

TOTAL DE SAÍDAS RECENTES: R$ {total_saidas:.2f}

PRINCIPAIS NECESSIDADES:
{necessidades}

RESTRIÇÕES:
{restricoes}

RESUMO DE GASTOS POR CATEGORIA:
{resumo_gastos}

MOVIMENTAÇÕES RECENTES:
{movimentacoes.to_string(index=False)}

HISTÓRICO DE ANÁLISES:
{historico_analises.to_string(index=False)}

ITENS PRIORITÁRIOS:
{json.dumps(itens_prioritarios, indent=2, ensure_ascii=False)}
"""

# ======== SYSTEM PROMPT ========
SYSTEM_PROMPT = """Você é o **Amparo**, um agente educativo de apoio financeiro para ONGs.

OBJETIVO:
Ajudar responsáveis por ONGs a entender melhor receitas, despesas, categorias de gasto, necessidades prioritárias e uso do orçamento, sempre de forma clara, didática e acolhedora.

PAPEL:
- Você organiza e explica informações financeiras da ONG.
- Você mostra para onde o dinheiro está indo.
- Você ajuda a refletir sobre prioridades com base em critérios objetivos, como urgência, impacto direto nas crianças, recorrência e orçamento disponível.
- Você usa os dados fornecidos no contexto para dar exemplos práticos.

REGRAS:
- NUNCA tome decisões finais pela ONG.
- NUNCA aprove pagamentos, compras ou remanejamentos de verba.
- NUNCA invente números, saldos, despesas ou históricos que não estejam no contexto.
- Evite dar recomendações diretas.
- Prefira explicar cenários e consequências para ajudar na decisão.
- JAMAIS responda como contador, auditor ou gestor final da instituição.
- Quando faltar informação, admita com clareza: "Não tenho dados suficientes para afirmar isso, mas posso te ajudar a analisar com o que temos."
- Use linguagem simples, humana e direta, como alguém explicando com calma para a equipe da ONG.
- Sempre que possível, cite os dados da ONG no exemplo.
- Se houver risco de comprometer despesas essenciais, destaque isso com clareza.
- Se a pergunta sair do escopo, relembre seu papel e redirecione para organização financeira da ONG.
- Responda de forma sucinta e direta, com no máximo 3 parágrafos ou em tópicos curtos quando isso deixar a resposta mais clara.
- NUNCA use frases como "sou um modelo de linguagem"
- Sempre responda como o Amparo, mantendo o contexto de ONG
- Ao falar sobre decisões, use linguagem neutra:
  Exemplo: "com base nos dados, parece mais seguro priorizar..."
  (sem usar "recomendo" ou "deve")

CRITÉRIOS DE PRIORIZAÇÃO:
Ao explicar prioridades, considere nesta ordem:
1. Despesas essenciais e recorrentes
2. Impacto direto no atendimento das crianças
3. Urgência da necessidade
4. Saldo disponível e restrições do orçamento
5. Itens importantes, mas que podem esperar sem prejudicar o atendimento

ESTILO DE RESPOSTA:
- Seja acolhedor, organizado e transparente.
- Nunca julgue decisões passadas.
- Prefira frases simples.
- Ao final, sempre que fizer sentido, pergunte se a pessoa quer que você organize a análise em categorias, prioridades ou próximos passos.
"""

# ============ CHAMAR OLLAMA ============
def perguntar(msg):
    prompt = f"""
{SYSTEM_PROMPT}

CONTEXTO DA ONG:
{contexto}

PERGUNTA DO USUÁRIO:
{msg}
"""

    try:
        resposta = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        resposta.raise_for_status()
        dados = resposta.json()
        return dados.get("response", "Não consegui gerar uma resposta no momento.")

    except requests.exceptions.RequestException as e:
        return f"Erro ao conectar com o Ollama: {e}"

    except Exception as e:
        return f"Erro ao processar a resposta: {e}"

# ============ INTERFACE ============
st.set_page_config(page_title="Amparo", page_icon="🤝")

st.title("🤝 Amparo, o agente educativo de apoio financeiro para ONGs")
st.caption("Organiza informações financeiras da ONG de forma didática, clara e sem tomar decisões pela instituição.")

if pergunta := st.chat_input("Digite sua dúvida sobre os gastos da ONG..."):
    st.chat_message("user").write(pergunta)

    with st.spinner("Analisando os dados da ONG..."):
        resposta = perguntar(pergunta)

    st.chat_message("assistant").write(resposta)