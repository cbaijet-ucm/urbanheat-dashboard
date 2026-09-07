from pathlib import Path
import sys

from streamlit.testing.v1 import AppTest


DASHBOARD_DIR = Path(__file__).resolve().parents[1]
if str(DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_DIR))

from components.wireframe import SECTION_STRUCTURE, anchor_id


def test_arrow_navigation_visits_every_route_once() -> None:
    app = AppTest.from_file(str(DASHBOARD_DIR / "app.py"))
    app.run(timeout=60)
    assert not app.exception

    sections = list(SECTION_STRUCTURE)
    for section_index, section in enumerate(sections):
        subsections = list(SECTION_STRUCTURE[section])
        assert app.session_state["active_section"] == section
        assert app.session_state["active_subsection"] == subsections[0]

        for target_subsection in subsections[1:]:
            current_subsection = app.session_state["active_subsection"]
            button_key = f"navigate_down_{anchor_id(section, current_subsection)}"
            app.button(key=button_key).click()
            app.run(timeout=60)
            assert not app.exception
            assert app.session_state["active_section"] == section
            assert app.session_state["active_subsection"] == target_subsection

        if section_index + 1 < len(sections):
            button_key = f"navigate_right_{anchor_id(section, subsections[-1])}"
            app.button(key=button_key).click()
            app.run(timeout=60)
            assert not app.exception
            next_section = sections[section_index + 1]
            assert app.session_state["active_section"] == next_section
            assert app.session_state["active_subsection"] == next(
                iter(SECTION_STRUCTURE[next_section])
            )


def test_vulnerability_second_slide_renders_without_error() -> None:
    app = AppTest.from_file(str(DASHBOARD_DIR / "app.py"))
    app.run(timeout=60)
    for button_key in (
        "navigate_right_route-introduccion-portada",
        "navigate_right_route-dataset-area-de-estudio",
        "navigate_right_route-modelizacion-metodologia",
        "navigate_down_route-analisis-sociodemografico-agregacion",
    ):
        app.button(key=button_key).click()
        app.run(timeout=60)
        assert not app.exception

    assert app.session_state["active_section"] == "Análisis sociodemográfico"
    assert app.session_state["active_subsection"] == "Vulnerabilidad"
    app.button(key="sociodemografico_vulnerabilidad_slide_trigger_button").click()
    app.run(timeout=60)
    assert not app.exception
    assert app.session_state["sociodemografico_vulnerabilidad_slide_index"] == 1
