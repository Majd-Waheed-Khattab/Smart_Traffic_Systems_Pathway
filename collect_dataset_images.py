from pathlib import Path
import shutil


PROJECT_DIR = Path(__file__).resolve().parent

SOURCE_DIRS = [
    PROJECT_DIR / "outputs" / "specific_events",
    PROJECT_DIR / "outputs" / "motorcycle_review",
    PROJECT_DIR / "outputs" / "van_review",
    PROJECT_DIR / "outputs" / "van_motorcycle_review",
]

DESTINATION_DIR = (
    PROJECT_DIR
    / "data"
    / "dataset"
    / "images"
    / "unlabeled"
)

DESTINATION_DIR.mkdir(parents=True, exist_ok=True)

copied_count = 0

for source_dir in SOURCE_DIRS:
    if not source_dir.exists():
        print(f"المجلد غير موجود، سيتم تجاهله: {source_dir}")
        continue

    source_name = source_dir.name

    image_paths = sorted(source_dir.glob("*.jpg"))

    for image_path in image_paths:
        new_name = f"{source_name}_{image_path.name}"
        destination_path = DESTINATION_DIR / new_name

        shutil.copy2(image_path, destination_path)

        copied_count += 1
        print(f"تم نسخ: {destination_path.name}")


print()
print(f"انتهى الجمع.")
print(f"عدد الصور المنسوخة: {copied_count}")
print(f"المجلد النهائي: {DESTINATION_DIR}")