# Migración de artefactos

Desde la raíz del repositorio:

```bash
python 07_Dashboard/scripts/migrate_dashboard_assets.py
```

El script lee `data/external_artifacts.json`, comprueba la existencia de cada origen imprescindible, copia únicamente los activos activos de esta iteración y crea `assets/manifest.json` con tamaño, transformación, hash SHA-256 y CRS cuando aplica. Las dependencias opcionales quedan registradas para fases posteriores, pero no se copian todavía. Devuelve código distinto de cero si falta un archivo imprescindible.

Después de migrar, ejecute:

```bash
streamlit run 07_Dashboard/app.py
```

La aplicación sólo lee `07_Dashboard/assets` en tiempo de ejecución. Para una migración limpia, copie el directorio del dashboard junto con los orígenes declarados a la misma estructura relativa, ejecute el comando anterior y confirme que `assets/manifest.json` no contiene faltantes imprescindibles.
