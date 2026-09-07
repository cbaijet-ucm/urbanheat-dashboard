"""Genera una vez las superficies LST de test para XGBoost y la CNN.

No reentrena ni modifica datasets. Reutiliza los rasters, tiles y estadísticas
persistidos por los notebooks 12 y 13, y deja un PNG ligero por modelo/escena
para que el dashboard sólo tenga que intercambiar capas ya preparadas.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

import geopandas as gpd
import joblib
from matplotlib import colormaps
import numpy as np
import pandas as pd
import tensorflow as tf
from xgboost import XGBRegressor


ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = ROOT / "00_Datasets"
MODELS_DIR = ROOT / "05_Models"
CACHE_DIR = ROOT / "07_Dashboard" / "assets" / "generated" / "model_comparison"

DEEP_DIR = DATASET_DIR / "processed" / "deep"
TABULAR_DIR = MODELS_DIR / "tabular_two_stage"
CNN_DIR = MODELS_DIR / "cnn"


def normalise_tile(raster: np.ndarray, row0: int, col0: int, size: int, channels: list[str], stats: pd.DataFrame) -> np.ndarray:
    tile = raster[row0 : row0 + size, col0 : col0 + size, :].copy()
    for index, channel in enumerate(channels):
        tile[:, :, index] = (tile[:, :, index] - stats.at[channel, "mean"]) / stats.at[channel, "std"]
    return tile


def cnn_prediction(
    scene_id: str,
    model: tf.keras.Model,
    static_stack: np.ndarray,
    static_channels: list[str],
    scene_stack: np.ndarray,
    scene_channels: list[str],
    tiles: pd.DataFrame,
    stats: pd.DataFrame,
) -> np.ndarray:
    """Reconstruye la escena completa promediando los tiles solapados del notebook 13."""
    height, width = static_stack.shape[:2]
    pred_sum = np.zeros((height, width), dtype=np.float32)
    pred_count = np.zeros((height, width), dtype=np.float32)
    scene_tiles = tiles.loc[tiles["scene_id"] == scene_id]

    batch_inputs: list[np.ndarray] = []
    batch_rows: list[tuple[int, int, int]] = []

    def flush() -> None:
        if not batch_inputs:
            return
        predictions = model.predict(np.stack(batch_inputs), batch_size=len(batch_inputs), verbose=0)[:, :, :, 0]
        for prediction, (row0, col0, size) in zip(predictions, batch_rows):
            pred_sum[row0 : row0 + size, col0 : col0 + size] += prediction
            pred_count[row0 : row0 + size, col0 : col0 + size] += 1
        batch_inputs.clear()
        batch_rows.clear()

    for tile in scene_tiles.itertuples(index=False):
        row0, col0, size = int(tile.row0), int(tile.col0), int(tile.tile_size)
        static_tile = normalise_tile(static_stack, row0, col0, size, static_channels, stats)
        dynamic_tile = normalise_tile(scene_stack, row0, col0, size, scene_channels, stats)
        batch_inputs.append(np.nan_to_num(np.concatenate((static_tile, dynamic_tile), axis=-1), nan=0.0).astype(np.float32))
        batch_rows.append((row0, col0, size))
        if len(batch_inputs) == 16:
            flush()
    flush()

    return np.divide(pred_sum, pred_count, out=np.full_like(pred_sum, np.nan), where=pred_count > 0)


def png_from_surface(surface: np.ndarray, lower: float, upper: float, cmap: str = "turbo") -> np.ndarray:
    scaled = np.clip((surface - lower) / (upper - lower), 0, 1)
    rgba = (colormaps[cmap](np.nan_to_num(scaled, nan=0.0)) * 255).astype(np.uint8)
    rgba[:, :, 3] = np.where(np.isfinite(surface), 235, 0).astype(np.uint8)
    return rgba


def main() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((TABULAR_DIR / "model_manifest.json").read_text(encoding="utf-8"))
    test_scene_ids = manifest["test_scene_ids"]
    temporal_features = manifest["temporal_features"]
    spatial_features = manifest["spatial_features"]

    temporal_model = joblib.load(TABULAR_DIR / "temporal_final.joblib")
    xgb_model = XGBRegressor()
    xgb_model.load_model(TABULAR_DIR / "xgboost_spatial.ubj")
    cnn_model = tf.keras.models.load_model(CNN_DIR / "model.keras", compile=False)

    with np.load(DEEP_DIR / "static_rasters.npz") as data:
        static_stack = data["static_stack"].astype(np.float32)
        inside_mask = data["inside_mask"].astype(bool)
        static_channels = [str(item) for item in data["channels"].tolist()]

    stats = pd.read_parquet(DEEP_DIR / "channel_statistics.parquet").set_index("channel")
    spatial_manifest = pd.read_parquet(DEEP_DIR / "spatial_rasters_manifest.parquet")
    tiles = pd.read_parquet(DEEP_DIR / "tile_manifest.parquet")
    temporal = pd.read_parquet(DATASET_DIR / "interim" / "scenes_by_date" / "temporal_model_extension" / "landsat_temporal_scene_dataset.parquet")

    cell_columns = ["scene_id", "row", "col", "LST_Celsius", *spatial_features]
    cell_data = pd.read_parquet(
        DATASET_DIR / "processed" / "cell_date_dataset" / "cell_date_dataset.parquet",
        columns=cell_columns,
        filters=[("inside_bcn", "==", True)],
    )

    grid = gpd.read_parquet(DATASET_DIR / "processed" / "grid" / "grid_30m_epsg25831.geoparquet")
    grid_wgs84 = grid.to_crs(4326)
    west, south, east, north = grid_wgs84.total_bounds
    cache_manifest: dict[str, object] = {
        "bounds": [[float(south), float(west)], [float(north), float(east)]],
        "scenes": [],
    }

    available = set(spatial_manifest["scene_id"])
    for scene_id in test_scene_ids:
        if scene_id not in available:
            print(f"Omitida, sin raster CNN persistido: {scene_id}")
            continue
        temporal_row = temporal.loc[temporal["scene_id"] == scene_id]
        scene_cells = cell_data.loc[cell_data["scene_id"] == scene_id]
        if temporal_row.empty or scene_cells.empty:
            print(f"Omitida, sin datos completos: {scene_id}")
            continue

        scene_mean = float(temporal_model.predict(temporal_row[temporal_features])[0])
        xgb_raw = xgb_model.predict(scene_cells[spatial_features])
        xgb_values = scene_mean + (xgb_raw - np.nanmean(xgb_raw))
        xgb_surface = np.full(static_stack.shape[:2], np.nan, dtype=np.float32)
        xgb_surface[scene_cells["row"].to_numpy(dtype=int), scene_cells["col"].to_numpy(dtype=int)] = xgb_values
        observed_surface = np.full(static_stack.shape[:2], np.nan, dtype=np.float32)
        observed_surface[scene_cells["row"].to_numpy(dtype=int), scene_cells["col"].to_numpy(dtype=int)] = scene_cells["LST_Celsius"].to_numpy(dtype=np.float32)

        scene_record = spatial_manifest.loc[spatial_manifest["scene_id"] == scene_id].iloc[0]
        with np.load(Path(scene_record["scene_path"])) as data:
            cnn_anomaly = cnn_prediction(
                scene_id, cnn_model, static_stack, static_channels,
                data["scene_stack"].astype(np.float32), [str(item) for item in data["channels"].tolist()],
                tiles, stats,
            )
        valid_cnn = np.isfinite(cnn_anomaly) & inside_mask
        cnn_surface = scene_mean + cnn_anomaly - np.nanmean(cnn_anomaly[valid_cnn])
        cnn_surface[~inside_mask] = np.nan

        lower, upper = np.nanpercentile(np.concatenate((xgb_surface[np.isfinite(xgb_surface)], cnn_surface[np.isfinite(cnn_surface)])), [2, 98])
        slug = str(scene_record["date_acquired"]).split(" ")[0]
        xgb_path = CACHE_DIR / f"{slug}_xgboost.png"
        cnn_path = CACHE_DIR / f"{slug}_cnn.png"
        import matplotlib.image as mpimg
        mpimg.imsave(xgb_path, png_from_surface(xgb_surface, lower, upper), origin="upper")
        mpimg.imsave(cnn_path, png_from_surface(cnn_surface, lower, upper), origin="upper")
        np.savez_compressed(CACHE_DIR / f"{slug}_predictions.npz", observed=observed_surface, xgboost=xgb_surface, cnn=cnn_surface)
        cache_manifest["scenes"].append({
            "id": scene_id,
            "date": slug,
            "xgboost": xgb_path.name,
            "cnn": cnn_path.name,
            "range_celsius": [round(float(lower), 2), round(float(upper), 2)],
        })
        print(f"Generada: {slug}")

    # Una única escala absoluta para todas las fechas y ambos modelos. La
    # comparación temporal deja de depender del contraste propio de cada día.
    cached_surfaces = []
    for scene in cache_manifest["scenes"]:
        with np.load(CACHE_DIR / f"{scene['date']}_predictions.npz") as data:
            cached_surfaces.extend(
                surface[np.isfinite(surface)] for surface in (data["xgboost"], data["cnn"])
            )
    global_lower = float(np.floor(np.min(np.concatenate(cached_surfaces))))
    global_upper = float(np.ceil(np.max(np.concatenate(cached_surfaces))))
    import matplotlib.image as mpimg
    for scene in cache_manifest["scenes"]:
        with np.load(CACHE_DIR / f"{scene['date']}_predictions.npz") as data:
            mpimg.imsave(CACHE_DIR / scene["xgboost"], png_from_surface(data["xgboost"], global_lower, global_upper), origin="upper")
            mpimg.imsave(CACHE_DIR / scene["cnn"], png_from_surface(data["cnn"], global_lower, global_upper), origin="upper")
        scene["range_celsius"] = [global_lower, global_upper]
    cache_manifest["common_range_celsius"] = [global_lower, global_upper]

    # Reproducción del mapa interactivo final del notebook 13: composite de
    # test y diferencia de error absoluto CNN − XGBoost por celda.
    observed_sum = np.zeros(static_stack.shape[:2], dtype=np.float64)
    xgb_sum = np.zeros(static_stack.shape[:2], dtype=np.float64)
    cnn_sum = np.zeros(static_stack.shape[:2], dtype=np.float64)
    observed_count = np.zeros(static_stack.shape[:2], dtype=np.uint16)
    xgb_count = np.zeros(static_stack.shape[:2], dtype=np.uint16)
    cnn_count = np.zeros(static_stack.shape[:2], dtype=np.uint16)
    for scene in cache_manifest["scenes"]:
        with np.load(CACHE_DIR / f"{scene['date']}_predictions.npz") as data:
            for values, total, count in (
                (data["observed"], observed_sum, observed_count),
                (data["xgboost"], xgb_sum, xgb_count),
                (data["cnn"], cnn_sum, cnn_count),
            ):
                valid = np.isfinite(values)
                total[valid] += values[valid]
                count[valid] += 1
    observed_composite = np.divide(observed_sum, observed_count, out=np.full_like(observed_sum, np.nan), where=observed_count > 0)
    xgb_composite = np.divide(xgb_sum, xgb_count, out=np.full_like(xgb_sum, np.nan), where=xgb_count > 0)
    cnn_composite = np.divide(cnn_sum, cnn_count, out=np.full_like(cnn_sum, np.nan), where=cnn_count > 0)
    common = inside_mask & np.isfinite(observed_composite) & np.isfinite(xgb_composite) & np.isfinite(cnn_composite)
    error_difference = np.where(common, np.abs(observed_composite - cnn_composite) - np.abs(observed_composite - xgb_composite), np.nan)
    difference_limit = float(np.nanquantile(np.abs(error_difference[common]), 0.99))
    error_png = "error_difference_cnn_vs_xgboost.png"
    mpimg.imsave(CACHE_DIR / error_png, png_from_surface(error_difference, -difference_limit, difference_limit, cmap="RdBu_r"), origin="upper")
    np.savez_compressed(CACHE_DIR / "error_difference_cnn_vs_xgboost.npz", difference=error_difference)
    cache_manifest["error_difference"] = {
        "image": error_png,
        "range_celsius": [-round(difference_limit, 3), round(difference_limit, 3)],
        "description": "|error CNN| − |error XGBoost|",
    }
    (CACHE_DIR / "manifest.json").write_text(json.dumps(cache_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Cache lista: {CACHE_DIR}")


if __name__ == "__main__":
    main()
