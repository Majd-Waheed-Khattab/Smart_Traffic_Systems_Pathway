from __future__ import annotations

import argparse
import hashlib
import json
import random
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import cv2
import yaml

from validate_datasets import IMAGE_EXTENSIONS, PROJECT_CLASSES, find_label

ALIASES = {
    "car": "car",
    "big car": "car",
    "car tracking 1": "car",
    "police car": "car",
    "taxi": "car",
    "vehicle": "car",
    "van": "van",
    "microbus": "van",
    "pickup-van": "van",
    "pickup": "van",
    "bus": "bus",
    "truck": "truck",
    "motorcycle": "motorcycle",
    "motorbike": "motorcycle",
    "motor": "motorcycle",
    "motorcycle_traffic_police": "motorcycle_traffic_police",
    "police motorcycle": "motorcycle_traffic_police",
    "police_motorcycle": "motorcycle_traffic_police",
}


def class_names(root: Path) -> list[str]:
    if root.name == "police_motorcycles":
        return ["motorcycle_traffic_police"]
    metadata = next(root.glob("**/data.yaml"), None)
    if metadata is None:
        return []
    data: dict[str, Any] = yaml.safe_load(metadata.read_text()) or {}
    names = data.get("names", [])
    return list(names.values()) if isinstance(names, dict) else list(names)


def canonical_name(source: Path, name: str) -> str | None:
    normalized = name.strip().lower()
    if source.name == "police_motorcycles":
        return "motorcycle_traffic_police"
    for suffix in ("-close", "-day", "-night"):
        if normalized.endswith(suffix):
            normalized = normalized[: -len(suffix)]
    return ALIASES.get(normalized)


def source_files(root: Path) -> list[Path]:
    return sorted(
        path for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def load_annotations(image: Path, source: Path) -> tuple[list[str], list[str]]:
    label = find_label(image)
    if label is None or cv2.imread(str(image)) is None:
        return [], ["missing_label_or_corrupt_image"]
    names = class_names(source)
    if not names:
        return [], ["missing_data_yaml"]
    mapped: list[str] = []
    reasons: list[str] = []
    for line_number, line in enumerate(
        (line.strip() for line in label.read_text().splitlines()), start=1
    ):
        if not line:
            continue
        values = line.split()
        if len(values) != 5:
            reasons.append(f"invalid_label_line:{label}:{line_number}")
            continue
        try:
            source_id = int(values[0])
            coords = [float(value) for value in values[1:]]
        except ValueError:
            reasons.append(f"non_numeric_label_line:{label}:{line_number}")
            continue
        if source_id < 0 or source_id >= len(names) or any(value < 0 or value > 1 for value in coords):
            reasons.append(f"invalid_label_values:{label}:{line_number}")
            continue
        target = canonical_name(source, str(names[source_id]))
        if target is None:
            reasons.append(f"unmapped_class:{names[source_id]}")
            continue
        mapped.append(f"{PROJECT_CLASSES.index(target)} {' '.join(values[1:])}")
    return mapped, reasons


def write_summary(summary: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    rows = [
        "# Dataset summary", "",
        f"- Images copied: **{summary['totals']['images']}**",
        f"- Labels copied: **{summary['totals']['labels']}**",
        f"- Skipped files: **{len(summary['skipped_files'])}**",
        "",
        "| Split | Images | Labels |", "|---|---:|---:|",
    ]
    rows.extend(
        f"| {split} | {summary['splits'][split]['images']} | {summary['splits'][split]['labels']} |"
        for split in ("train", "val", "test")
    )
    rows += ["", "| Class | Count |", "|---|---:|"]
    rows.extend(f"| {name} | {count} |" for name, count in summary["class_counts"].items())
    rows += ["", "## Class mappings", ""]
    rows.extend(f"- `{source}`: {mapping}" for source, mapping in summary["class_mappings"].items())
    path.with_suffix(".md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, default=Path("data/source_datasets"))
    parser.add_argument("--output-root", type=Path, default=Path("data/dataset"))
    parser.add_argument("--seed", type=int, default=20261015)
    parser.add_argument("--summary", type=Path, default=Path("reports/dataset_summary.json"))
    args = parser.parse_args()
    random.seed(args.seed)
    if args.output_root.exists():
        for split in ("train", "val", "test"):
            for kind in ("images", "labels"):
                for path in (args.output_root / kind / split).glob("*"):
                    path.unlink()
    for split in ("train", "val", "test"):
        (args.output_root / "images" / split).mkdir(parents=True, exist_ok=True)
        (args.output_root / "labels" / split).mkdir(parents=True, exist_ok=True)

    candidates: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    seen_hashes: set[str] = set()
    mappings: dict[str, str] = {}
    roots = [path for path in sorted(args.source_root.iterdir()) if path.is_dir()]
    for root in roots:
        names = class_names(root)
        mappings[root.name] = ", ".join(
            f"{name}->{canonical_name(root, name) or 'SKIP'}" for name in names
        ) or ("all labels -> motorcycle_traffic_police" if root.name == "police_motorcycles" else "no mapping")
        for image in source_files(root):
            digest = hashlib.sha256(image.read_bytes()).hexdigest()
            if digest in seen_hashes:
                skipped.append({"file": str(image), "reason": "duplicate_image"})
                continue
            mapped, reasons = load_annotations(image, root)
            if reasons:
                for reason in reasons:
                    skipped.append({"file": str(image), "reason": reason})
            if not mapped:
                skipped.append({"file": str(image), "reason": "no_mappable_annotations"})
                continue
            seen_hashes.add(digest)
            candidates.append({"image": image, "labels": mapped, "source": root.name, "digest": digest})

    random.shuffle(candidates)
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in candidates:
        groups[f"{item['source']}:{item['image'].stem.rsplit('_jpg', 1)[0]}"].append(item)
    group_list = list(groups.values())
    random.shuffle(group_list)
    targets = {"train": 0.8, "val": 0.1, "test": 0.1}
    split_items: dict[str, list[dict[str, Any]]] = defaultdict(list)
    total = len(candidates)
    for group in group_list:
        current = min(
            targets,
            key=lambda split: len(split_items[split]) / max(targets[split], 0.01),
        )
        split_items[current].extend(group)

    class_counts = Counter()
    split_counts: dict[str, dict[str, int]] = {}
    for split in ("train", "val", "test"):
        split_counts[split] = {"images": 0, "labels": 0}
        for index, item in enumerate(split_items[split]):
            stem = f"{item['source']}_{index:06d}_{item['digest'][:10]}"
            shutil.copy2(item["image"], args.output_root / "images" / split / f"{stem}{item['image'].suffix.lower()}")
            (args.output_root / "labels" / split / f"{stem}.txt").write_text("\n".join(item["labels"]) + "\n")
            split_counts[split]["images"] += 1
            split_counts[split]["labels"] += 1
            for line in item["labels"]:
                class_counts[PROJECT_CLASSES[int(line.split()[0])]] += 1

    (args.output_root / "data.yaml").write_text(
        yaml.safe_dump(
            {"path": str(args.output_root.resolve()), "train": "images/train", "val": "images/val", "test": "images/test", "nc": 6, "names": PROJECT_CLASSES},
            sort_keys=False,
        )
    )
    summary = {
        "seed": args.seed, "source_datasets": [root.name for root in roots],
        "class_mappings": mappings, "class_counts": dict(class_counts),
        "splits": split_counts, "totals": {"images": total, "labels": total},
        "skipped_files": skipped,
        "leakage_policy": "exact image duplicates removed; source/name groups kept within one split",
    }
    write_summary(summary, args.summary)


if __name__ == "__main__":
    main()
