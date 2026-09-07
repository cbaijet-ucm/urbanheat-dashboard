# Registro de dependencias externas

El registro legible por máquina es `data/external_artifacts.json`. Las rutas son relativas a la raíz del repositorio; nunca se incorporan rutas absolutas locales.

| Archivo de origen | Tipo | Tamaño aproximado | Uso | ¿Imprescindible? | Copia derivada | Método de migración |
| --- | --- | ---: | --- | --- | --- | --- |
| `00_Datasets/metadata/scene_catalog.csv` | CSV | pequeño | Cronología de escenas | Sí | `assets/summaries/scene_catalog.csv` | Copia |
| `00_Datasets/processed/cell_date_dataset/dataset_summary.csv` | CSV | 1.5 MB | Contrato y rangos de variables | Sí | `assets/summaries/feature_summary.csv` | Eliminar `mode` |
| `.../boundaries/bcn_epsg4326.geojson` | GeoJSON | 240 KB | Contorno municipal | Sí | `assets/maps/bcn_epsg4326.geojson` | Copia |
| `.../boundaries/bcn_1km_epsg4326.geojson` | GeoJSON | 40 KB | Buffer | Sí | `assets/maps/bcn_1km_epsg4326.geojson` | Copia |
| `.../boundaries/barris_epsg4326.geojson` | GeoJSON | 1.3 MB | Selección territorial futura | No | `assets/maps/barris_epsg4326.geojson` | Copia |
| `05_Models/tabular_two_stage/model_manifest.json` | JSON | pequeño | Trazabilidad del modelo | No | `assets/summaries/tabular_model_manifest.json` | Copia |
| `06_Results/metrics/tabular_two_stage/*.csv` | CSV | pequeño | Métricas futuras | No | `assets/summaries/tabular_*` | Copia |
| `06_Results/metrics/cnn_runs/cnn_runs_summary.csv` | CSV | pequeño | Auditoría DL futura | No | `assets/summaries/cnn_runs_summary.csv` | Copia |

No se registran los modelos ni el Parquet de 383 MB como dependencias de ejecución porque esta iteración no ejecuta inferencia.
