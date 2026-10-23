from pathlib import Path

import pandas as pd
import streamlit as st

from src.financas import (EMPRESAS, PERIODOS_COVID, ativos_com_dados, carregar_cdi, carregar_precos, cagr,
                          indice_sharpe, maior_queda, simular_carteira)

st.set_page_config(page_title="Simulador de Carteira 📈", page_icon="📈", layout="wide")
st.title("📈 Simulador de Carteira de Ações")
st.markdown("Monte uma carteira com as ações do estudo e compare com o **BOVA11** (Ibovespa) e o **CDI** (renda fixa), "
            "de **2015 a 2025**.")

PASTA_DADOS = Path(__file__).parent / "Datasets"


### Carregamento dos dados
@st.cache_data
def carregar(com_dividendos):
    arquivo = "acoes_ajustado_2015_2025.csv" if com_dividendos else "acoes_2015_2025.csv"
    precos = carregar_precos(PASTA_DADOS / arquivo)
    return precos, carregar_cdi(PASTA_DADOS / "cdi_2015_2025.csv", precos.index)


def formatar_reais(valor):
    return f"R$ {valor:,.0f}".replace(",", ".")


### Parâmetros da simulação
with st.sidebar:
    st.header("⚙️ Simulação")
    valor_inicial = st.number_input("Valor investido (R$)", 1_000, 1_000_000, 10_000, step=1_000)
    com_dividendos = st.checkbox("Incluir dividendos (preço ajustado)", value=False)
    rebalancear = st.checkbox("Rebalancear todo ano (voltar aos pesos escolhidos)", value=False)

    precos, cdi = carregar(com_dividendos)
    primeira, ultima = precos.index[0].date(), precos.index[-1].date()

    st.header("📅 Período")
    inicio = st.date_input("Data de início", value=primeira, min_value=primeira, max_value=ultima, format="DD/MM/YYYY")
    fim = st.date_input("Data de término", value=ultima, min_value=primeira, max_value=ultima, format="DD/MM/YYYY")
    st.caption("Pré-pandemia: até 19/02/2020 · Pandemia: 20/02/2020 a 05/05/2023 · Pós-pandemia: depois disso")

    periodo = precos.loc[pd.Timestamp(inicio):pd.Timestamp(fim)]
    disponiveis = ativos_com_dados(periodo)
    acoes = [a for a in precos.columns if a != "BOVA"]
    peso_padrao = 100 // max(len([a for a in acoes if a in disponiveis]), 1) // 5 * 5

    st.header("⚖️ Pesos da carteira (%)")
    pesos = {}
    for acao in acoes:
        tem_dados = acao in disponiveis
        peso = st.slider(f"{acao} – {EMPRESAS[acao].split(' (')[0]}", 0, 100, peso_padrao if tem_dados else 0,
                         step=5, disabled=not tem_dados)
        pesos[acao] = peso if tem_dados else 0
    if len(disponiveis) < len(precos.columns):
        st.caption("A GOL não tem dados públicos depois de 29/12/2022 (recuperação judicial e saída da bolsa). "
                   "Para incluí-la, termine o período até essa data.")

if inicio >= fim:
    st.warning("A data de término precisa ser depois da data de início.")
    st.stop()
if len(periodo) < 2:
    st.warning("Escolha um período maior.")
    st.stop()
if sum(pesos.values()) == 0:
    st.warning("Defina o peso de pelo menos uma ação.")
    st.stop()

### Simulação
carteira = simular_carteira(periodo, pesos, valor_inicial, rebalancear=rebalancear)
bova = simular_carteira(periodo, {"BOVA": 1}, valor_inicial)
cdi_periodo = cdi.loc[periodo.index]
renda_fixa = cdi_periodo / cdi_periodo.iloc[0] * valor_inicial

st.caption(f"Período analisado: {periodo.index[0]:%d/%m/%Y} a {periodo.index[-1]:%d/%m/%Y} ({len(periodo)} pregões).")
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

### Antes, durante e depois da Covid
fases = {}
for nome, (inicio_fase, fim_fase) in PERIODOS_COVID.items():
    trecho = periodo.loc[inicio_fase:fim_fase]
    if len(trecho) < 20:  # fase fora do período escolhido (ou curta demais para um CAGR)
        continue
    carteira_fase = simular_carteira(trecho, pesos, 1, rebalancear=rebalancear)
    cdi_fase = cdi.loc[trecho.index]
    fases[nome] = {"Início": f"{trecho.index[0]:%d/%m/%Y}", "Fim": f"{trecho.index[-1]:%d/%m/%Y}",
                   "CAGR da carteira": f"{cagr(carteira_fase):+.1%}", "CAGR do BOVA11": f"{cagr(trecho['BOVA']):+.1%}",
                   "CAGR do CDI": f"{cagr(cdi_fase):+.1%}",
                   "Sharpe da carteira": f"{indice_sharpe(carteira_fase, cdi_fase):.2f}",
                   "Sharpe do BOVA11": f"{indice_sharpe(trecho['BOVA'], cdi_fase):.2f}"}
if fases:
    st.markdown("#### Antes, durante e depois da Covid")
    st.caption("Em cada fase, a carteira é comprada no primeiro pregão da fase, com os pesos escolhidos.")
    st.table(pd.DataFrame(fases).T)

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
