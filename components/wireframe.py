"""Estructura navegable, deliberadamente libre de contenido final."""

import streamlit as st
import unicodedata

from components.prototype_content import (
    render_cell_scene_table,
    render_object_canvas_editor,
    render_pipeline_image,
    render_sentinel_indices_interactive,
    render_meteo_slide_deck,
    render_scope_slide,
    render_target_lst_slide_deck,
    render_topomorphological_slide_deck,
    render_land_cover_slide_deck,
    render_distancias_slide_deck,
    render_modelizacion_metodologia_slide_deck,
    render_modelizacion_visualizacion_slide_deck,
    render_territorial_lst_map,
    render_sociodemografico_vulnerabilidad_hybrid,
)


SECTION_STRUCTURE = {
    "Introducción": {
        "Scope": "HTML",
        "Pipeline": "Infografía / imagen fija",
        "Stack tecnológico": "HTML",
    },
    "Dataset": {
        "Área de estudio": "HTML",
        "Target LST": "HTML · 2 slides",
        "Predictores / Índices espectrales": "Texto + mapa / chart no interactivo",
        "Predictores / Topomorfológicas": "HTML · 2 slides",
        "Predictores / Land cover": "HTML · 2 slides",
      "Predictores / Distancias": "Mapa interactivo + HTML · 2 slides",
        "Predictores / Meteo": "HTML · Mapa interactivo · HTML · 3 slides",
        "Matriz celda-escena": "Texto + infografía / imagen fija",
    },
    "Modelización": {
        "Metodología": "HTML · 2 slides (Formulación, Split)",
        "Modelo tabular": "HTML",
        "Red CNN / Entrenamiento": "HTML",
        "Red CNN / Arquitectura final": "HTML",
        "Resultados / Métricas": "HTML",
        "Resultados / Visualización": "Mapa interactivo · HTML · Mapa interactivo · 3 slides",
    },
    "Análisis sociodemográfico": {
        "Agregación": "Mapa interactivo",
        "Vulnerabilidad": "HTML + mapa interactivo · pantalla híbrida 40/60",
    },
    "Síntesis": {
        "Conclusiones": "HTML",
        "Ir más allá": "HTML",
    },
}


def anchor_id(section: str, subsection: str) -> str:
    value = unicodedata.normalize("NFKD", f"{section}-{subsection}").encode("ascii", "ignore").decode().lower()
    return "route-" + "".join(character if character.isalnum() else "-" for character in value).strip("-")


def _placeholder(label: str, kind: str) -> None:
    st.markdown(
        f'<div class="placeholder placeholder-{kind}"><span>{label}</span><small>placeholder</small></div>',
        unsafe_allow_html=True,
    )


def _screen_key(section: str, subsection: str) -> str:
    return "screen_" + anchor_id(section, subsection).replace("-", "_")


def _subsection_header(subsection: str, state: str, is_active: bool) -> None:
    # Presentación no añade un título intermedio al contenido precargado: al
    # activarlo la altura del documento permanece idéntica y no hay rebote.
    title = "" if (is_active or st.session_state.get("presentation_mode", False)) else f"<h2>{subsection}</h2>"
    st.markdown(f'<div class="subsection-block{state}">{title}</div>', unsafe_allow_html=True)


