# Registro de decisões analíticas

Este documento registra as principais decisões do projeto, no formato
**Contexto → Decisão → Alternativas consideradas → Consequência → Onde está**.
Cada decisão tem um código (DA-XX) para ser citada em commits e pull requests.

Os números vêm das saídas do notebook [`Notebooks/Análise do Comportamento da Carteira de Ações - Finanças parte 1 - v2.ipynb`](../Notebooks/).

| Código | Decisão |
|---|---|
| [DA-01](#da-01--cagr-em-vez-da-média-anualizada) | CAGR em vez da média anualizada |
| [DA-02](#da-02--risco-medido-pela-volatilidade-dos-retornos) | Risco medido pela volatilidade dos retornos |
| [DA-03](#da-03--bases-salvas-em-csv) | Bases salvas em CSV |
| [DA-04](#da-04--cdi-e-bova11-como-referências) | CDI e BOVA11 como referências |
| [DA-05](#da-05--dias-extremos-mantidos) | Dias extremos mantidos |
| [DA-06](#da-06--pesos-iguais-com-rebalanceamento-como-alternativa) | Pesos iguais, com rebalanceamento como alternativa |

---

## DA-01 — CAGR em vez da média anualizada

- **Contexto:** a versão original anualizava a média dos retornos diários (× 246), o que superestima ativos voláteis: a GOL, que perdeu 51%, aparecia com "+19,6% ao ano".
- **Decisão:** usar o **CAGR** (crescimento anual composto) pelos anos de calendário.
- **Alternativas consideradas:** média aritmética anualizada e média dos retornos logarítmicos.
- **Consequência:** GOL com −8,6% ao ano; a carteira com 19,9% ao ano, coerente com R$ 10.000 → R$ 42.750.
- **Onde está:** `cagr` em `src/financas.py` (com teste); itens 5 e 6 da Fase 03.

## DA-02 — Risco medido pela volatilidade dos retornos

- **Contexto:** a versão original usava o desvio padrão do **preço**, que é maior só porque o preço do BOVA11 é maior.
- **Decisão:** medir o risco pela **volatilidade anual dos retornos diários** e pela **maior queda**; comparar risco e retorno pelo **Índice de Sharpe** (contra o CDI).
- **Alternativas consideradas:** desvio padrão do preço (versão original).
- **Consequência:** o BOVA11 passa de "ativo mais arriscado" para o **menos** volátil (26% ao ano).
- **Onde está:** `volatilidade`, `maior_queda` e `indice_sharpe` em `src/financas.py`; H6.

## DA-03 — Bases salvas em CSV

- **Contexto:** dados de internet mudam ou somem (o ticker GOLL4.SA saiu do Yahoo Finance).
- **Decisão:** salvar preços (com e sem dividendos) e o CDI em `Datasets/`, com a opção `ATUALIZAR_DADOS` para baixar de novo.
- **Alternativas consideradas:** baixar a cada execução.
- **Consequência:** resultados reproduzíveis; a GOL usa o preço sem ajuste na base com dividendos (limitação documentada).
- **Onde está:** item 1.2 da Fase 02.

## DA-04 — CDI e BOVA11 como referências

- **Contexto:** comparar só com o índice não mostra se valeu correr risco.
- **Decisão:** comparar a carteira com o **BOVA11** (mercado) e o **CDI** (renda fixa, sem risco).
- **Alternativas consideradas:** só o BOVA11 (versão original).
- **Consequência:** a carteira supera os dois no acumulado, e o Sharpe (0,25 contra 0,08 do BOVA11) mostra que o retorno extra compensou parte do risco.
- **Onde está:** Fase 04.

## DA-05 — Dias extremos mantidos

- **Contexto:** pela regra do IQR, de 3,2% a 6,0% dos pregões são outliers (numa normal seriam ~0,7%).
- **Decisão:** manter todos os dias.
- **Alternativas consideradas:** remover ou suavizar os dias extremos, o que esconderia o risco real (como março de 2020).
- **Consequência:** as medidas de risco refletem as "caudas gordas" do mercado.
- **Onde está:** item 2.6 da Fase 02.

## DA-06 — Pesos iguais, com rebalanceamento como alternativa

- **Contexto:** comprando e mantendo, a MGLU passa a dominar a carteira, que chega a cair 87%.
- **Decisão:** analisar a carteira de pesos iguais (20% por ação) comprada em 2015 e comparar com o **rebalanceamento anual**.
- **Alternativas consideradas:** otimização de pesos (exigiria prever retornos futuros).
- **Consequência:** rebalanceando, R$ 62.147 com queda máxima de −62%, contra R$ 42.750 e −87% sem rebalancear.
- **Onde está:** `simular_carteira(rebalancear=True)` em `src/financas.py`; item 7 da Fase 03.
