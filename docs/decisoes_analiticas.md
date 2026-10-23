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
| [DA-07](#da-07--extensão-até-2025-em-uma-seção-própria-com-4-ações) | Extensão até 2025 em uma seção própria, com 4 ações |
| [DA-08](#da-08--três-fases-da-covid) | Três fases da Covid |

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

## DA-07 — Extensão até 2025 em uma seção própria, com 4 ações

- **Contexto:** o usuário pediu a análise até 2025. A GOL não tem dados públicos gratuitos depois de 29/12/2022: depois da recuperação judicial, a ação virou GOLL54, passou a valer menos de R$ 0,01 e está saindo da bolsa (o Yahoo Finance não tem o ticker).
- **Decisão:** manter a análise principal (2015–2022, 5 ações) comparável com a versão original e acrescentar a extensão até 2025 no item 1.2 da Fase 04, com uma **carteira de 4 ações** (25% em cada), em bases novas (`*_2015_2025.csv`). As bases antigas não mudam, para que a versão original continue reproduzível.
- **Alternativas consideradas:** manter a GOL até 2022 e redistribuir o peso dela depois (mistura duas carteiras); obter os dados da GOL em fonte paga.
- **Consequência:** 2023–2025 funcionam como teste fora do tempo; a vantagem da carteira não se repetiu (R$ 9.595 x R$ 15.395 do BOVA11). O download novo ajusta o preço da CVC pelos aumentos de capital de 2020 a 2022, então os números da CVC até 2022 diferem um pouco dos da análise principal.
- **Onde está:** item 1.2 da Fase 04; `ativos_com_dados` em `src/financas.py`; no app, a GOL fica desativada em períodos que terminam depois de 2022.

## DA-08 — Três fases da Covid

- **Contexto:** para comparar o comportamento antes e depois da Covid, é preciso definir datas objetivas.
- **Decisão:** **pré-pandemia** até 19/02/2020 (véspera da queda da bolsa), **pandemia** de 20/02/2020 a 05/05/2023 (fim da emergência de saúde declarado pela OMS) e **pós-pandemia** até 30/12/2025. Em cada fase, a carteira é comprada no primeiro pregão da fase.
- **Alternativas consideradas:** pandemia só em 2020–2021 (fase mais aguda).
- **Consequência:** carteira com +75,0% ao ano antes, −8,6% durante e −1,9% depois; BOVA11 com +18,3%, −2,4% e +17,8%.
- **Onde está:** `PERIODOS_COVID` e `classificar_periodo` em `src/financas.py`; item 1.2 da Fase 04; tabela por fase no app.
