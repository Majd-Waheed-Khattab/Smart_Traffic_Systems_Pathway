from pathlib import Path

from ultralytics import YOLO


IMAGE_PATH = Path("/home/majd/2016_7_4_12_45_23_816.jpg")

if not IMAGE_PATH.exists():
    raise FileNotFoundError(f"Image not found: {IMAGE_PATH}")

print("Loading YOLO11n...")
model = YOLO("yolo11n.pt")

print("Running detection on CPU...")
results = model.predict(
    source=str(IMAGE_PATH),
    device="cpu",
    conf=0.25,
    save=True,
    project="outputs",
    name="image_detection",
    exist_ok=True,
)

print("Detection completed successfully")
print("Output folder: outputs/image_detection")
