from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ultralytics import YOLO


def evaluate(model_path: Path, data: Path, output_dir: Path) -> dict[str, Any]:
    model = YOLO(str(model_path))
    name = model_path.stem
    metrics = model.val(
        data=str(data),
        split="test",
        imgsz=320,
        batch=8,
        device="cpu",
        project=str(output_dir),
        name=name,
        exist_ok=True,
        plots=True,
        verbose=False,
    )
    per_class = {}
    names = metrics.names if hasattr(metrics, "names") else model.names
    maps = getattr(metrics.box, "maps", [])
    precisions = getattr(metrics.box, "p", [])
    recalls = getattr(metrics.box, "r", [])
    for index, class_name in enumerate(names.values() if isinstance(names, dict) else names):
        per_class[str(class_name)] = {
            "precision": float(precisions[index]) if index < len(precisions) else None,
            "recall": float(recalls[index]) if index < len(recalls) else None,
            "map50_95": float(maps[index]) if index < len(maps) else None,
        }
    return {
        "model": str(model_path),
        "precision": float(metrics.box.mp),
        "recall": float(metrics.box.mr),
        "map50": float(metrics.box.map50),
        "map50_95": float(metrics.box.map),
        "per_class": per_class,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, default=Path("models/best_before_improvement.pt"))
    parser.add_argument("--improved", type=Path, default=Path("models/best_improved.pt"))
    parser.add_argument("--data", type=Path, default=Path("data/dataset/data.yaml"))
    parser.add_argument("--output", type=Path, default=Path("reports/model_comparison.json"))
    parser.add_argument("--reuse-json", action="store_true")
    args = parser.parse_args()
    if args.reuse_json and args.output.exists():
        results = json.loads(args.output.read_text(encoding="utf-8"))
        results.pop("decision_metrics", None)
    else:
        results = {
            "baseline": evaluate(args.baseline, args.data, Path("runs/detect/evaluation")),
            "improved": evaluate(args.improved, args.data, Path("runs/detect/evaluation")),
        }
    improved = results["improved"]
    baseline = results["baseline"]
    results["decision_metrics"] = {
        "map50_95_delta": improved["map50_95"] - baseline["map50_95"],
        "map50_delta": improved["map50"] - baseline["map50"],
        "precision_delta": improved["precision"] - baseline["precision"],
        "recall_delta": improved["recall"] - baseline["recall"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    lines = [
        "# Model comparison", "",
        "| Model | Precision | Recall | mAP50 | mAP50-95 |",
        "|---|---:|---:|---:|---:|",
    ]
    for label in ("baseline", "improved"):
        item = results[label]
        lines.append(
            f"| {label} | {item['precision']:.4f} | {item['recall']:.4f} | "
            f"{item['map50']:.4f} | {item['map50_95']:.4f} |"
        )
    lines += ["", "## Per-class metrics", ""]
    for label in ("baseline", "improved"):
        lines += [f"### {label}", "", "| Class | Precision | Recall | mAP50-95 |", "|---|---:|---:|---:|"]
        for class_name, item in results[label]["per_class"].items():
            def fmt(value: float | None) -> str:
                return "n/a" if value is None else f"{value:.4f}"

            lines.append(
                f"| {class_name} | {fmt(item['precision'])} | "
                f"{fmt(item['recall'])} | {fmt(item['map50_95'])} |"
            )
    args.output.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
