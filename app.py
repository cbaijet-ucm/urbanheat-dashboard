"""Estructura de navegación para la revisión visual del dashboard."""

from pathlib import Path
import hashlib
import hmac
import sys
import re
import unicodedata
import json

import streamlit as st
import streamlit.components.v1 as components
from html import escape

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from components.styles import apply_global_styles
from components.wireframe import SECTION_STRUCTURE, anchor_id, render_parent_page
from components.prototype_content import render_slide_navigation
from data.content_store import ensure_content_store_server

EDITOR_PASSWORD_SHA256 = "ff281492a15f80db594fe7898c7358eb92744c82278d75a2f7de06a32a149855"

st.set_page_config(page_title="UrbanHeat BCN", layout="wide", initial_sidebar_state="expanded")
ensure_content_store_server()
if "admin_controls_unlocked" not in st.session_state:
    st.session_state.admin_controls_unlocked = False
if "secret_access_requested" not in st.session_state:
    st.session_state.secret_access_requested = False
if "secret_access_error" not in st.session_state:
    st.session_state.secret_access_error = False
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
if "presentation_mode" not in st.session_state:
    st.session_state.presentation_mode = False
if "presentation_toggle" not in st.session_state:
    st.session_state.presentation_toggle = False
if not st.session_state.admin_controls_unlocked:
    st.session_state.edit_mode = False
    st.session_state.presentation_mode = False
    st.session_state.presentation_toggle = False
