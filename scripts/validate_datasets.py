from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import cv2
import yaml

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".jfif", ".webp", ".bmp"}
PROJECT_CLASSES = [
    "car",
    "van",
    "bus",
    "truck",
    "motorcycle",
    "motorcycle_traffic_police",
]


def image_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def find_label(image: Path) -> Path | None:
    candidates = [
        image.with_suffix(".txt"),
        image.parent.parent / "labels" / f"{image.stem}.txt",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def dataset_names(root: Path) -> list[str]:
    metadata = next(root.glob("**/data.yaml"), None)
    if metadata is None:
        return []
    try:
        data: dict[str, Any] = yaml.safe_load(metadata.read_text()) or {}
        names = data.get("names", [])
        return list(names.values()) if isinstance(names, dict) else list(names)
    except (OSError, yaml.YAMLError, TypeError, ValueError):
        return []


def validate_dataset(root: Path) -> dict[str, Any]:
    images = image_files(root)
    counts = Counter()
    invalid_lines: list[dict[str, Any]] = []
    missing_labels: list[str] = []
    orphan_labels: list[str] = []
    empty_labels: list[str] = []
    corrupt_images: list[str] = []
    hashes: dict[str, list[str]] = {}

    image_stems = {image.stem for image in images}
    label_files = list(root.rglob("*.txt"))
    for label in label_files:
        if label.stem not in image_stems:
            orphan_labels.append(str(label))

    for image in images:
        relative = str(image.relative_to(root))
        if cv2.imread(str(image)) is None:
            corrupt_images.append(relative)
        digest = hashlib.sha256(image.read_bytes()).hexdigest()
        hashes.setdefault(digest, []).append(relative)
        label = find_label(image)
        if label is None:
            missing_labels.append(relative)
            continue
        lines = [line.strip() for line in label.read_text().splitlines() if line.strip()]
        if not lines:
            empty_labels.append(str(label.relative_to(root)))
            continue
        for line_number, line in enumerate(lines, start=1):
            values = line.split()
            if len(values) != 5:
                invalid_lines.append(
                    {"file": str(label), "line": line_number, "reason": "expected_5_values"}
                )
                continue
            try:
                class_id, *coordinates = [float(value) for value in values]
            except ValueError:
                invalid_lines.append(
                    {"file": str(label), "line": line_number, "reason": "non_numeric"}
                )
                continue
            if class_id != int(class_id) or class_id < 0:
                invalid_lines.append(
                    {"file": str(label), "line": line_number, "reason": "invalid_class_id"}
                )
            if any(value < 0 or value > 1 for value in coordinates):
                invalid_lines.append(
                    {"file": str(label), "line": line_number, "reason": "coordinate_out_of_range"}
                )
            counts[str(int(class_id))] += 1

    duplicate_groups = [files for files in hashes.values() if len(files) > 1]
    return {
        "dataset": root.name,
        "path": str(root),
        "class_names": dataset_names(root),
        "images": len(images),
        "labels": len(label_files),
        "missing_labels": missing_labels,
        "orphan_labels": orphan_labels,
        "empty_labels": empty_labels,
        "corrupt_images": corrupt_images,
        "invalid_label_lines": invalid_lines,
        "class_id_counts": dict(counts),
        "duplicate_image_groups": duplicate_groups,
        "valid_image_candidates": len(images) - len(missing_labels) - len(corrupt_images),
    }


def write_reports(report: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    rows = [
        "# Dataset validation report",
        "",
        f"- Datasets inspected: **{len(report['datasets'])}**",
        f"- Images inspected: **{report['totals']['images']}**",
        f"- Missing labels: **{report['totals']['missing_labels']}**",
        f"- Corrupt images: **{report['totals']['corrupt_images']}**",
        f"- Invalid label lines: **{report['totals']['invalid_label_lines']}**",
        "",
        "| Dataset | Images | Labels | Missing | Corrupt | Invalid lines | Duplicate groups |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for item in report["datasets"]:
        rows.append(
            f"| {item['dataset']} | {item['images']} | {item['labels']} | "
            f"{len(item['missing_labels'])} | {len(item['corrupt_images'])} | "
            f"{len(item['invalid_label_lines'])} | {len(item['duplicate_image_groups'])} |"
        )
    markdown_path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("data/source_datasets"))
    parser.add_argument("--json", type=Path, default=Path("reports/dataset_validation_report.json"))
    parser.add_argument("--markdown", type=Path, default=Path("reports/dataset_validation_report.md"))
    args = parser.parse_args()
    datasets = [path for path in sorted(args.root.iterdir()) if path.is_dir()]
    results = [validate_dataset(path) for path in datasets]
    totals = {
        key: sum(
            len(item[key]) if isinstance(item[key], list) else item[key]
            for item in results
        )
        for key in ("images", "labels", "missing_labels", "corrupt_images", "invalid_label_lines")
    }
    write_reports({"project_classes": PROJECT_CLASSES, "datasets": results, "totals": totals}, args.json, args.markdown)


if __name__ == "__main__":
    main()