def render_parent_page(
    section: str,
    active_subsection: str,
    loaded_subsections: set[tuple[str, str]],
    only_subsections: set[str] | None = None,
) -> None:
    """Renderiza la página larga del padre y materializa sólo rutas ya visitadas."""
    visible_items = [
        (subsection, composition)
        for subsection, composition in SECTION_STRUCTURE[section].items()
        if only_subsections is None or subsection in only_subsections
    ]
    for visible_index, (subsection, composition) in enumerate(visible_items):
        route = (section, subsection)
        route_anchor = anchor_id(section, subsection)
        is_active = subsection == active_subsection
        if visible_index > 0:
            st.markdown('<div class="explicit-screen-gap" aria-hidden="true"></div>', unsafe_allow_html=True)
        with st.container(key=_screen_key(section, subsection)):
            st.markdown(f'<section id="{route_anchor}" class="subsection-anchor"></section>', unsafe_allow_html=True)
            if route not in loaded_subsections:
                st.markdown(
                    f'<div class="deferred-block"><h2>{subsection}</h2><div class="deferred-rule"></div></div>',
                    unsafe_allow_html=True,
                )
                continue

            state = " subsection-active" if is_active else ""

            if section == "Introducción" and subsection == "Scope":
                with st.container(key="movable_scope_slide"):
                    _subsection_header(subsection, state, is_active)
                    render_scope_slide()
                continue
            if section == "Introducción" and subsection == "Pipeline":
                with st.container(key="movable_pipeline_figure"):
                    _subsection_header(subsection, state, is_active)
                    render_pipeline_image()
                continue
            if section == "Introducción" and subsection == "Stack tecnológico":
                with st.container(key="movable_stack_tecnologico_html"):
                    _subsection_header(subsection, state, is_active)
                    render_object_canvas_editor("stack_tecnologico")
                continue

            # Contenido de prueba: se invoca únicamente cuando esta ruta ya fue visitada.
            if section == "Dataset" and subsection == "Matriz celda-escena":
                with st.container(key="movable_cell_scene_table"):
                    _subsection_header(subsection, state, is_active)
                    render_cell_scene_table()
                continue
            if section == "Dataset" and subsection == "Target LST":
                with st.container(key="movable_target_lst_slides"):
                    _subsection_header(subsection, state, is_active)
                    render_target_lst_slide_deck()
                continue
            if section == "Dataset" and subsection == "Área de estudio":
                with st.container(key="movable_area_estudio_html"):
                    _subsection_header(subsection, state, is_active)
                    render_object_canvas_editor("area_estudio")
                continue
            if section == "Dataset" and subsection == "Predictores / Índices espectrales":
                with st.container(key="movable_sentinel_indices_comparison"):
                    _subsection_header(subsection, state, is_active)
                    render_sentinel_indices_interactive()
                continue
            if section == "Dataset" and subsection == "Predictores / Meteo":
                with st.container(key="movable_meteo_slides"):
                    _subsection_header(subsection, state, is_active)
                    render_meteo_slide_deck()
                continue
            if section == "Dataset" and subsection == "Predictores / Distancias":
                with st.container(key="movable_editor_distancias"):
                    _subsection_header(subsection, state, is_active)
                    render_distancias_slide_deck()
                continue
            if section == "Dataset" and subsection == "Predictores / Land cover":
                with st.container(key="movable_editor_land_cover"):
                    _subsection_header(subsection, state, is_active)
                    render_land_cover_slide_deck()
                continue
            if section == "Dataset" and subsection == "Predictores / Topomorfológicas":
                with st.container(key="movable_editor_topomorfologicas"):
                    _subsection_header(subsection, state, is_active)
                    render_topomorphological_slide_deck()
                continue
            if section == "Modelización" and subsection == "Metodología":
                with st.container(key="movable_modelizacion_metodologia"):
                    _subsection_header(subsection, state, is_active)
                    render_modelizacion_metodologia_slide_deck()
                continue
            if section == "Modelización" and subsection == "Resultados / Métricas":
                with st.container(key="movable_modelizacion_resultados_metricas"):
                    _subsection_header(subsection, state, is_active)
                    render_object_canvas_editor("modelizacion_resultados_metricas_1")
                continue
            if section == "Modelización" and subsection == "Resultados / Visualización":
                with st.container(key="movable_modelizacion_visualizacion"):
                    _subsection_header(subsection, state, is_active)
                    render_modelizacion_visualizacion_slide_deck()
                continue
            if section == "Modelización" and subsection in {
                "Modelo tabular",
                "Red CNN / Entrenamiento",
                "Red CNN / Arquitectura final",
            }:
                storage_suffix = {
                    "Modelo tabular": "modelizacion_tabular_temporal",
                    "Red CNN / Entrenamiento": "modelizacion_red_cnn_entrenamiento",
                    "Red CNN / Arquitectura final": "modelizacion_deep_learning_arquitectura_training",
                }[subsection]
                with st.container(key=f"movable_{storage_suffix}"):
                    _subsection_header(subsection, state, is_active)
                    render_object_canvas_editor(storage_suffix)
                continue
            if section == "Análisis sociodemográfico" and subsection == "Agregación":
                with st.container(key="movable_sociodemografico_agregacion"):
                    _subsection_header(subsection, state, is_active)
                    render_territorial_lst_map()
                continue
            if section == "Análisis sociodemográfico" and subsection == "Vulnerabilidad":
                with st.container(key="movable_sociodemografico_vulnerabilidad"):
                    _subsection_header(subsection, state, is_active)
                    render_sociodemografico_vulnerabilidad_hybrid()
                continue
            if section == "Síntesis" and subsection in {"Conclusiones", "Ir más allá"}:
                storage_suffix = "conclusiones_1" if subsection == "Conclusiones" else "conclusiones_2"
                with st.container(key=f"movable_{storage_suffix}"):
                    _subsection_header(subsection, state, is_active)
                    render_object_canvas_editor(storage_suffix)
                continue
            with st.container(key=f"movable_{anchor_id(section, subsection).replace('-', '_')}"):
                _subsection_header(subsection, state, is_active)
                st.markdown(
                    '<p class="lede">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec sed erat sed arcu posuere interdum.</p>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    '<p class="wire-copy">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla facilisi. Suspendisse non sem ut massa elementum tincidunt.</p>',
                    unsafe_allow_html=True,
                )
                if composition != "Texto":
                    if "tabla" in composition:
                        _placeholder("Tabla de resultados", "table")
                    elif "infografía" in composition:
                        _placeholder("Infografía / imagen fija", "wide")
                    elif "interactivo" in composition:
                        _placeholder("Mapa / chart interactivo", "map")
                    else:
                        _placeholder("Mapa / chart no interactivo", "chart")