apply_global_styles()
st.markdown(
    """
    <style>
      .breadcrumb-title, .breadcrumb-title span {
        font-family: Helvetica, Arial, sans-serif !important;
        font-weight: 300 !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# El control nativo de Streamlit queda oculto con la cabecera minimalista. Esta
# pequeña flecha sólo se muestra al plegar el sidebar y delega en dicho control.
with st.container(key="sidebar_reopen"):
    components.html(
        """
        <style>html,body{margin:0;background:transparent;overflow:hidden}button{width:32px;height:32px;border:1px solid #e4e4e4;background:#fff;color:#161616;font-size:17px;line-height:1;cursor:pointer}</style>
        <button aria-label="Mostrar menú lateral" title="Mostrar menú lateral">›</button>
        <script>
          document.querySelector('button').addEventListener('click', () => {
            const root = window.parent.document;
            const sidebar = root.querySelector('[data-testid="stSidebar"]');
            if (sidebar) {
              sidebar.setAttribute('aria-expanded', 'true');
              sidebar.style.transform = 'none';
              sidebar.style.visibility = 'visible';
              sidebar.style.minWidth = '256px';
              sidebar.style.width = '256px';
            }
          });
        </script>
        """,
        height=32,
        width=32,
    )

with st.container(key="layout_left_guide"):
    components.html(
        """
        <style>html,body{margin:0;background:transparent;overflow:hidden}</style>
        <script>
          const root = window.parent.document;
          const storageKey = 'urbanheat-layout-left-guide';
          let guide = root.getElementById('urbanheat-left-guide');
          if (!guide) {
            guide = root.createElement('div');
            guide.id = 'urbanheat-left-guide';
            guide.innerHTML = '<div id="urbanheat-left-guide-tag"></div>';
            root.body.appendChild(guide);
          }
          const tag = guide.querySelector('#urbanheat-left-guide-tag');
          guide.style.cssText = 'position:fixed;top:0;bottom:0;left:120px;width:10px;z-index:2500;background:transparent;pointer-events:none;';
          tag.style.cssText = 'position:absolute;top:6px;left:8px;background:#fff;border:1px solid #d0d0d0;color:#0000ff;font:11px Arial,sans-serif;padding:2px 4px;white-space:nowrap;';
          if (!root.getElementById('urbanheat-left-guide-style')) {
            const style = root.createElement('style');
            style.id = 'urbanheat-left-guide-style';
            style.textContent = '#urbanheat-left-guide::before{content:"";position:absolute;top:0;bottom:0;left:4px;width:1px;background:rgb(0,0,255);opacity:.45}';
            root.head.appendChild(style);
          }
          localStorage.setItem(storageKey, '120');
          tag.textContent = '120px';
        </script>
        """,
        height=1,
        width=1,
    )

sections = list(SECTION_STRUCTURE)

if "active_section" not in st.session_state:
    st.session_state.active_section = "Introducción"
    st.session_state.active_subsection = "Portada"
    st.session_state.loaded_subsections = {("Introducción", "Portada")}
    st.session_state.scroll_target = anchor_id("Introducción", "Portada")

# Migra rutas guardadas de versiones anteriores de la estructura.
if st.session_state.get("active_section") == "Datos":
    st.session_state.active_section = "Dataset"
    legacy_subsection = st.session_state.get("active_subsection", "Área de estudio")
    st.session_state.active_subsection = {
        "Escenas": "Target LST",
        "Dataset celda–escena": "Matriz celda-escena",
        "Dataset celda-escena": "Matriz celda-escena",
    }.get(legacy_subsection, legacy_subsection)

if (
    st.session_state.get("active_section") == "Introducción"
    and st.session_state.get("active_subsection") in {"Scope y Motivación", "Motivación"}
):
    st.session_state.active_subsection = "Scope"
    st.session_state.loaded_subsections.add(("Introducción", "Scope"))
    st.session_state.scroll_target = anchor_id("Introducción", "Scope")
elif (
    st.session_state.get("active_section") == "Introducción"
    and st.session_state.get("active_subsection") == "Stack Tecnológico"
):
    st.session_state.active_subsection = "Stack tecnológico"
    st.session_state.loaded_subsections.add(("Introducción", "Stack tecnológico"))

legacy_sections = {
    "MODELIZACIÓN": "Modelización",
    "ESTUDIO SOCIODEMOGRÁFICO": "Análisis sociodemográfico",
    "Estudio sociodemográfico": "Análisis sociodemográfico",
    "CONCLUSIONES": "Síntesis",
    "Conclusiones": "Síntesis",
}
st.session_state.active_section = legacy_sections.get(
    st.session_state.get("active_section"), st.session_state.get("active_section")
)
legacy_model_routes = {
    "METODOLOGÍA": "Metodología",
    "MODELO TABULAR / MODELO TEMPORAL": "Modelo tabular",
    "MODELO TABULAR / MODELO XGBOOST": "Modelo tabular",
    "Modelo tabular / Temporal": "Modelo tabular",
    "Modelo tabular / XGBoost": "Modelo tabular",
    "MODELO DEEP LEARNING / DATASET": "Red CNN / Arquitectura final",
    "MODELO DEEP LEARNING / ARQUITECTURA + TRAINING": "Red CNN / Arquitectura final",
    "Red CNN / Dataset": "Red CNN / Arquitectura final",
    "Red CNN / Arquitectura + training": "Red CNN / Arquitectura final",
    "Red CNN / Arquitectura": "Red CNN / Arquitectura final",
    "RESULTADOS / MÉTRICAS": "Resultados / Métricas",
    "RESULTADOS / VISUALIZACIÓN": "Resultados / Visualización",
}
if st.session_state.active_section == "Modelización":
    st.session_state.active_subsection = legacy_model_routes.get(
        st.session_state.get("active_subsection"), st.session_state.get("active_subsection")
    )
if st.session_state.active_section == "Análisis sociodemográfico":
    st.session_state.active_subsection = {
        "AGREGACIÓN": "Agregación",
        "ANALISIS VULNERABILIDAD": "Vulnerabilidad",
        "Análisis vulnerabilidad": "Vulnerabilidad",
    }.get(st.session_state.get("active_subsection"), st.session_state.get("active_subsection"))
if (
    st.session_state.get("active_section") == "Dataset"
    and st.session_state.get("active_subsection") == "Predictores / Land Cover"
):
    st.session_state.active_subsection = "Predictores / Land cover"
    st.session_state.loaded_subsections.add(("Dataset", "Predictores / Land cover"))

if (
    st.session_state.get("active_section") == "Síntesis"
    and st.session_state.get("active_subsection") == "Síntesis"
):
    st.session_state.active_subsection = "Conclusiones"
    st.session_state.loaded_subsections.add(("Síntesis", "Conclusiones"))
    st.session_state.scroll_target = anchor_id("Síntesis", "Conclusiones")

if st.session_state.active_section not in SECTION_STRUCTURE:
    st.session_state.active_section = "Dataset"
    st.session_state.active_subsection = next(iter(SECTION_STRUCTURE["Dataset"]))
    st.session_state.loaded_subsections.add(
        (st.session_state.active_section, st.session_state.active_subsection)
    )

# Migra sesiones abiertas cuando una ruta plana pasa a tener un tercer nivel.
if st.session_state.active_subsection not in SECTION_STRUCTURE[st.session_state.active_section]:
    if st.session_state.active_section == "Dataset" and st.session_state.active_subsection == "Predictores":
        st.session_state.active_subsection = "Predictores / Índices espectrales"
    else:
        st.session_state.active_subsection = next(iter(SECTION_STRUCTURE[st.session_state.active_section]))
    st.session_state.loaded_subsections.add(
        (st.session_state.active_section, st.session_state.active_subsection)
    )


def go_to(section: str, subsection: str) -> None:
    st.session_state.active_section = section
    st.session_state.active_subsection = subsection
    st.session_state.loaded_subsections.add((section, subsection))
    st.session_state.scroll_target = anchor_id(section, subsection)
    st.session_state.normal_initial_slide = 0
    if section == "Dataset" and subsection == "Predictores / Distancias":
        st.session_state.distancias_slide_index = 0
    if section == "Dataset" and subsection == "Predictores / Meteo":
        st.session_state.meteo_slide_index = 0


def _navigation_button(
    label: str,
    direction: str,
    current_route: tuple[str, str],
    target: tuple[str, str] | None,
) -> None:
    """Render a route-bound button whose click cannot leak into another route."""
    route_key = anchor_id(*current_route)
    if target is None:
        st.button(
            label,
            key=f"navigate_{direction}_{route_key}",
            disabled=True,
        )
        return
    st.button(
        label,
        key=f"navigate_{direction}_{route_key}",
        on_click=go_to,
        args=target,
    )


def _presentation_slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", normalized).strip()


PRESENTATION_TARGETS = {
    "introduccion / portada": ("Introducción", "Portada", None),
    "introduccion / scope / slide 1 · scope": ("Introducción", "Scope", 0),
    "introduccion / scope / slide 2 · motivacion": ("Introducción", "Scope", 1),
    "introduccion / pipeline": ("Introducción", "Pipeline", None),
    "introduccion / stack tecnologico": ("Introducción", "Stack tecnológico", None),
    "dataset / area de estudio": ("Dataset", "Área de estudio", None),
    "dataset / target lst / slide 1": ("Dataset", "Target LST", 0),
    "dataset / target lst / slide 2": ("Dataset", "Target LST", 1),
    "dataset / predictores / indices espectrales · comparacion interactiva sentinel-2": ("Dataset", "Predictores / Índices espectrales", None),
    "dataset / predictores / topomorfologicas / slide 1": ("Dataset", "Predictores / Topomorfológicas", 0),
    "dataset / predictores / topomorfologicas / slide 2": ("Dataset", "Predictores / Topomorfológicas", 1),
    "dataset / predictores / land cover / slide 1": ("Dataset", "Predictores / Land cover", 0),
    "dataset / predictores / land cover / slide 2": ("Dataset", "Predictores / Land cover", 1),
    "dataset / predictores / distancias / slide 1 · mapa interactivo de parques y refugios": ("Dataset", "Predictores / Distancias", 0),
    "dataset / predictores / distancias / slide 2 · html": ("Dataset", "Predictores / Distancias", 1),
    "dataset / predictores / meteo / slide 1 · html": ("Dataset", "Predictores / Meteo", 0),
    "dataset / predictores / meteo / slide 2 · mapa interactivo de evolucion meteorologica": ("Dataset", "Predictores / Meteo", 1),
    "dataset / predictores / meteo / slide 3 · html": ("Dataset", "Predictores / Meteo", 2),
    "dataset / matriz celda-escena": ("Dataset", "Matriz celda-escena", None),
    "modelizacion / metodologia / slide 1 · formulacion": ("Modelización", "Metodología", 0),
    "modelizacion / metodologia / slide 2 · split": ("Modelización", "Metodología", 1),
    "modelizacion / modelo tabular": ("Modelización", "Modelo tabular", None),
    "modelizacion / red cnn / entrenamiento": ("Modelización", "Red CNN / Entrenamiento", None),
    "modelizacion / red cnn / arquitectura final": ("Modelización", "Red CNN / Arquitectura final", None),
    "modelizacion / resultados / metricas · html": ("Modelización", "Resultados / Métricas", None),
    "modelizacion / resultados / visualizacion / slide 1 · html": ("Modelización", "Resultados / Visualización", 0),
    "modelizacion / resultados / visualizacion / slide 2 · prediccion xgboost vs red cnn": ("Modelización", "Resultados / Visualización", 1),
    "modelizacion / resultados / visualizacion / slide 3 · diferencia de error cnn vs xgboost": ("Modelización", "Resultados / Visualización", 2),
    "analisis sociodemografico / agregacion · mapa interactivo": ("Análisis sociodemográfico", "Agregación", None),
    "analisis sociodemografico / vulnerabilidad · html + mapa interactivo": ("Análisis sociodemográfico", "Vulnerabilidad", None),
    "sintesis / conclusiones · html": ("Síntesis", "Conclusiones", None),
    "sintesis / ir mas alla · html": ("Síntesis", "Ir más allá", None),
}
PRESENTATION_TARGETS = {
    _presentation_slug(path): target for path, target in PRESENTATION_TARGETS.items()
}

PRESENTATION_DECKS = {
    ("Introducción", "Scope"): ("scope_motivation_slide", 2),
    ("Dataset", "Target LST"): ("target_lst_slide", 2),
    ("Dataset", "Predictores / Topomorfológicas"): ("topomorfologicas_slide", 2),
    ("Dataset", "Predictores / Land cover"): ("land_cover_slide", 2),
    ("Dataset", "Predictores / Distancias"): ("distancias_slide", 2),
    ("Dataset", "Predictores / Meteo"): ("meteo_slide", 3),
    ("Modelización", "Metodología"): ("modelizacion_metodologia_slide", 2),
    ("Modelización", "Resultados / Visualización"): ("modelizacion_visualizacion_slide", 3),
}


@st.cache_data(show_spinner=False)
def load_presentation_plan(markdown_mtime_ns: int) -> list[tuple[int, str, str, int | None]]:
    """Convierte el árbol Markdown del usuario en una secuencia de pantallas."""
    markdown = APP_DIR / "presentation_order.md"
    section = ""
    hierarchy: dict[int, str] = {}
    entries: list[tuple[int, str, str, int | None]] = []
    for raw_line in markdown.read_text(encoding="utf-8").splitlines():
        if raw_line.startswith("## "):
            section = raw_line[3:].strip()
            hierarchy.clear()
            continue
        bullet = re.match(r"^(\s*)-\s+(.+?)\s*$", raw_line)
        if not bullet or not section:
            continue
        depth = len(bullet.group(1).expandtabs(2)) // 2
        numbered = re.match(r"^(.+?)\s+—\s+(\d+)\s*$", bullet.group(2).strip())
        label = (numbered.group(1) if numbered else bullet.group(2)).strip()
        hierarchy[depth] = label
        for child_depth in tuple(hierarchy):
            if child_depth > depth:
                del hierarchy[child_depth]
        path = " / ".join([section, *[hierarchy[index] for index in sorted(hierarchy)]])
        target = PRESENTATION_TARGETS.get(_presentation_slug(path))
        order = int(numbered.group(2)) if numbered else 0
        if order > 0 and target:
            entries.append((order, *target))
    return sorted(entries, key=lambda entry: entry[0])


def _presentation_plan() -> list[tuple[int, str, str, int | None]]:
    markdown = APP_DIR / "presentation_order.md"
    if not markdown.is_file():
        return []
    return load_presentation_plan(markdown.stat().st_mtime_ns)


def _apply_presentation_target(target: tuple[int, str, str, int | None]) -> None:
    _, section, subsection, slide_index = target
    go_to(section, subsection)
    st.session_state.presentation_slide_index = slide_index
    if section == "Dataset" and subsection == "Predictores / Distancias":
        st.session_state.distancias_slide_index = slide_index or 0
    elif section == "Dataset" and subsection == "Predictores / Meteo":
        st.session_state.meteo_slide_index = slide_index or 0


def enter_presentation_mode() -> None:
    """Activa la presentación; el toggle es solo un disparador transitorio."""
    if not st.session_state.get("presentation_toggle", False):
        return
    plan = _presentation_plan()
    if not plan:
        st.session_state.presentation_toggle = False
        st.session_state.presentation_mode = False
        return
    st.session_state.presentation_mode = True
    st.session_state.presentation_previous_edit_mode = st.session_state.edit_mode
    st.session_state.edit_mode = False
    st.session_state.loaded_subsections.update(
        (section, subsection) for _, section, subsection, _ in plan
    )
    _apply_presentation_target(plan[0])


def exit_presentation_mode() -> None:
    """Sale del estado persistente y prepara un reload limpio del dashboard."""
    st.session_state.presentation_mode = False
    st.session_state.presentation_toggle = False
    st.session_state.edit_mode = st.session_state.pop("presentation_previous_edit_mode", False)
    st.session_state.reload_after_presentation_exit = True


def exit_presentation_to(target_index: int) -> None:
    """Sale a una ruta concreta y descarta por completo el deck precargado."""
    plan = _presentation_plan()
    if not plan:
        exit_presentation_mode()
        return
    target_index = max(0, min(target_index, len(plan) - 1))
    _, section, subsection, slide_index = plan[target_index]
    st.session_state.loaded_subsections = {(section, subsection)}
    _apply_presentation_target(plan[target_index])
    st.session_state.normal_initial_slide = slide_index or 0
    exit_presentation_mode()


def adjacent_section(offset: int) -> tuple[str, str] | None:
    current_index = sections.index(st.session_state.active_section)
    target_index = current_index + offset
    if 0 <= target_index < len(sections):
        section = sections[target_index]
        return section, next(iter(SECTION_STRUCTURE[section]))
    return None


def scroll_to(target: str) -> None:
    components.html(
        f"""
        <script>
        const target = window.parent.document.getElementById({target!r});
        if (target) {{
          const parentWindow = window.parent;
          const parentDocument = parentWindow.document;
          const isScrollable = (node) => {{
            const style = parentWindow.getComputedStyle(node);
            return /(auto|scroll)/.test(style.overflowY) && node.scrollHeight > node.clientHeight;
          }};
          let scroller = target.parentElement;
          while (scroller && !isScrollable(scroller)) scroller = scroller.parentElement;
          scroller = scroller || parentDocument.scrollingElement;
          if (!scroller) {{
            target.scrollIntoView({{behavior: 'smooth', block: 'start'}});
          }} else {{
            const isDocumentScroller = scroller === parentDocument.scrollingElement;
            const current = scroller.scrollTop;
            const containerTop = isDocumentScroller ? 0 : scroller.getBoundingClientRect().top;
            const header = parentDocument.querySelector('.st-key-route_header');
            const offset = target.id === 'route-introduccion-portada' && header
              ? header.getBoundingClientRect().bottom
              : 74;
            const destination = current + target.getBoundingClientRect().top - containerTop - offset;
            const distance = destination - current;
            const duration = {30 if st.session_state.presentation_mode else "Math.min(360, Math.max(160, Math.abs(distance) * 0.09))"};
            const startedAt = performance.now();
            const tick = (now) => {{
              const progress = Math.min((now - startedAt) / duration, 1);
              const eased = 1 - Math.pow(1 - progress, 3);
              scroller.scrollTop = current + distance * eased;
              if (progress < 1) {{
                requestAnimationFrame(tick);
              }} else if (target.id === 'route-introduccion-portada' && header) {{
                requestAnimationFrame(() => requestAnimationFrame(() => {{
                  const correction = target.getBoundingClientRect().top - header.getBoundingClientRect().bottom;
                  scroller.scrollTop += correction;
                }}));
              }}
            }};
            requestAnimationFrame(tick);
          }}
        }}
        </script>
        """,
        height=0,
        width=0,
    )


def reveal_secret_access() -> None:
    st.session_state.secret_access_requested = True
    st.session_state.secret_access_error = False


def unlock_admin_controls() -> None:
    candidate = st.session_state.get("secret_editor_password", "")
    digest = hashlib.sha256(candidate.encode("utf-8")).hexdigest()
    if hmac.compare_digest(digest, EDITOR_PASSWORD_SHA256):
        st.session_state.admin_controls_unlocked = True
        st.session_state.secret_access_requested = False
        st.session_state.secret_access_error = False
        st.session_state.edit_mode = True
        st.session_state.presentation_mode = False
        st.session_state.presentation_toggle = False
        st.session_state.secret_editor_password = ""
        return
    st.session_state.secret_access_error = True


with st.sidebar:
    logo = Path(__file__).resolve().parent / "assets" / "graphic" / "Logo.png"
    if logo.exists():
        with st.container(key="sidebar_logo"):
            st.image(str(logo), width="stretch")
        st.button(
            "Abrir acceso privado",
            key="secret_access_trigger",
            on_click=reveal_secret_access,
        )
        components.html(
            """
            <script>
              const root = window.parent.document;
              const bindSecretLogoAccess = () => {
                const logo = root.querySelector('.st-key-sidebar_logo img');
                if (!logo || logo.dataset.urbanheatSecretAccessBound === 'true') return;
                logo.dataset.urbanheatSecretAccessBound = 'true';
                let clicks = [];
                logo.addEventListener('click', () => {
                  const now = Date.now();
                  clicks = clicks.filter((time) => now - time < 900);
                  clicks.push(now);
                  if (clicks.length < 3) return;
                  clicks = [];
                  root.querySelector('.st-key-secret_access_trigger button')?.click();
                });
              };
              bindSecretLogoAccess();
              window.parent.__urbanheatSecretAccessObserver?.disconnect();
              window.parent.__urbanheatSecretAccessObserver = new MutationObserver(bindSecretLogoAccess);
              window.parent.__urbanheatSecretAccessObserver.observe(root.body, {childList:true, subtree:true});
            </script>
            """,
            height=0,
            width=0,
        )
    if st.session_state.secret_access_requested and not st.session_state.admin_controls_unlocked:
        with st.container(key="secret_access_panel"):
            st.text_input(
                "Contraseña",
                type="password",
                key="secret_editor_password",
                on_change=unlock_admin_controls,
            )
            st.button("Entrar", key="secret_access_submit", on_click=unlock_admin_controls)
            if st.session_state.secret_access_error:
                st.error("Contraseña incorrecta")
    for section in sections:
        with st.expander(section, expanded=section == st.session_state.active_section):
            shown_nested_parents: set[str] = set()
            for subsection in SECTION_STRUCTURE[section]:
                subsection_parts = subsection.split(" / ", 1)
                button_label = subsection_parts[-1]
                is_nested = len(subsection_parts) == 2
                if is_nested and subsection_parts[0] not in shown_nested_parents:
                    with st.container(key=f"nav_parent_{anchor_id(section, subsection_parts[0])}"):
                        if st.button(
                            subsection_parts[0],
                            key=f"{section}_{subsection_parts[0]}_parent",
                            width="stretch",
                        ):
                            go_to(section, subsection)
                            st.rerun()
                    shown_nested_parents.add(subsection_parts[0])
                if is_nested and not st.session_state.active_subsection.startswith(f"{subsection_parts[0]} / "):
                    continue
                nav_state = "active" if (
                    section == st.session_state.active_section
                    and subsection == st.session_state.active_subsection
                ) else "item"
                nav_depth = "nested" if is_nested else "root"
                with st.container(key=f"nav_{nav_depth}_{nav_state}_{anchor_id(section, subsection)}"):
                    if st.button(button_label, key=f"{section}_{subsection}", width="stretch"):
                        go_to(section, subsection)
                        st.rerun()
    components.html(
        """
        <script>
          const root = window.parent.document;
          const bindAccordion = () => {
            const sidebar = root.querySelector('[data-testid="stSidebar"]');
            if (!sidebar) return;
            sidebar.querySelectorAll('details').forEach((details) => {
              if (details.dataset.urbanheatAccordionBound === 'true') return;
              details.dataset.urbanheatAccordionBound = 'true';
              details.addEventListener('toggle', () => {
                if (!details.open) return;
                sidebar.querySelectorAll('details[open]').forEach((other) => {
                  if (other !== details) other.open = false;
                });
              });
            });
          };
          bindAccordion();
          if (!root.body.dataset.urbanheatAccordionObserver) {
            root.body.dataset.urbanheatAccordionObserver = 'true';
            new MutationObserver(bindAccordion).observe(root.body, {childList: true, subtree: true});
          }
        </script>
        """,
        height=0,
        width=0,
    )

current_section = st.session_state.active_section
current_subsection = st.session_state.active_subsection
current_route = (current_section, current_subsection)
if st.session_state.get("_last_rendered_route") != current_route:
    if current_route == ("Dataset", "Predictores / Distancias"):
        st.session_state.distancias_slide_index = 0
    if current_route == ("Dataset", "Predictores / Meteo"):
        st.session_state.meteo_slide_index = 0
    st.session_state._last_rendered_route = current_route
subsections = list(SECTION_STRUCTURE[current_section])
subsection_index = subsections.index(current_subsection)
previous_section = adjacent_section(-1)
next_section = adjacent_section(1)
up_target = (
    (current_section, subsections[subsection_index - 1])
    if subsection_index > 0
    else None
)
down_target = (
    (current_section, subsections[subsection_index + 1])
    if subsection_index + 1 < len(subsections)
    else None
)

with st.container(key="route_header"):
    title_column, mode_column, controls_column = st.columns((10.8, 1.7, 2.6), gap="small", vertical_alignment="center")
    with title_column:
        if current_section == current_subsection:
            st.markdown(
                f'<h1 class="breadcrumb-title"><span class="breadcrumb-active">{escape(current_section)}</span></h1>',
                unsafe_allow_html=True,
            )
        else:
            breadcrumb_parts = [current_section, *current_subsection.split(" / ")]
            breadcrumb_prefix = ' <span>/</span> '.join(
                f'<span class="breadcrumb-prefix">{escape(part)}</span>' for part in breadcrumb_parts[:-1]
            )
            breadcrumb_active = escape(breadcrumb_parts[-1])
            st.markdown(
                f'<h1 class="breadcrumb-title">{breadcrumb_prefix} <span>/</span> <span class="breadcrumb-active">{breadcrumb_active}</span></h1>',
                unsafe_allow_html=True,
            )
    with mode_column:
        if st.session_state.admin_controls_unlocked:
            with st.container(key="mode_toggle"):
                if not st.session_state.presentation_mode:
                    st.toggle("Edición", key="edit_mode")
                    st.toggle("Presentación", key="presentation_toggle", on_change=enter_presentation_mode)
    with controls_column:
        if not st.session_state.presentation_mode:
            up, down, left, right = st.columns(4, gap="small")
            with up:
                _navigation_button("↑", "up", current_route, up_target)
            with down:
                _navigation_button("↓", "down", current_route, down_target)
            with left:
                _navigation_button("←", "left", current_route, previous_section)
            with right:
                _navigation_button("→", "right", current_route, next_section)

if st.session_state.presentation_mode:
    presentation_plan = _presentation_plan()
    for exit_index in range(len(presentation_plan)):
        with st.container(key=f"presentation_exit_{exit_index}"):
            st.button(
                "Salir de presentación",
                key=f"presentation_exit_button_{exit_index}",
                on_click=exit_presentation_to,
                args=(exit_index,),
            )
    presentation_payload = []
    for _, plan_section, plan_subsection, plan_slide in presentation_plan:
        title_parts = [plan_section, *plan_subsection.split(" / ")]
        title_prefix = " / ".join(title_parts[:-1])
        title_html = (
            f'<span class="breadcrumb-prefix">{escape(title_prefix)}</span> '
            f'<span>/</span> <span class="breadcrumb-active">{escape(title_parts[-1])}</span>'
            if title_prefix
            else f'<span class="breadcrumb-active">{escape(title_parts[-1])}</span>'
        )
        deck = PRESENTATION_DECKS.get((plan_section, plan_subsection))
        presentation_payload.append(
            {
                "anchor": anchor_id(plan_section, plan_subsection),
                "section": plan_section,
                "subsection": plan_subsection,
                "title_html": title_html,
                "slide": plan_slide,
                "deck_prefix": deck[0] if deck else None,
                "deck_count": deck[1] if deck else 0,
            }
        )
    components.html(
        """
        <script>
          const root=window.parent.document;
          const plan=__PRESENTATION_PLAN__;
          const parentWindow=window.parent;
          const state={index:0,busy:false};
          const warmFrame=(frame)=>{
            frame.loading='eager';
            const warm=()=>{try{
              const doc=frame.contentDocument;
              if(!doc) return;
              doc.querySelectorAll('img').forEach(image=>{
                image.loading='eager';
                if(image.src && !image.src.startsWith('data:')) fetch(image.src,{cache:'force-cache'}).catch(()=>{});
                image.decode?.().catch(()=>{});
              });
              frame.contentWindow.dispatchEvent(new Event('resize'));
            }catch(_){}};
            if(frame.dataset.urbanheatPresentationWarmBound!=='true'){
              frame.dataset.urbanheatPresentationWarmBound='true';
              frame.addEventListener('load',warm);
            }
            warm();
          };
          const warmAllContent=()=>{
            plan.forEach(item=>{
              const anchor=root.getElementById(item.anchor);
              const screen=anchor?.closest('[class*="st-key-screen_"]') || anchor?.parentElement;
              screen?.querySelectorAll('iframe').forEach(warmFrame);
              screen?.querySelectorAll('img').forEach(image=>{
                image.loading='eager';
                image.decode?.().catch(()=>{});
              });
            });
          };
          const isScrollable=(node)=>{
            const style=parentWindow.getComputedStyle(node);
            return /(auto|scroll)/.test(style.overflowY) && node.scrollHeight>node.clientHeight;
          };
          const showSlide=(item)=>{
            if(!item.deck_prefix || item.slide===null) return;
            for(let index=1;index<=item.deck_count;index++){
              root.querySelectorAll('.st-key-'+item.deck_prefix+'_'+index).forEach(node=>node.style.setProperty('display','none','important'));
            }
            const active=root.querySelector('.st-key-'+item.deck_prefix+'_'+(Number(item.slide)+1));
            if(active){
              active.style.setProperty('display','block','important');
              active.querySelectorAll('iframe').forEach(frame=>{
                try{frame.contentWindow.dispatchEvent(new Event('resize'))}catch(_){}
              });
            }
          };
          const updateTitle=(item)=>{
            const title=root.querySelector('.st-key-route_header .breadcrumb-title');
            if(title) title.innerHTML=item.title_html;
          };
          const settle=(item,index)=>{
            showSlide(item); updateTitle(item); state.index=index; state.busy=false;
            root.documentElement.dataset.urbanheatPresentationIndex=String(index);
            const url=new URL(parentWindow.location.href);
            url.hash='presentation='+encodeURIComponent(item.section+'|'+item.subsection+'|'+String(item.slide ?? 0));
            parentWindow.history.replaceState(null,'',url.toString());
          };
          const exitPresentation=()=>{
            if(state.exiting) return;
            state.exiting=true;
            root.documentElement.dataset.urbanheatReloadAfterPresentationExit='true';
            const button=root.querySelector('.st-key-presentation_exit_'+state.index+' button');
            if(button) button.click();
            else {
              delete root.documentElement.dataset.urbanheatReloadAfterPresentationExit;
              state.exiting=false;
            }
          };
          const handleEscape=(event)=>{
            if(event.key!=='Escape') return;
            event.preventDefault();
            event.stopImmediatePropagation();
            exitPresentation();
          };
          const bindEscapeSurface=(surface)=>{
            if(!surface) return;
            if(surface.__urbanheatPresentationEscapeCapture){
              surface.removeEventListener('keydown',surface.__urbanheatPresentationEscapeCapture,true);
            }
            surface.__urbanheatPresentationEscapeCapture=handleEscape;
            surface.addEventListener('keydown',handleEscape,true);
          };
          const advance=()=>{
            if(state.busy || state.index+1>=plan.length) return;
            state.busy=true;
            const nextIndex=state.index+1;
            const item=plan[nextIndex];
            state.index=nextIndex;
            root.documentElement.dataset.urbanheatPresentationIndex=String(nextIndex);
            const target=root.getElementById(item.anchor);
            showSlide(item);
            if(!target){settle(item,nextIndex);return;}
            let scroller=target.parentElement;
            while(scroller && !isScrollable(scroller)) scroller=scroller.parentElement;
            scroller=scroller || root.scrollingElement;
            const header=root.querySelector('.st-key-route_header');
            const isDocumentScroller=scroller===root.scrollingElement;
            const current=scroller.scrollTop;
            const containerTop=isDocumentScroller ? 0 : scroller.getBoundingClientRect().top;
            const headerBottom=header ? header.getBoundingClientRect().bottom : 74;
            const destination=current+target.getBoundingClientRect().top-containerTop-headerBottom;
            const distance=destination-current;
            if(Math.abs(distance)<2){settle(item,nextIndex);return;}
            const duration=440;
            const started=performance.now();
            const tick=(now)=>{
              const progress=Math.min((now-started)/duration,1);
              const eased=progress<.5 ? 4*progress*progress*progress : 1-Math.pow(-2*progress+2,3)/2;
              scroller.scrollTop=current+distance*eased;
              if(progress<1) requestAnimationFrame(tick);
              else settle(item,nextIndex);
            };
            requestAnimationFrame(tick);
          };
          const activate=()=>{
            if(root.__urbanheatPresentationClickCapture){
              root.removeEventListener('click',root.__urbanheatPresentationClickCapture,true);
            }
            root.__urbanheatPresentationClickCapture=(event)=>{
              if(root.documentElement.dataset.urbanheatPresentation!=='true') return;
              if(event.target.closest('.st-key-mode_toggle')){
                event.preventDefault();
                event.stopImmediatePropagation();
                exitPresentation();
                return;
              }
              const header=root.querySelector('.st-key-route_header');
              if(!header || !header.contains(event.target)) return;
              if(event.target.closest('button,input,label,select,a,iframe')) return;
              event.preventDefault();
              event.stopImmediatePropagation();
              advance();
            };
            root.addEventListener('click',root.__urbanheatPresentationClickCapture,true);
            bindEscapeSurface(root);
            bindEscapeSurface(parentWindow);
            const bindFrames=()=>root.querySelectorAll('iframe').forEach(frame=>{
              const bind=()=>{try{bindEscapeSurface(frame.contentDocument)}catch(_){}};
              if(frame.dataset.urbanheatPresentationEscapeBound!=='true'){
                frame.dataset.urbanheatPresentationEscapeBound='true';
                frame.addEventListener('load',bind);
              }
              bind();
            });
            bindFrames();
            if(root.__urbanheatPresentationFrameObserver) root.__urbanheatPresentationFrameObserver.disconnect();
            root.__urbanheatPresentationFrameObserver=new MutationObserver(bindFrames);
            root.__urbanheatPresentationFrameObserver.observe(root.body,{childList:true,subtree:true});
          };
          const initializeContent=()=>{
            if(!plan.length || !plan.every(item=>root.getElementById(item.anchor))) return;
            warmAllContent();
            const initializedDecks=new Set();
            plan.forEach(item=>{
              if(item.deck_prefix && !initializedDecks.has(item.deck_prefix)){
                initializedDecks.add(item.deck_prefix); showSlide(item);
              }
            });
            settle(plan[0],0);
            contentObserver.disconnect();
          };
          const contentObserver=new MutationObserver(initializeContent);
          contentObserver.observe(root.body,{childList:true,subtree:true});
          window.setTimeout(()=>{activate();initializeContent();},0);
        </script>
        """
        .replace("__PRESENTATION_PLAN__", json.dumps(presentation_payload, ensure_ascii=False)),
        height=0,
        width=0,
    )

slide_navigation = None
if current_section == "Dataset" and current_subsection == "Target LST":
    slide_navigation = ("st-key-target_lst_slide_deck", "st-key-target_lst_slide_", 2)
elif current_section == "Introducción" and current_subsection == "Scope":
    slide_navigation = ("st-key-scope_motivation_slide_deck", "st-key-scope_motivation_slide_", 2)
elif current_section == "Dataset" and current_subsection == "Predictores / Topomorfológicas":
    slide_navigation = ("st-key-topomorfologicas_slide_deck", "st-key-topomorfologicas_slide_", 2)
elif current_section == "Dataset" and current_subsection == "Predictores / Land cover":
    slide_navigation = ("st-key-land_cover_slide_deck", "st-key-land_cover_slide_", 2)
elif current_section == "Modelización" and current_subsection == "Metodología":
    slide_navigation = ("st-key-modelizacion_metodologia_slide_deck", "st-key-modelizacion_metodologia_slide_", 2)
elif current_section == "Modelización" and current_subsection == "Resultados / Visualización":
    slide_navigation = ("st-key-modelizacion_visualizacion_slide_deck", "st-key-modelizacion_visualizacion_slide_", 3)
if current_section == "Dataset" and current_subsection == "Predictores / Meteo":
    with st.container(key="slide_navigation"):
        render_slide_navigation("st-key-meteo_slide_deck", "st-key-meteo_slide_", 3)
    with st.container(key="meteo_slide_trigger"):
        current_slide = int(st.session_state.get("meteo_slide_index", 0)) % 3
        if st.button("Siguiente slide", key="meteo_slide_trigger_button"):
            st.session_state.meteo_slide_index = (current_slide + 1) % 3
            st.rerun()
    components.html(
        """
        <script>
          const root=window.parent.document;
          const bind=()=>root.querySelectorAll('.st-key-slide_navigation iframe').forEach((frame)=>{
            if(frame.dataset.meteoSlideBound==='true')return;
            frame.dataset.meteoSlideBound='true';
            const attach=()=>{try{
              const next=frame.contentDocument.getElementById('next-slide');
              if(next && next.dataset.meteoSlideBound!=='true'){
                next.dataset.meteoSlideBound='true';
                next.addEventListener('click',()=>root.querySelector('.st-key-meteo_slide_trigger_button button')?.click());
              }
            }catch(_){}};
            frame.addEventListener('load',attach);attach();
          });
          bind();new MutationObserver(bind).observe(root.body,{childList:true,subtree:true});
        </script>
        """,
        height=0,
        width=0,
    )
elif current_section == "Dataset" and current_subsection == "Predictores / Distancias":
    with st.container(key="slide_navigation"):
        render_slide_navigation(
            "st-key-distancias_slide_deck",
            "st-key-distancias_slide_",
            2,
        )
    with st.container(key="distancias_slide_trigger"):
        current_slide = int(st.session_state.get("distancias_slide_index", 0)) % 2
        if st.button("Siguiente slide", key="distancias_slide_trigger_button"):
            st.session_state.distancias_slide_index = (current_slide + 1) % 2
            st.rerun()
    components.html(
        """
        <script>
          const root=window.parent.document;
          const bind=()=>root.querySelectorAll('.st-key-slide_navigation iframe').forEach((frame)=>{
            if(frame.dataset.distanceSlideBound==='true')return;
            frame.dataset.distanceSlideBound='true';
            const attach=()=>{
              try{
                const next=frame.contentDocument.getElementById('next-slide');
                if(next && next.dataset.distanceSlideBound!=='true'){
                  next.dataset.distanceSlideBound='true';
                  next.addEventListener('click',()=>root.querySelector('.st-key-distancias_slide_trigger_button button')?.click());
                }
              }catch(_){}
            };
            frame.addEventListener('load',attach); attach();
          });
          bind(); new MutationObserver(bind).observe(root.body,{childList:true,subtree:true});
        </script>
        """,
        height=0,
        width=0,
    )
elif not st.session_state.presentation_mode and slide_navigation:
    with st.container(key="slide_navigation"):
        render_slide_navigation(
            *slide_navigation,
            initial_index=int(st.session_state.get("normal_initial_slide", 0)),
        )

# En presentación, las slides de decks estáticos se seleccionan desde el guion
# de servidor, sin crear flechas ni depender de eventos del iframe.
if st.session_state.presentation_mode and current_route in PRESENTATION_DECKS:
    prefix, count = PRESENTATION_DECKS[current_route]
    active_slide = int(st.session_state.get("presentation_slide_index", 0) or 0) + 1
    hide_rules = ", ".join(f".st-key-{prefix}_{index}" for index in range(1, count + 1))
    st.markdown(
        f"<style>{hide_rules}{{display:none!important}}.st-key-{prefix}_{active_slide}{{display:block!important}}</style>",
        unsafe_allow_html=True,
    )

if st.session_state.presentation_mode:
    presentation_routes: dict[str, set[str]] = {}
    for _, plan_section, plan_subsection, _ in _presentation_plan():
        presentation_routes.setdefault(plan_section, set()).add(plan_subsection)
    for plan_section in sections:
        selected_subsections = presentation_routes.get(plan_section)
        if selected_subsections:
            render_parent_page(
                plan_section,
                current_subsection if plan_section == current_section else "",
                st.session_state.loaded_subsections,
                selected_subsections,
            )
else:
    render_parent_page(current_section, current_subsection, st.session_state.loaded_subsections)

# Los contenidos viven en bloques de Streamlit. El arrastre tiene que ocurrir
# aquí (en el documento padre), no dentro de los iframes de imagen/mapa: de ese
# modo todos comparten exactamente la misma línea azul de alineación.
components.html(
    """
    <script>
      const root = window.parent.document;
      const parentWindow = window.parent;
      const storage = parentWindow.localStorage;
      root.getElementById('urbanheat-sentinel-route-guard')?.remove();
      const keyOf = (node) => {
        const match = Array.from(node.classList || []).find((name) => name.indexOf('st-key-movable_') !== -1);
        return match ? match.replace('st-key-', '') : null;
      };
      const guideLeft = () => {
        const guide = root.getElementById('urbanheat-left-guide');
        return guide ? guide.getBoundingClientRect().left + 4 : 120;
      };
      const attach = (node) => {
        const contentKey = keyOf(node);
        if (!contentKey) return;
        const host = node.closest('.element-container') || node;
        const existingHandle = Array.from(host.children).find(
          (child) => child.classList?.contains('urbanheat-content-move-handle')
        );
        if (existingHandle) return;
        node.dataset.urbanheatMovable = 'true';
        host.dataset.urbanheatMovableHost = contentKey;
        host.style.position = 'relative';
        host.style.overflow = 'visible';
        const layoutVersion = contentKey === 'movable_meteo_slides' ? 'v3' : 'v2';
        const layoutKey = 'urbanheat-movable-' + layoutVersion + '-' + contentKey;
        let saved = null;
        try { saved = JSON.parse(storage.getItem(layoutKey)); } catch (_) {}
        const state = { x: saved && Number.isFinite(saved.x) ? saved.x : 0, y: saved && Number.isFinite(saved.y) ? saved.y : 0 };
        const apply = () => {
          const baseTransform = `translate(${state.x}px, ${state.y}px)`;
          host.style.transform = baseTransform;
        };
        const constrain = () => {
          const rect = host.getBoundingClientRect();
          const minDelta = guideLeft() - rect.left;
          if (minDelta > 0) state.x += minDelta;
        };
        apply();
        constrain();
        apply();
        const handle = root.createElement('button');
        handle.type = 'button';
        handle.className = 'urbanheat-content-move-handle';
        handle.setAttribute('aria-label', 'Mover contenedor');
        handle.innerHTML = '✥';
        host.appendChild(handle);
        const persist = () => storage.setItem(layoutKey, JSON.stringify(state));
        handle.addEventListener('pointerdown', (event) => {
            event.preventDefault();
            event.stopPropagation();
            handle.setPointerCapture?.(event.pointerId);
            const startX = event.clientX;
            const startY = event.clientY;
            const initialX = state.x;
            const initialY = state.y;
            const move = (next) => {
              next.preventDefault();
              const before = host.getBoundingClientRect();
              const requestedX = initialX + next.clientX - startX;
              const requestedY = initialY + next.clientY - startY;
              const lowerBound = initialX + guideLeft() - before.left;
              state.x = Math.max(lowerBound, requestedX);
              state.y = requestedY;
              apply();
            };
            const finish = () => {
              parentWindow.removeEventListener('pointermove', move, true);
              parentWindow.removeEventListener('pointerup', finish, true);
              persist();
            };
            parentWindow.addEventListener('pointermove', move, true);
            parentWindow.addEventListener('pointerup', finish, true);
          });
      };
      const bindMovables = () => root.querySelectorAll('[class*="st-key-movable_"]').forEach(attach);
      bindMovables();
      if (parentWindow.__urbanheatMovableObserver) parentWindow.__urbanheatMovableObserver.disconnect();
      parentWindow.__urbanheatMovableObserver = new MutationObserver(bindMovables);
      parentWindow.__urbanheatMovableObserver.observe(root.body, { childList: true, subtree: true });
    </script>
    """,
    height=0,
    width=0,
)

# Edición muestra las guías y controles; Renderizado deja únicamente el
# contenido persistido. Las posiciones no se modifican al cambiar de modo.
mode_value = "render" if st.session_state.presentation_mode else ("edit" if st.session_state.edit_mode else "render")
force_reload_after_exit = bool(
    not st.session_state.presentation_mode
    and st.session_state.pop("reload_after_presentation_exit", False)
)
components.html(
    """
    <script>
      const root = window.parent.document;
      const mode = '__URBANHEAT_MODE__';
      root.documentElement.dataset.urbanheatMode = mode;
      const presentation = __URBANHEAT_PRESENTATION__;
      const forceReloadAfterExit = __URBANHEAT_FORCE_RELOAD__;
      root.documentElement.dataset.urbanheatPresentation = String(presentation);
      if (!presentation) {
        if (forceReloadAfterExit || root.documentElement.dataset.urbanheatReloadAfterPresentationExit === 'true') {
          delete root.documentElement.dataset.urbanheatReloadAfterPresentationExit;
          window.setTimeout(() => window.parent.location.reload(), 0);
        }
        if (root.__urbanheatPresentationClickCapture) {
          root.removeEventListener('click', root.__urbanheatPresentationClickCapture, true);
          delete root.__urbanheatPresentationClickCapture;
        }
        if (root.__urbanheatPresentationEscapeCapture) {
          root.removeEventListener('keydown', root.__urbanheatPresentationEscapeCapture, true);
          delete root.__urbanheatPresentationEscapeCapture;
        }
        if (window.parent.__urbanheatPresentationEscapeCapture) {
          window.parent.removeEventListener('keydown', window.parent.__urbanheatPresentationEscapeCapture, true);
          delete window.parent.__urbanheatPresentationEscapeCapture;
        }
        if (root.__urbanheatPresentationFrameObserver) {
          root.__urbanheatPresentationFrameObserver.disconnect();
          delete root.__urbanheatPresentationFrameObserver;
        }
        delete root.documentElement.dataset.urbanheatPresentationIndex;
      }
      const presentationStyleId = 'urbanheat-presentation-mode-style';
      let presentationStyle = root.getElementById(presentationStyleId);
      if (!presentationStyle) { presentationStyle = root.createElement('style'); presentationStyle.id = presentationStyleId; root.head.appendChild(presentationStyle); }
      presentationStyle.textContent = presentation
        ? 'html[data-urbanheat-presentation="true"] [data-testid="stSidebar"],html[data-urbanheat-presentation="true"] .st-key-sidebar_reopen,html[data-urbanheat-presentation="true"] .st-key-layout_left_guide,html[data-urbanheat-presentation="true"] .st-key-mode_toggle,html[data-urbanheat-presentation="true"] .st-key-slide_navigation,html[data-urbanheat-presentation="true"] [class*="st-key-presentation_exit_"]{display:none!important} html[data-urbanheat-presentation="true"] [data-testid="stMain"]{margin-left:0!important;width:100%!important;max-width:none!important}'
        : '';
      const styleId = 'urbanheat-render-mode-style';
      const css = 'html[data-urbanheat-mode="render"] #urbanheat-left-guide, html[data-urbanheat-mode="render"] .urbanheat-content-move-handle { display:none !important; }';
      let rootStyle = root.getElementById(styleId);
      if (!rootStyle) { rootStyle = root.createElement('style'); rootStyle.id = styleId; root.head.appendChild(rootStyle); }
      rootStyle.textContent = css;
      const frameCss = `
        body.urbanheat-render-mode .toolbar,
        body.urbanheat-render-mode .move-handle,
        body.urbanheat-render-mode .resize-handle,
        body.urbanheat-render-mode .urbanheat-resize-handle,
        body.urbanheat-render-mode .urbanheat-map-drag-handle,
        body.urbanheat-render-mode .editor-image-handle,
        body.urbanheat-render-mode .editor-image-resize,
        body.urbanheat-render-mode .editor-text-handle,
        body.urbanheat-render-mode .object-handle,
        body.urbanheat-render-mode .object-resize,
        body.urbanheat-render-mode .sentinel-resize { display:none !important; }
        body.urbanheat-render-mode .shell { position:relative !important; left:0 !important; top:0 !important; width:100% !important; border:0 !important; resize:none !important; overflow:visible !important; height:auto !important; min-height:0 !important; display:block !important; }
        body.urbanheat-render-mode .editor-stage { position:relative !important; min-height:0 !important; height:auto !important; overflow:visible !important; }
        body.urbanheat-render-mode .shell .canvas,
        body.urbanheat-render-mode .shell.source-mode .canvas { display:block !important; flex:none !important; height:auto !important; min-height:0 !important; overflow:visible !important; }
        body.urbanheat-render-mode .object-editor .canvas { display:block !important; width:100% !important; height:1400px !important; min-height:1400px !important; overflow:hidden !important; }
        body.urbanheat-render-mode .html-source { display:none !important; }
      `;
      const applyFrame = (frame) => {
        try {
          const doc = frame.contentDocument;
          if (!doc) return;
          doc.body.classList.toggle('urbanheat-render-mode', mode === 'render');
          let style = doc.getElementById('urbanheat-frame-mode-style');
          if (!style) { style = doc.createElement('style'); style.id = 'urbanheat-frame-mode-style'; doc.head.appendChild(style); }
          style.textContent = frameCss;
        } catch (_) {}
      };
      const syncFrames = () => root.querySelectorAll('iframe').forEach((frame) => {
        applyFrame(frame);
        if (frame.dataset.urbanheatModeBound !== 'true') {
          frame.dataset.urbanheatModeBound = 'true';
          frame.addEventListener('load', () => applyFrame(frame), {once:false});
        }
      });
      syncFrames();
      new MutationObserver(syncFrames).observe(root.body, {childList:true, subtree:true});
    </script>
    """
    .replace("__URBANHEAT_MODE__", mode_value)
    .replace("__URBANHEAT_PRESENTATION__", str(st.session_state.presentation_mode).lower())
    .replace("__URBANHEAT_FORCE_RELOAD__", str(force_reload_after_exit).lower()),
    height=0,
    width=0,
)

if st.session_state.scroll_target:
    target = st.session_state.scroll_target
    st.session_state.scroll_target = None
    scroll_to(target)
