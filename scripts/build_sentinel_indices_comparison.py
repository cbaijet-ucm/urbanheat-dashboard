"""Genera el asset estático equivalente al grid 2x3 del notebook Sentinel."""

from pathlib import Path
import json

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import rasterio
from rasterio.warp import transform_bounds


ROOT = Path(__file__).resolve().parents[2]
SENTINEL = ROOT / "00_Datasets" / "processed" / "raster_stacks" / "sentinel"
OUTPUT = ROOT / "07_Dashboard" / "assets" / "graphic" / "sentinel_indices_comparison.png"
MAP_OUTPUT = ROOT / "07_Dashboard" / "assets" / "maps" / "sentinel_indices"
MAP_MANIFEST = ROOT / "07_Dashboard" / "assets" / "maps" / "sentinel_indices_manifest.json"

SCENES = (
    ("REFERENCE", "2023-04-19"),
    ("CORE", "2024-07-11"),
)
LAYERS = (
    ("NDVI", -0.2, 0.8, ("brown", "yellow", "green")),
    ("NDBI", -0.5, 0.5, ("green", "white", "purple")),
    ("MNDWI", -0.5, 0.5, ("brown", "white", "blue")),
)


def main() -> None:
    figure, axes = plt.subplots(2, 3, figsize=(16, 10), facecolor="white")
    map_manifest = {}
    for row, (scene_kind, date) in enumerate(SCENES):
        path = SENTINEL / f"{date}_sentinel_indexes.tif"
        with rasterio.open(path) as source:
            west, south, east, north = transform_bounds(source.crs, "EPSG:4326", *source.bounds)
            for column, (name, minimum, maximum, colors) in enumerate(LAYERS):
                values = source.read(column + 1, masked=True).astype("float32")
                values = np.ma.masked_invalid(values)
                axis = axes[row, column]
                cmap = LinearSegmentedColormap.from_list(name.lower(), colors)
                cmap.set_bad("white", alpha=0)
                image = axis.imshow(values, cmap=cmap, vmin=minimum, vmax=maximum)
                axis.set_title(f"{scene_kind} · {name} · {date}", loc="left", fontsize=13, pad=9)
                axis.set_axis_off()
                colorbar = figure.colorbar(image, ax=axis, fraction=0.035, pad=0.018)
                colorbar.ax.tick_params(labelsize=8, length=2)
                colorbar.outline.set_linewidth(0.4)
                normalized = np.clip((values.filled(minimum) - minimum) / (maximum - minimum), 0, 1)
                rgba = (cmap(normalized) * 255).astype("uint8")
                rgba[values.mask, 3] = 0
                map_name = f"{scene_kind.lower()}_{name.lower()}_{date}.png"
                MAP_OUTPUT.mkdir(parents=True, exist_ok=True)
                plt.imsave(MAP_OUTPUT / map_name, rgba)
                map_manifest[f"{scene_kind}_{name}"] = {
                    "title": f"{scene_kind} · {name} · {date}",
                    "image": map_name,
                    "bounds": [[south, west], [north, east]],
                }
    figure.suptitle("Comparación visual de índices Sentinel-2", x=0.055, ha="left", fontsize=19, fontweight="normal")
    figure.subplots_adjust(left=0.045, right=0.975, top=0.91, bottom=0.035, wspace=0.08, hspace=0.13)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, dpi=180, facecolor="white")
    plt.close(figure)
    MAP_MANIFEST.write_text(json.dumps(map_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
