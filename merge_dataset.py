from pathlib import Path
from collections import Counter
import random
import shutil
import yaml


PROJECT_DIR = Path(__file__).resolve().parent
SOURCES_DIR = PROJECT_DIR / "data" / "source_datasets"
OUTPUT_DIR = PROJECT_DIR / "data" / "dataset"

SEED = 42
TRAIN_RATIO = 0.80
VAL_RATIO = 0.10
TEST_RATIO = 0.10

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".jfif",
}

FINAL_NAMES = {
    0: "car",
    1: "van",
    2: "bus",
    3: "truck",
    4: "motorcycle",
    5: "motorcycle_traffic_police",
}

SOURCE_CONFIGS = {
    "roboflow_03": {
        "mapping": {
            0: 2,  # Bus -> bus
            1: 0,  # Car -> car
            2: 4,  # Motorcycle -> motorcycle
            3: 0,  # Taxi -> car
            4: 3,  # Truck -> truck
            5: 1,  # Van -> van
        }
    },
    "roboflow_05": {
        "mapping": {
            0: 2,  # bus -> bus
            1: 0,  # car -> car
            2: 4,  # motorcycle -> motorcycle
            3: 0,  # pickup -> car
            4: 3,  # truck -> truck
            5: 1,  # van -> van
        }
    },
    "police_motorcycles": {
        "mapping": {
            0: 5,  # police motorcycle -> motorcycle_traffic_police
        }
    },
}


def create_output_directories():
    for split in ["train", "val", "test"]:
        (OUTPUT_DIR / "images" / split).mkdir(parents=True, exist_ok=True)
        (OUTPUT_DIR / "labels" / split).mkdir(parents=True, exist_ok=True)


def find_image_for_label(label_path):
    image_dir = label_path.parent.parent / "images"

    candidates = [
        path
        for path in image_dir.rglob("*")
        if path.is_file()
        and path.stem == label_path.stem
        and (
            path.suffix.lower() in IMAGE_EXTENSIONS
            or path.suffix == ""
        )
    ]

    if not candidates:
        return None

    return sorted(candidates)[0]


def find_source_items(source_name):
    source_dir = SOURCES_DIR / source_name
    items = []

    label_paths = sorted(
        path
        for path in source_dir.rglob("*.txt")
        if path.is_file() and "labels" in path.parts
    )

    for label_path in label_paths:
        image_path = find_image_for_label(label_path)

        if image_path is None:
            continue

        items.append((image_path, label_path))

    return items


def convert_label(label_path, mapping):
    converted_lines = []

    try:
        lines = label_path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        lines = label_path.read_text(encoding="latin-1").splitlines()

    for line_number, line in enumerate(lines, start=1):
        parts = line.split()

        if len(parts) != 5:
            print(
                f"تحذير: سطر غير صالح تم تجاهله: "
                f"{label_path}:{line_number}"
            )
            continue

        try:
            source_class = int(parts[0])
        except ValueError:
            print(
                f"تحذير: class id غير صالح تم تجاهله: "
                f"{label_path}:{line_number}"
            )
            continue

        if source_class not in mapping:
            print(
                f"تحذير: class id {source_class} غير موجود في mapping: "
                f"{label_path}"
            )
            continue

        try:
            coordinates = [float(value) for value in parts[1:]]
        except ValueError:
            print(
                f"تحذير: إحداثيات غير صالحة تم تجاهلها: "
                f"{label_path}:{line_number}"
            )
            continue

        if not all(0.0 <= value <= 1.0 for value in coordinates):
            print(
                f"تحذير: إحداثيات خارج النطاق 0..1 تم تجاهلها: "
                f"{label_path}:{line_number}"
            )
            continue

        target_class = mapping[source_class]

        converted_lines.append(
            f"{target_class} "
            f"{coordinates[0]:.6f} "
            f"{coordinates[1]:.6f} "
            f"{coordinates[2]:.6f} "
            f"{coordinates[3]:.6f}"
        )

    return converted_lines


def choose_split(index, total):
    train_end = int(total * TRAIN_RATIO)
    val_end = train_end + int(total * VAL_RATIO)

    if index < train_end:
        return "train"

    if index < val_end:
        return "val"

    return "test"


def main():
    random.seed(SEED)

    if OUTPUT_DIR.exists():
        print(f"حذف Dataset سابق: {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)

    create_output_directories()

    all_items = []

    for source_name, config in SOURCE_CONFIGS.items():
        source_items = find_source_items(source_name)

        print(
            f"{source_name}: "
            f"{len(source_items)} زوج صورة/Label صالح"
        )

        for image_path, label_path in source_items:
            all_items.append(
                (source_name, image_path, label_path, config["mapping"])
            )

    if not all_items:
        raise RuntimeError("لم يتم العثور على أي أزواج صورة/Label.")

    random.shuffle(all_items)

    class_counts = Counter()
    split_counts = Counter()

    for index, (source_name, image_path, label_path, mapping) in enumerate(
        all_items
    ):
        split = choose_split(index, len(all_items))

        safe_stem = (
            f"{source_name}__"
            f"{image_path.stem.replace(' ', '_')}"
        )

        image_suffix = image_path.suffix.lower()

        if image_suffix not in IMAGE_EXTENSIONS:
            image_suffix = ".jpg"

        output_image_name = safe_stem + image_suffix
        output_label_name = safe_stem + ".txt"

        destination_image = (
            OUTPUT_DIR / "images" / split / output_image_name
        )
        destination_label = (
            OUTPUT_DIR / "labels" / split / output_label_name
        )

        shutil.copy2(image_path, destination_image)

        converted_lines = convert_label(label_path, mapping)

        if not converted_lines:
            print(f"تحذير: Label فارغ أو غير صالح: {label_path}")
            destination_image.unlink(missing_ok=True)
            continue

        destination_label.write_text(
            "\n".join(converted_lines) + "\n",
            encoding="utf-8",
        )

        split_counts[split] += 1

        for line in converted_lines:
            class_id = int(line.split()[0])
            class_counts[class_id] += 1

    data_yaml = {
        "path": str(OUTPUT_DIR),
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        "nc": len(FINAL_NAMES),
        "names": [FINAL_NAMES[index] for index in range(len(FINAL_NAMES))],
    }

    yaml_path = OUTPUT_DIR / "data.yaml"
    yaml_path.write_text(
        yaml.safe_dump(
            data_yaml,
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )

    print("\nتم إنشاء Dataset النهائي بنجاح.")
    print(f"المسار: {OUTPUT_DIR}")
    print(f"عدد الصور حسب التقسيم: {dict(split_counts)}")
    print(f"عدد الكائنات حسب الفئة: {dict(sorted(class_counts.items()))}")
    print(f"ملف YAML: {yaml_path}")


if __name__ == "__main__":
    main()