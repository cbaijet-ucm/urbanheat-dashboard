"""Prepara activos pequeños y autocontenidos para el prototipo de contenidos.

No se ejecuta en tiempo de consulta del dashboard: el parquet de 7 M de filas se
reduce aquí a una muestra determinista y los puntos sociales se proyectan una vez.
"""

from __future__ import annotations

import base64
import csv
import json
import math
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from pyproj import Transformer


ROOT = Path(__file__).resolve().parents[3]
DASHBOARD = ROOT / "02_Code" / "dashboard"
ASSETS = DASHBOARD / "assets"


def extract_scene_figure() -> None:
    """Extrae la comparación Reference/Core ya producida en el notebook 04."""
    notebook = json.loads((ROOT / "02_Code/notebooks/04_landsat_lst_processing.ipynb").read_text(encoding="utf-8"))
    output_path = ASSETS / "graphic" / "lst_reference_vs_core.png"
    for cell in notebook["cells"]:
        source = "".join(cell.get("source", []))
        if "def load_scene_map(row)" not in source:
            continue
        for output in cell.get("outputs", []):
            image = output.get("data", {}).get("image/png")
            if image:
                output_path.write_bytes(base64.b64decode(image))
                return
    raise RuntimeError("No se encontró la figura Reference/Core en el notebook 04.")


def build_cell_date_sample(rows: int = 12_000) -> None:
    source = ROOT / "00_Datasets/processed/cell_date_dataset/cell_date_dataset.parquet"
    output = ASSETS / "summaries" / "cell_date_sample.parquet"
    parquet = pq.ParquetFile(source)
    row_groups = parquet.num_row_groups
    per_group = math.ceil(rows / min(24, row_groups))
    count = min(24, row_groups)
    selected = [0] if count == 1 else sorted({round(index * (row_groups - 1) / (count - 1)) for index in range(count)})
    chunks = []
    for index in selected:
        table = parquet.read_row_group(index)
        start = max(0, (table.num_rows - per_group) // 2)
        chunks.append(table.slice(start, per_group))
    sample = pa.concat_tables(chunks).slice(0, rows)
    pq.write_table(sample, output, compression="zstd")


def build_social_map_assets() -> None:
    parks = ROOT / "00_Datasets/raw/opendata_bcn/parques/parcs.csv"
    shelters = ROOT / "00_Datasets/raw/opendata_bcn/refugios_climaticos/refugis.csv"
    districts = ROOT / "00_Datasets/processed/boundaries/districtes_epsg4326.geojson"
    transformer = Transformer.from_crs(25831, 4326, always_xy=True)

    def load_points(path: Path, label: str, has_latlon: bool) -> list[dict[str, object]]:
        points: list[dict[str, object]] = []
        with path.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                if has_latlon:
                    lat, lon = float(row["lat_4326"]), float(row["lon_4326"])
                else:
                    lon, lat = transformer.transform(float(row["x_25831"]), float(row["y_25831"]))
                points.append({"name": row.get("name", label), "district": row.get("district", ""), "lat": lat, "lon": lon})
        return points

    payload = {
        "parks": load_points(parks, "Parque", has_latlon=True),
        "shelters": load_points(shelters, "Refugio climático", has_latlon=False),
        "districts": json.loads(districts.read_text(encoding="utf-8")),
    }
    (ASSETS / "maps" / "parks_refuges_clusters.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    (ASSETS / "graphic").mkdir(parents=True, exist_ok=True)
    (ASSETS / "summaries").mkdir(parents=True, exist_ok=True)
    (ASSETS / "maps").mkdir(parents=True, exist_ok=True)
    extract_scene_figure()
    build_cell_date_sample()
    build_social_map_assets()
    print("content_prototype_assets=ok")


if __name__ == "__main__":
    main()
