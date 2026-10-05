from pathlib import Path
import cv2

PROJECT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = PROJECT_DIR / "data" / "input" / "training_h264.mp4"
SAMPLE_DIR = PROJECT_DIR / "outputs" / "video_samples"

SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

if not VIDEO_PATH.exists():
    raise FileNotFoundError(f"الفيديو غير موجود: {VIDEO_PATH}")

cap = cv2.VideoCapture(str(VIDEO_PATH))

if not cap.isOpened():
    raise RuntimeError("تعذر فتح الفيديو.")

fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = total_frames / fps if fps > 0 else 0

print("===== معلومات الفيديو =====")
print(f"المسار: {VIDEO_PATH}")
print(f"FPS: {fps}")
print(f"العرض: {width}")
print(f"الارتفاع: {height}")
print(f"إجمالي الإطارات: {total_frames}")
print(f"المدة: {duration:.2f} ثانية")
print(f"المدة: {duration / 60:.2f} دقيقة")

positions = [0.0, 0.25, 0.50, 0.75, 0.99]

for i, pos in enumerate(positions, start=1):
    target_frame = int(total_frames * pos)
    cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
    success, frame = cap.read()
    if success:
        out = SAMPLE_DIR / f"sample_{i}.jpg"
        cv2.imwrite(str(out), frame)
        print(f"تم حفظ: {out}")

cap.release()
print("تم إنهاء فحص الفيديو بنجاح.")