# Evaluación del escenario exploratorio NDVI

## Estado: bloqueado para esta iteración

El modelo tabular final sí incluye `NDVI` entre sus variables espaciales y existe un modelo XGBoost serializado. Sin embargo, el dashboard no debe cargar el Parquet completo de `cell_id + scene_id` (≈383 MB) para localizar celdas, recuperar las 27 features espaciales y reconstruir el componente temporal de una escena.

No se ha creado una aproximación ni se han inventado predicciones.

## Artefactos necesarios para activarlo con seguridad

1. Una tabla derivada y versionada para **una escena declarada**, con `cell_id`, `barri_name`, `NDVI` y todas las variables de `spatial_features` del manifiesto; debe contener sólo las celdas válidas necesarias y sus rangos.
2. Un resumen temporal por escena con todas las variables de `temporal_features`, y un identificador de la escena seleccionada o fijada.
3. Copias versionadas de `temporal_final.joblib` y `xgboost_spatial.ubj`, con hashes y una prueba reproducible de inferencia contra una predicción de referencia.
4. Una definición explícita del límite de NDVI usada en el escenario (el resumen actual registra mínimo −0.98889554 y máximo 1.0) y una prueba de saturación.
5. Una derivación territorial `cell_id`–`barri_name` que permita filtrar por barrio sin reconstruir geometrías de cientos de miles de celdas.

Cuando esos artefactos se generen, el control se limitará a: barrio, incremento NDVI de 20 %, comparación de predicción original/escenario/diferencia y advertencia no causal. El resto de variables permanecerá constante.
