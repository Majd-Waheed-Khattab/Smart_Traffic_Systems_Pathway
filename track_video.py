from pathlib import Path
from ultralytics import YOLO


MODEL_PATH = Path(
    "runs/detect/runs/vehicle_yolo11n_final/weights/best.pt"
)

VIDEO_PATH = Path("data/input/training_h264.mp4")

model = YOLO(str(MODEL_PATH))

results = model.track(
    source=str(VIDEO_PATH),
    device="cpu",
    tracker="bytetrack.yaml",
    conf=0.25,
    imgsz=320,
    vid_stride=2,
    stream=True,
    save=True,
    project="outputs",
    name="vehicle_yolo11n_final_track_stream",
    exist_ok=True,
    verbose=True,
)

for frame_number, result in enumerate(results, start=1):
    if frame_number % 100 == 0:
        print(
            f"تمت معالجة {frame_number} إطارًا "
            f"من الإطارات المعالجة",
            flush=True,
        )

    # اطبع ملخص الكشف الحالي كل 100 إطار
    if frame_number % 100 == 0:
        print(f"الكشف: {result.verbose()}", flush=True)

print("تمت معالجة الفيديو بنجاح.", flush=True)