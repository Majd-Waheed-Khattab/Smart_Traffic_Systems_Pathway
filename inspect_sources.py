from collections import Counter
from pathlib import Path

import yaml


PROJECT_DIR = Path(__file__).resolve().parent
SOURCES_DIR = PROJECT_DIR / "data" / "source_datasets"

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".jfif",
}


def collect_images(source_dir):
    return {
        path.stem
        for path in source_dir.rglob("*")
        if path.is_file()
        and path.suffix.lower() in IMAGE_EXTENSIONS
        and "images" in path.parts
    }


def collect_labels(source_dir):
    return {
        path.stem
        for path in source_dir.rglob("*.txt")
        if path.is_file()
        and "labels" in path.parts
    }


def find_data_yaml(source_dir):
    yaml_files = list(source_dir.rglob("data.yaml"))
    if not yaml_files:
        yaml_files = list(source_dir.rglob("data.yml"))
    return yaml_files[0] if yaml_files else None


def read_names(yaml_path):
    if yaml_path is None:
        return None

    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    return data.get("names")


def count_classes(source_dir):
    counts = Counter()

    label_paths = [
        path
        for path in source_dir.rglob("*.txt")
        if path.is_file() and "labels" in path.parts
    ]

    for label_path in label_paths:
        try:
            lines = label_path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            lines = label_path.read_text(encoding="latin-1").splitlines()

        for line in lines:
            parts = line.split()

            if len(parts) != 5:
                continue

            class_id = parts[0]

            try:
                int(class_id)
            except ValueError:
                continue

            counts[class_id] += 1

    return dict(sorted(counts.items(), key=lambda item: int(item[0])))


for source_dir in sorted(SOURCES_DIR.iterdir()):
    if not source_dir.is_dir():
        continue

    images = collect_images(source_dir)
    labels = collect_labels(source_dir)

    missing_labels = images - labels
    orphan_labels = labels - images

    yaml_path = find_data_yaml(source_dir)

    print("\n" + "=" * 60)
    print(f"المصدر: {source_dir.name}")
    print(f"عدد الصور: {len(images)}")
    print(f"عدد Labels: {len(labels)}")
    print(f"صور بدون Label: {len(missing_labels)}")
    print(f"Labels بدون صورة: {len(orphan_labels)}")
    print(f"أرقام الفئات الحقيقية: {count_classes(source_dir)}")

    if yaml_path:
        print(f"data.yaml: {yaml_path}")
        print(f"names: {read_names(yaml_path)}")
    else:
        print("data.yaml: غير موجود")

    if missing_labels:
        print("أمثلة صور بدون Labels:")
        for item in sorted(missing_labels)[:5]:
            print(f"  {item}")

    if orphan_labels:
        print("أمثلة Labels بدون صور:")
        for item in sorted(orphan_labels)[:5]:
            print(f"  {item}")