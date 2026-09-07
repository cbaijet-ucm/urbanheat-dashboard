"""Genera capas WebP para reproducir el mapa Meteo del notebook 09."""

from __future__ import annotations

import json
import re
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pyarrow.dataset as ds
from matplotlib import colormaps
from PIL import Image
from pyproj import Transformer


ROOT = Path(__file__).resolve().parents[2]
GRID_PATH = ROOT / "00_Datasets/processed/grid/grid_30m_epsg25831.geoparquet"
METEO_PATH = ROOT / "00_Datasets/interim/features/dynamic/meteo_cell_date.parquet"
OUTPUT_DIR = ROOT / "07_Dashboard/static/meteo"
MANIFEST_PATH = ROOT / "07_Dashboard/assets/maps/meteo_evolution_manifest.json"

UNITS = {
    "T": "°C", "T_3h": "°C", "T_max24h": "°C",
    "HR": "%", "HR_6h": "%",
    "WS": "m/s", "WS_6h": "m/s", "WS_U": "m/s", "WS_V": "m/s",
    "WS_U_6h": "m/s", "WS_V_6h": "m/s",
    "Rain_72h": "mm", "Last_rain": "h",
    "Solar": "W/m²", "Solar_24h": "MJ/m²",
}


def scene_date(scene_id: str) -> str:
    match = re.search(r"_(20\d{6})_", scene_id)
    if not match:
        return scene_id
    value = match.group(1)
    return f"{value[:4]}-{value[4:6]}-{value[6:]}"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

    grid = gpd.read_parquet(GRID_PATH, columns=["row", "col", "cell_id", "geometry"])
    height = int(grid["row"].max()) + 1
    width = int(grid["col"].max()) + 1
    grid_ids = pd.Index(grid["cell_id"].astype(str))
    rows = grid["row"].to_numpy(dtype=np.int32)
    cols = grid["col"].to_numpy(dtype=np.int32)

    dataset = ds.dataset(METEO_PATH, format="parquet", partitioning="hive")
    features = [name for name in dataset.schema.names if name not in {"cell_id", "scene_id"}]
    fragments = list(dataset.get_fragments())

    samples: dict[str, list[np.ndarray]] = {feature: [] for feature in features}
    scene_frames: list[tuple[str, pd.DataFrame]] = []
    for fragment in fragments:
        frame = fragment.to_table(columns=["cell_id", *features]).to_pandas()
        expression = str(fragment.partition_expression)
        match = re.search(r'scene_id == "([^"]+)"', expression)
        scene_id = match.group(1) if match else Path(fragment.path).parent.name.split("=", 1)[-1]
        scene_frames.append((scene_id, frame))
        stride = max(1, len(frame) // 5000)
        sampled = frame.iloc[::stride]
        for feature in features:
            values = sampled[feature].to_numpy(dtype=np.float32)
            samples[feature].append(values[np.isfinite(values)])

    limits: dict[str, list[float]] = {}
    for feature in features:
        values = np.concatenate(samples[feature])
        low, high = np.nanpercentile(values, [2, 98])
        if not np.isfinite(low) or not np.isfinite(high):
            low, high = 0.0, 1.0
        if low == high:
            high = low + 1e-6
        limits[feature] = [float(low), float(high)]

    scenes = []
    cmap = colormaps["turbo"]
    for scene_index, (scene_id, frame) in enumerate(sorted(scene_frames, key=lambda item: scene_date(item[0]))):
        ordered = frame.set_index(frame["cell_id"].astype(str)).reindex(grid_ids)
        scene_key = f"s{scene_index:02d}"
        scene_dir = OUTPUT_DIR / scene_key
        scene_dir.mkdir(exist_ok=True)
        images: dict[str, str] = {}
        for feature in features:
            values = ordered[feature].to_numpy(dtype=np.float32)
            raster = np.full((height, width), np.nan, dtype=np.float32)
            raster[rows, cols] = values
            low, high = limits[feature]
            normalized = np.clip((raster - low) / (high - low), 0, 1)
            rgba = (cmap(np.nan_to_num(normalized, nan=0.0)) * 255).astype(np.uint8)
            rgba[..., 3] = np.where(np.isfinite(raster), 255, 0).astype(np.uint8)
            filename = f"{feature}.webp"
            Image.fromarray(rgba, mode="RGBA").save(scene_dir / filename, "WEBP", quality=82, method=4)
            images[feature] = f"meteo/{scene_key}/{filename}"
        scenes.append({"id": scene_id, "label": scene_date(scene_id), "images": images})
        print(f"[{scene_index + 1}/{len(scene_frames)}] {scene_id}")

    minx, miny, maxx, maxy = grid.total_bounds
    transformer = Transformer.from_crs(grid.crs, "EPSG:4326", always_xy=True)
    west, south = transformer.transform(minx, miny)
    east, north = transformer.transform(maxx, maxy)
    manifest = {
        "bounds": [[south, west], [north, east]],
        "features": [{"id": feature, "unit": UNITS.get(feature, ""), "limits": limits[feature]} for feature in features],
        "scenes": scenes,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    print(f"Manifest: {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
