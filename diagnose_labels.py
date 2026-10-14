from pathlib import Path
from collections import Counter


PROJECT_DIR = Path(__file__).resolve().parent
SOURCES_DIR = PROJECT_DIR / "data" / "source_datasets"

SOURCE_NAMES = [
    "roboflow_03",
    "roboflow_05",
    "police_motorcycles",
]


def inspect_source(source_name):
    source_dir = SOURCES_DIR / source_name

    label_paths = [
        path
        for path in source_dir.rglob("*.txt")
        if path.is_file() and "labels" in path.parts
    ]

    empty_files = []
    field_counts = Counter()
    invalid_class_ids = []
    valid_detection_files = 0

    for label_path in label_paths:
        text = label_path.read_text(
            encoding="utf-8",
            errors="replace",
        ).strip()

        if not text:
            empty_files.append(label_path)
            continue

        file_is_valid = True

        for line_number, line in enumerate(text.splitlines(), start=1):
            parts = line.split()
            field_counts[len(parts)] += 1

            if len(parts) != 5:
                file_is_valid = False
                continue

            try:
                class_id = int(parts[0])
                coordinates = [float(value) for value in parts[1:]]
            except ValueError:
                file_is_valid = False
                continue

            if not all(0 <= value <= 1 for value in coordinates):
                file_is_valid = False

            if source_name == "police_motorcycles" and class_id != 0:
                invalid_class_ids.append(
                    f"{label_path}:{line_number}: {class_id}"
                )

        if file_is_valid:
            valid_detection_files += 1

    print("\n" + "=" * 60)
    print(f"SOURCE: {source_name}")
    print(f"Total label files: {len(label_paths)}")
    print(f"Empty label files: {len(empty_files)}")
    print(f"Valid detection label files: {valid_detection_files}")
    print(f"Number of fields per line: {dict(field_counts)}")
    print(f"Invalid police class IDs: {len(invalid_class_ids)}")

    if empty_files:
        print("\nExamples of empty labels:")
        for path in empty_files[:10]:
            print(path)

    if invalid_class_ids:
        print("\nExamples of invalid class IDs:")
        for item in invalid_class_ids[:10]:
            print(item)


for source_name in SOURCE_NAMES:
    inspect_source(source_name)