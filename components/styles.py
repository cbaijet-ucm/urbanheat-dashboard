"""Único punto de CSS adicional; el tema base vive en .streamlit/config.toml."""

import streamlit as st


def apply_global_styles() -> None:
    st.markdown("""
    <style>
    html {scroll-behavior: smooth;}
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] > .main,
    [data-testid="stHeader"], [data-testid="stToolbar"] {background: #ffffff !important; color: #161616 !important;}
    [data-testid="stHeader"] {height: 0 !important; min-height: 0 !important; overflow: visible !important;}
    [data-testid="stToolbar"], [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stSidebar"] {display: block !important; background: #ffffff !important; border-right: 1px solid #d8d8d8 !important;}
    [data-testid="stSidebar"][aria-expanded="true"], [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {min-width: 256px !important; width: 256px !important;}
    [data-testid="stSidebar"][aria-expanded="false"], [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {min-width: 0 !important; width: 0 !important; border: 0 !important; overflow: hidden !important;}
    .st-key-sidebar_reopen {display: none;}
    .st-key-layout_left_guide,
    .element-container:has(.st-key-layout_left_guide),
    .element-container:has(.st-key-route_header) {
      height: 0 !important; min-height: 0 !important; margin: 0 !important; padding: 0 !important; overflow: visible !important;
    }
    .st-key-layout_left_guide iframe {height: 0 !important; width: 0 !important; border: 0 !important;}
    body:has([data-testid="stSidebar"][aria-expanded="false"]) .st-key-sidebar_reopen {
      display: block !important; position: fixed !important; top: .5rem !important; left: .55rem !important;
      z-index: 3000 !important; width: 32px !important; height: 32px !important; margin: 0 !important;
    }
    .st-key-sidebar_reopen iframe {width: 32px !important; height: 32px !important; border: 0 !important;}
    [data-testid="stSidebar"][aria-expanded="true"] [data-testid="stSidebarContent"] {padding: 1.5rem 1rem !important; background: #ffffff !important;}
    body:has([data-testid="stSidebar"][aria-expanded="false"]) .st-key-route_header {left: 0 !important; padding-left: 120px !important;}
    body:has([data-testid="stSidebar"][aria-expanded="false"]) .block-container {padding-left: 120px !important;}
    [data-testid="stSidebar"] * {color: #252525 !important;}
    [data-testid="stSidebarNav"] {display: none !important;}
    .block-container {max-width: none; width: 100%; padding: 3.05rem clamp(2rem, 5vw, 6rem) 5rem !important; padding-left: 120px !important;}
    h1, h2, h3 {color: #161616 !important; letter-spacing: -0.03em; font-weight: 500;}
    h1 {font-size: clamp(2.5rem, 4vw, 4.25rem); line-height: 1; margin: .3rem 0 1.2rem !important;}
    .breadcrumb-title {margin: 0 !important; font-size: clamp(1.75rem, 2.65vw, 2.85rem) !important;}
    .breadcrumb-title span {color: #8d8d8d !important; font-weight: 300;}
    .breadcrumb-title .breadcrumb-active {color: rgb(0, 0, 255) !important;}
    .st-key-route_header {position: fixed !important; top: 0 !important; left: 256px !important; right: 0 !important; width: auto !important; z-index: 1000 !important; box-sizing: border-box !important; background: #ffffff !important; padding: .55rem clamp(1.5rem, 2.5vw, 3rem) .6rem !important; padding-left: 120px !important; border-bottom: 1px solid #e4e4e4; margin: 0 !important;}
    .element-container:has(.st-key-route_header) {position: static !important;}
    .st-key-mode_toggle {display: flex !important; align-items: center !important; justify-content: flex-end !important; margin: 0 !important; padding: 0 !important;}
    .st-key-mode_toggle [data-testid="stToggle"] {margin: 0 !important; padding: 0 !important; display: flex !important; justify-content: flex-end !important;}
    .st-key-mode_toggle [data-testid="stToggle"] label {display: inline-flex !important; align-items: center !important; gap: .42rem !important; white-space: nowrap !important; cursor: pointer !important;}
    .st-key-mode_toggle [data-testid="stToggle"] label p {font-size: .78rem !important; line-height: 1 !important; margin: 0 !important; color: #3f3f3f !important;}
    p, li, label, [data-testid="stMarkdownContainer"] {color: #161616 !important; font-size: 1rem; line-height: 1.55;}
    [data-testid="stSidebar"] img {width: 100% !important; max-width: 100% !important; height: auto !important; margin: 0 0 1.35rem !important;}
    [data-testid="stSidebar"] [data-testid="stExpander"] {border: 0 !important; border-bottom: 1px solid #ededed !important; border-radius: 0 !important; background: #ffffff !important; margin: 0 !important;}
    [data-testid="stSidebar"] [data-testid="stExpander"] details {border: 0 !important; background: #ffffff !important;}
    [data-testid="stSidebar"] [data-testid="stExpander"] summary {padding: .65rem 0 !important; background: #ffffff !important; font-size: .9rem !important; font-weight: 500 !important;}
    [data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {background: #ffffff !important; color: #161616 !important;}
    [data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stExpanderDetails"] {padding: 0 0 .4rem .85rem !important; background: #ffffff !important;}
    [data-testid="stSidebar"] [class*="st-key-nav_nested_"] {padding-left: .8rem !important;}
    [data-testid="stSidebar"] .stButton {margin: 0 !important;}
    [data-testid="stSidebar"] .stButton > button {min-height: 0 !important; padding: .28rem 0 !important; border: 0 !important; border-radius: 0 !important; background: transparent !important; box-shadow: none !important; color: #4d4d4d !important; font-size: .82rem !important; font-weight: 400 !important; justify-content: flex-start !important; text-align: left !important;}
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] .stButton > button {justify-content: flex-start !important; text-align: left !important;}
    [data-testid="stSidebar"] [data-testid="stExpanderDetails"] .stButton > button > div,
    [data-testid="stSidebar"] [data-testid="stExpanderDetails"] .stButton > button span,
    [data-testid="stSidebar"] [data-testid="stExpanderDetails"] .stButton > button p {
      width: 100% !important; justify-content: flex-start !important; text-align: left !important;
    }
    [data-testid="stSidebar"] [class*="st-key-nav_active_"] .stButton > button,
    [data-testid="stSidebar"] [class*="st-key-nav_active_"] .stButton > button *,
    [data-testid="stSidebar"] [class*="st-key-nav_nested_active_"] .stButton > button,
    [data-testid="stSidebar"] [class*="st-key-nav_nested_active_"] .stButton > button * {
      color: rgb(0, 0, 255) !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {background: transparent !important; color: #161616 !important; text-decoration: underline;}
    [data-testid="stHorizontalBlock"] .stButton > button {min-width: 0 !important; padding: .16rem .18rem !important; border: 0 !important; border-radius: 0 !important; background: transparent !important; box-shadow: none !important; color: #525252 !important; font-size: 1.12rem !important; font-weight: 300 !important;}
    .st-key-route_header [data-testid="stHorizontalBlock"] .stButton > button {font-size: 1.32rem !important;}
    [data-testid="stHorizontalBlock"] .stButton > button:hover {background: transparent !important; color: #161616 !important;}
    [data-testid="stHorizontalBlock"] .stButton > button:disabled {color: #c6c6c6 !important;}
    .eyebrow {font-size: .73rem !important; letter-spacing: .09em; text-transform: uppercase; color: #6f6f6f !important;}
    .lede {font-size: 1.25rem !important; max-width: 44rem; line-height: 1.45; margin-bottom: 1rem;}
    .wire-copy {max-width: 42rem; color: #5f5f5f !important; margin-bottom: 2.8rem;}
    .placeholder {width: 100%; border: 1px solid #c6c6c6; background: #fafafa; color: #5f5f5f !important; margin: 1.1rem 0; display: flex; flex-direction: column; justify-content: center; align-items: center; text-transform: uppercase; letter-spacing: .08em; font-size: .78rem;}
    .placeholder span, .placeholder small {color: #5f5f5f !important;}
    .placeholder small {margin-top: .35rem; font-size: .65rem; letter-spacing: .12em;}
    .placeholder-hero {height: 390px;}
    .placeholder-map {height: 410px;}
    .placeholder-chart {height: 270px;}
    .placeholder-table {height: 230px;}
    .placeholder-wide {height: 260px;}
    .subsection-anchor {scroll-margin-top: 6rem; height: 1px;}
    [class*="st-key-screen_"], .element-container:has([class*="st-key-screen_"]) {min-height: 115vh !important; padding: 0;}
    .element-container:has([class*="st-key-screen_"]) {margin-top: 0 !important;}
    .element-container:has(.st-key-screen_route_introduccion_portada) {margin-top: 0;}
    .subsection-block {border-top: 1px solid #d8d8d8; padding-top: 1.25rem; margin-top: 0;}
    .subsection-block h2, .deferred-block h2 {font-size: clamp(1.7rem, 2.2vw, 2.35rem) !important; margin: 0 0 1rem !important; border: 0 !important; padding: 0 !important;}
    .subsection-active {border-top-color: #161616;}
    .deferred-block {min-height: 150px; border-top: 1px solid #e0e0e0; padding-top: 1.25rem; margin-top: 0;}
    .deferred-block h2 {color: #767676 !important;}
    .deferred-rule {height: 1px; width: 24%; background: #ededed;}
    .explicit-screen-gap {height: 450vh !important; width: 100%; pointer-events: none;}
    .st-key-scope_motivation_slide_deck {position: relative !important; overflow: visible !important;}
    .st-key-scope_motivation_slide_2 {display: none;}
    .st-key-target_lst_slide_deck {position: relative !important; overflow: visible !important;}
    .st-key-target_lst_slide_2 {display: none;}
    .st-key-topomorfologicas_slide_deck {position: relative !important; overflow: visible !important;}
    .st-key-topomorfologicas_slide_2 {display: none;}
    .st-key-land_cover_slide_deck {position: relative !important; overflow: visible !important;}
    .st-key-land_cover_slide_2 {display: none;}
    .st-key-modelizacion_metodologia_slide_deck {position: relative !important; overflow: visible !important;}
    .st-key-modelizacion_metodologia_slide_2, .st-key-modelizacion_metodologia_slide_3 {display: none;}
    .st-key-modelizacion_resultados_metricas_slide_deck {position: relative !important; overflow: visible !important;}
    .st-key-modelizacion_resultados_metricas_slide_2 {display: none;}
    .st-key-modelizacion_visualizacion_slide_deck {position: relative !important; overflow: visible !important;}
    .st-key-modelizacion_visualizacion_slide_2, .st-key-modelizacion_visualizacion_slide_3 {display: none;}
    .st-key-conclusiones_slide_deck {position: relative !important; overflow: visible !important;}
    .st-key-conclusiones_slide_2 {display: none;}
    .st-key-slide_navigation {
      position: fixed !important; top: 5.4rem; right: 1.35rem !important;
      z-index: 2700 !important; width: 58px !important; height: 58px !important; margin: 0 !important; padding: 0 !important;
    }
    .st-key-slide_navigation iframe {width: 58px !important; height: 58px !important; border: 0 !important;}
    .st-key-distancias_slide_trigger,
    .element-container:has(.st-key-distancias_slide_trigger),
    .st-key-meteo_slide_trigger,
    .element-container:has(.st-key-meteo_slide_trigger),
    .st-key-sociodemografico_vulnerabilidad_slide_trigger,
    .element-container:has(.st-key-sociodemografico_vulnerabilidad_slide_trigger) {display: none !important;}
    [data-urbanheat-movable-host] {will-change: transform;}
    .urbanheat-content-move-handle {
      position: absolute !important; top: 4px !important; left: 4px !important; z-index: 2600 !important;
      width: 20px !important; height: 20px !important; min-height: 20px !important; padding: 0 !important;
      display: inline-flex !important; align-items: center !important; justify-content: center !important;
      border: 1px solid #bdbdbd !important; border-radius: 0 !important; background: rgba(255,255,255,.92) !important;
      color: #4b4b4b !important; box-shadow: none !important; cursor: move !important; font-size: 13px !important;
      line-height: 1 !important; touch-action: none !important;
    }
    .urbanheat-content-move-handle:hover {border-color: rgb(0,0,255) !important; color: rgb(0,0,255) !important;}
    ::-webkit-scrollbar {width: 7px;}
    ::-webkit-scrollbar-track {background: #ffffff;}
    ::-webkit-scrollbar-thumb {background: #bdbdbd;}
    ::-webkit-scrollbar-thumb:hover {background: #777777;}
    </style>
    """, unsafe_allow_html=True)
