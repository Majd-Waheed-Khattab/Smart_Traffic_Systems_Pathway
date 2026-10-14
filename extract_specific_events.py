from pathlib import Path
import cv2


PROJECT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = PROJECT_DIR / "data" / "input" / "training_h264.mp4"
OUTPUT_DIR = PROJECT_DIR / "outputs" / "specific_events"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

if not VIDEO_PATH.exists():
    raise FileNotFoundError(f"الفيديو غير موجود: {VIDEO_PATH}")

cap = cv2.VideoCapture(str(VIDEO_PATH))

if not cap.isOpened():
    raise RuntimeError("تعذر فتح الفيديو.")

fps = cap.get(cv2.CAP_PROP_FPS)
if fps <= 0:
    raise RuntimeError("FPS غير صحيح.")

# القيم بعد تنقيص 4 دقائق
# 04:14 => 00:14
# 04:15 => 00:15
# 04:51 => 00:51
# 05:29 => 01:29
time_ranges = [
    ("ordinary_motorcycle", 12, 16),   # 00:12 إلى 00:16
    ("police_motorcycle", 13, 17),      # 00:13 إلى 00:17
    ("ordinary_motorcycle_2", 49, 53), # 00:49 إلى 00:53
    ("buses", 87, 91),                  # 01:27 إلى 01:31
]

for label, start_second, end_second in time_ranges:
    start_frame = int(start_second * fps)
    end_frame = int(end_second * fps)

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    current_frame = start_frame
    saved_index = 0

    while current_frame <= end_frame:
        success, frame = cap.read()
        if not success:
            break

        if (current_frame - start_frame) % 5 == 0:
            output_name = f"{label}_{saved_index:03d}.jpg"
            output_path = OUTPUT_DIR / output_name
            cv2.imwrite(str(output_path), frame)
            print(f"تم حفظ: {output_path}")
            saved_index += 1

        current_frame += 1

cap.release()
print("تم استخراج الإطارات الخاصة.")