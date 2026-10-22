from pathlib import Path

import pandas as pd
import streamlit as st

from src.financas import EMPRESAS, carregar_cdi, carregar_precos, cagr, indice_sharpe, maior_queda, simular_carteira

st.set_page_config(page_title="Simulador de Carteira 📈", page_icon="📈", layout="wide")
st.title("📈 Simulador de Carteira de Ações")
st.markdown("Monte uma carteira com as ações do estudo e compare com o **BOVA11** (Ibovespa) e o **CDI** (renda fixa).")

PASTA_DADOS = Path(__file__).parent / "Datasets"


### Carregamento dos dados
@st.cache_data
def carregar(com_dividendos):
    arquivo = "acoes_ajustado.csv" if com_dividendos else "acoes.csv"
    precos = carregar_precos(PASTA_DADOS / arquivo)
    return precos, carregar_cdi(PASTA_DADOS / "cdi.csv", precos.index)


def formatar_reais(valor):
    return f"R$ {valor:,.0f}".replace(",", ".")


### Parâmetros da simulação
with st.sidebar:
    st.header("⚙️ Simulação")
    valor_inicial = st.number_input("Valor investido (R$)", 1_000, 1_000_000, 10_000, step=1_000)
    com_dividendos = st.checkbox("Incluir dividendos (preço ajustado)", value=False)
    rebalancear = st.checkbox("Rebalancear todo ano (voltar aos pesos escolhidos)", value=False)

    precos, cdi = carregar(com_dividendos)
    inicio, fim = st.slider("Período", min_value=precos.index[0].date(), max_value=precos.index[-1].date(),
                            value=(precos.index[0].date(), precos.index[-1].date()), format="MM/YYYY")

    st.header("⚖️ Pesos da carteira (%)")
    acoes = [a for a in precos.columns if a != "BOVA"]
    pesos = {acao: st.slider(f"{acao} – {EMPRESAS[acao].split(' (')[0]}", 0, 100, 20, step=5) for acao in acoes}

if sum(pesos.values()) == 0:
    st.warning("Defina o peso de pelo menos uma ação.")
    st.stop()

periodo = precos.loc[str(inicio):str(fim)]
if len(periodo) < 2:
    st.warning("Escolha um período maior.")
    st.stop()

### Simulação
carteira = simular_carteira(periodo, pesos, valor_inicial, rebalancear=rebalancear)
bova = simular_carteira(periodo, {"BOVA": 1}, valor_inicial)
cdi_periodo = cdi.loc[periodo.index]
renda_fixa = cdi_periodo / cdi_periodo.iloc[0] * valor_inicial

col1, col2, col3, col4 = st.columns(4)
col1.metric("Minha carteira", formatar_reais(carteira.iloc[-1]), f"{carteira.iloc[-1] / valor_inicial - 1:+.1%}")
col2.metric("BOVA11 (Ibovespa)", formatar_reais(bova.iloc[-1]), f"{bova.iloc[-1] / valor_inicial - 1:+.1%}")
col3.metric("CDI (renda fixa)", formatar_reais(renda_fixa.iloc[-1]), f"{renda_fixa.iloc[-1] / valor_inicial - 1:+.1%}")
col4.metric("Crescimento anual (CAGR)", f"{cagr(carteira):.1%}",
            f"{(cagr(carteira) - cagr(bova)) * 100:+.1f} p.p. vs BOVA11")

st.markdown("#### Evolução do valor investido")
st.line_chart(pd.DataFrame({"Minha carteira": carteira, "BOVA11 (Ibovespa)": bova, "CDI (renda fixa)": renda_fixa}),
              y_label="R$")

st.markdown(f"**Índice de Sharpe** (retorno acima do CDI por unidade de risco): "
            f"carteira **{indice_sharpe(carteira, cdi_periodo):.2f}** · BOVA11 **{indice_sharpe(bova, cdi_periodo):.2f}** "
            f"· quanto maior, melhor. Maior queda da carteira no período: **{maior_queda(carteira):.1%}**.")

### Detalhe por ação
st.markdown("#### Resultado de cada ação no período")
pesos_validos = {a: p for a, p in pesos.items() if p > 0}
acoes_validas = list(pesos_validos)
detalhe = pd.DataFrame({
    "Peso": pd.Series(pesos_validos) / sum(pesos_validos.values()),
    "Retorno total": periodo[acoes_validas].iloc[-1] / periodo[acoes_validas].iloc[0] - 1,
    "CAGR": cagr(periodo[acoes_validas]),
    "Maior queda": maior_queda(periodo[acoes_validas]),
})
st.dataframe(detalhe.style.format("{:.1%}"), width="stretch")
st.caption("Sem custos de corretagem, impostos e taxa de administração. Com dividendos, a GOL usa o preço sem ajuste "
           "(ticker indisponível no Yahoo Finance). Rentabilidade passada não garante rentabilidade futura.")
