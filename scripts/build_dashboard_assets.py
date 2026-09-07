"""Genera activos compactos del dashboard a partir del registro declarado.

Nunca copia el dataset tabular completo, rasters fuente ni modelos de inferencia.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


DASHBOARD_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = DASHBOARD_DIR.parents[1]
REGISTRY_PATH = DASHBOARD_DIR / "data" / "external_artifacts.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def derive(source: Path, destination: Path, method: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if method == "copy":
        shutil.copy2(source, destination)
    elif method == "drop_mode_column":
        frame = pd.read_csv(source)
        frame.drop(columns=["mode"], errors="ignore").to_csv(destination, index=False)
    else:
        raise ValueError(f"Método de migración no reconocido: {method}")


def main() -> int:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    manifest = {"generated_at": datetime.now(timezone.utc).isoformat(), "artifacts": [], "missing": []}
    for item in registry:
        if not item["required"]:
            print(f"OMITIDO (opcional): {item['source']}")
            continue
        source = REPO_DIR / item["source"]
        destination = DASHBOARD_DIR / item["derived"]
        if not source.exists():
            manifest["missing"].append({"source": item["source"], "required": item["required"]})
            print(f"FALTA: {item['source']}")
            continue
        derive(source, destination, item["method"])
        manifest["artifacts"].append({
            "name": destination.name,
            "path": destination.relative_to(DASHBOARD_DIR).as_posix(),
            "source": item["source"],
            "transformation": item["method"],
            "size_bytes": destination.stat().st_size,
            "sha256": sha256(destination),
            "crs": "EPSG:4326" if destination.suffix == ".geojson" else None,
        })
        print(f"OK: {item['source']} -> {destination.relative_to(DASHBOARD_DIR)}")
    (DASHBOARD_DIR / "assets" / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    missing_required = [item for item in manifest["missing"] if item["required"]]
    return 1 if missing_required else 0


if __name__ == "__main__":
    raise SystemExit(main())
