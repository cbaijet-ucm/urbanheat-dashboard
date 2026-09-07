# UrbanHeat BCN — dashboard narrativo

Dashboard Streamlit del TFM, organizado como una navegación jerárquica con modos de edición, renderizado y presentación.

## Ejecución

Desde PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File C:\Urbanheat\07_Dashboard\restart_dashboard.ps1
```

El script elimina primero cualquier instancia que escuche en los puertos `8501` y `8766`, y después levanta una única aplicación en `http://localhost:8501` usando el entorno `.urbanheat`.

## Estructura viva

- `app.py`: navegación y modos globales.
- `components/`: estructura visual y renderizadores activos.
- `data/`: persistencia y registro de artefactos.
- `.urbanheat_content/`: estado canónico de los lienzos editables; no debe borrarse.
- `assets/`: activos fuente y derivados del dashboard.
- `static/`: recursos optimizados servidos en tiempo de ejecución.
- `scripts/`: construcción reproducible de activos.
- `presentation_order.md`: orden declarativo del modo Presentación.
