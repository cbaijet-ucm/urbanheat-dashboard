"""Build the compact territorial LST payload consumed by the dashboard."""

from __future__ import annotations

import json
from pathlib import Path
import re
import unicodedata

import geopandas as gpd
import pandas as pd
import pyarrow.parquet as pq


PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_DIR / "00_Datasets"
BOUNDARIES_DIR = DATA_DIR / "processed" / "boundaries"
GRID_PATH = DATA_DIR / "processed" / "grid" / "grid_30m_epsg25831.geoparquet"
LST_DIR = DATA_DIR / "interim" / "lst"
OUTPUT_PATH = PROJECT_DIR / "07_Dashboard" / "assets" / "maps" / "lst_territorial_aggregation.json"


def _normalise(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", text).strip().lower()


def _summer_lst() -> pd.DataFrame:
    tables = []
    for path in sorted(LST_DIR.glob("LST_cells_*.parquet")):
        match = re.search(r"(\d{4})-(\d{2})-(\d{2})", path.stem)
        if not match or int(match.group(2)) not in {7, 8}:
            continue
        table = pq.read_table(path, columns=["cell_id", "LST_Celsius"])
        tables.append(table.to_pandas())
    if not tables:
        raise RuntimeError(f"No July/August LST parquet files found in {LST_DIR}")
    return (
        pd.concat(tables, ignore_index=True)
        .groupby("cell_id", as_index=False, observed=True)["LST_Celsius"]
        .mean()
    )


def _level_payload(
    source_name: str,
    grid_column: str,
    boundary_file: str,
    boundary_column: str,
    label: str,
    grid_values: pd.DataFrame,
) -> dict:
    values = (
        grid_values.dropna(subset=[grid_column, "LST_Celsius"])
        .groupby(grid_column, as_index=False, observed=True)["LST_Celsius"]
        .mean()
    )
    values["_join"] = values[grid_column].map(_normalise)

    boundaries = gpd.read_file(BOUNDARIES_DIR / boundary_file).to_crs(4326)
    boundaries["_join"] = boundaries[boundary_column].map(_normalise)
    merged = boundaries.merge(values[["_join", "LST_Celsius"]], on="_join", how="left")
    merged = merged.dropna(subset=["LST_Celsius"]).copy()
    merged["name"] = merged[boundary_column].astype(str)
    merged["lst"] = merged["LST_Celsius"].round(2)
    merged["level"] = source_name
    merged.geometry = merged.geometry.simplify(0.000025, preserve_topology=True)
    feature_collection = json.loads(merged[["name", "lst", "level", "geometry"]].to_json(drop_id=True))
    return {"id": source_name, "label": label, "geojson": feature_collection}


def main() -> None:
    grid = pd.read_parquet(
        GRID_PATH,
        columns=["cell_id", "inside_bcn", "district_name", "barri_name", "section_code"],
    )
    grid = grid.loc[grid["inside_bcn"]].drop_duplicates("cell_id")
    grid_values = grid.merge(_summer_lst(), on="cell_id", how="inner", validate="one_to_one")

    levels = [
        _level_payload(
            "district",
            "district_name",
            "districtes_epsg4326.geojson",
            "NOM",
            "Distrito",
            grid_values,
        ),
        _level_payload(
            "neighbourhood",
            "barri_name",
            "barris_epsg4326.geojson",
            "NOM",
            "Barrio",
            grid_values,
        ),
        _level_payload(
            "census_section",
            "section_code",
            "seccions_epsg4326.geojson",
            "section_code",
            "Sección censal",
            grid_values,
        ),
    ]
    values = [
        feature["properties"]["lst"]
        for level in levels
        for feature in level["geojson"]["features"]
    ]
    bounds_source = gpd.read_file(BOUNDARIES_DIR / "districtes_epsg4326.geojson").to_crs(4326)
    west, south, east, north = (float(value) for value in bounds_source.total_bounds)
    payload = {
        "metric": "LST media julio–agosto",
        "unit": "°C",
        "limits": [round(min(values), 2), round(max(values), 2)],
        "bounds": [[south, west], [north, east]],
        "levels": levels,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    counts = {level["label"]: len(level["geojson"]["features"]) for level in levels}
    print(f"Wrote {OUTPUT_PATH} ({OUTPUT_PATH.stat().st_size:,} bytes): {counts}")


if __name__ == "__main__":
    main()
