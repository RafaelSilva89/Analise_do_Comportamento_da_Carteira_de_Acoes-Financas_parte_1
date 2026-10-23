"""Teste do app Streamlit: abre sem erro, respeita as datas escolhidas e desativa a GOL depois de 2022."""
from datetime import date
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / 'app.py')


def abrir():
    return AppTest.from_file(APP, default_timeout=60).run()


def test_app_abre_com_2015_a_2025_e_gol_desativada():
    app = abrir()
    assert not app.exception
    assert len(app.metric) == 4
    gol = next(s for s in app.sidebar.slider if s.label.startswith('GOL'))
    assert gol.disabled and gol.value == 0
    assert len(app.table) == 1 and len(app.table[0].value) == 3   # pré, pandemia e pós


def test_app_libera_a_gol_quando_o_periodo_termina_ate_2022():
    app = abrir()
    app.sidebar.date_input[1].set_value(date(2022, 12, 29)).run()
    assert not app.exception
    gol = next(s for s in app.sidebar.slider if s.label.startswith('GOL'))
    assert not gol.disabled and gol.value == 20


def test_app_avisa_quando_as_datas_estao_invertidas():
    app = abrir()
    app.sidebar.date_input[0].set_value(date(2024, 1, 2))
    app.sidebar.date_input[1].set_value(date(2023, 1, 2)).run()
    assert any('depois da data de início' in aviso.value for aviso in app.warning)
