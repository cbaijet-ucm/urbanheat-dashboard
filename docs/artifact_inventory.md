# Inventario de artefactos — primera iteración

Auditoría realizada sobre los notebooks `01`–`14`, el catálogo de escenas, el dataset tabular y las carpetas `05_Models` y `06_Results`. No se han modificado artefactos externos.

| Sección del dashboard | Contenido | Artefacto fuente | Transformación necesaria |
| --- | --- | --- | --- |
| Inicio | Alcance, unidad de análisis y advertencia LST | `02_Code/config.yaml`, prompt rector y notebooks de preparación | Texto trazable; sin cifra inventada |
| Datos | Límite municipal y buffer | `processed/boundaries/*epsg4326.geojson` | Copia ligera para Plotly |
| Datos | Distribución de escenas y nubosidad | `metadata/scene_catalog.csv` | Copia CSV compacta |
| Datos | Familias, rango y nulos de variables | `processed/cell_date_dataset/dataset_summary.csv` | Eliminar columna `mode` para evitar una lista masiva |
| Modelo tabular (fase posterior) | Especificación y test | `05_Models/tabular_two_stage/model_manifest.json`, `06_Results/metrics/tabular_two_stage/*.csv` | Copias de métricas y manifiesto |
| Deep Learning (fase posterior) | Histórico de ejecuciones | `06_Results/metrics/cnn_runs/cnn_runs_summary.csv` | Copia; seleccionar runs consolidados después |
| Capa social (fase posterior) | Agregaciones por barrio/sección | `notebook 14` y geometrías administrativas | Falta seleccionar y derivar indicadores finales |
| What-if NDVI (fase posterior) | Inferencia por barrio | modelo XGBoost, modelo temporal y subconjunto `cell_id`–barrio con todas las features | Pendiente: contrato compacto y validación de inferencia |

## Hallazgos verificados

- El dataset tabular contiene 37 escenas y ocupa 382,996,804 bytes; no se migrará ni cargará desde la aplicación.
- El target es `LST_Celsius`. El resumen del dataset registra valores entre 14.983922 y 60.61449 °C, pero estos límites no se usan para afirmar una escala de un mapa no derivado.
- El modelo tabular final registrado es `regularized_scene_mean_plus_centered_xgboost_spatial`: Elastic Net temporal (especificación `completo`) y XGBoost espacial.
- El manifiesto registra siete escenas de test, con corte temporal `2025-08-15`; las métricas macro existen y se reservarán para la página de modelo en la siguiente fase.
- Existen experimentos CNN y U-Net. Esta iteración no declara ninguno como ganador: la selección requiere consolidar qué evaluación final es comparable.

## Activos deliberadamente excluidos

- `cell_date_dataset.parquet` completo (≈383 MB).
- GeoTIFFs, mosaicos y rasters Landsat/Sentinel originales.
- Modelos serializados y tensores de Deep Learning.
- Cualquier predicción de celdas completa hasta que se genere una derivación de presentación justificada.
