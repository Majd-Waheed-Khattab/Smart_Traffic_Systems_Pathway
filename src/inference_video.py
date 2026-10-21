from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import cv2
from ultralytics import YOLO

from speed_logic import SpeedEstimator
from violation_config import (
    INFO_COLOR,
    NORMAL_COLOR,
    PIXELS_PER_METER,
    SPEED_LIMIT_KMH,
    VIOLATION_COLOR,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = PROJECT_ROOT / "models/best_continued.pt"
DEFAULT_VIDEO = PROJECT_ROOT / "data/input/training_h264.mp4"
DEFAULT_OUTPUT_VIDEO = PROJECT_ROOT / "outputs/inference/training_h264_result.mp4"
DEFAULT_OUTPUT_STATS = PROJECT_ROOT / "outputs/inference/training_h264_statistics.json"
SPEED_HISTORY_SIZE = 8


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Video inference with tracking and speed violations."
    )
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument(
        "--output-video", type=Path, default=DEFAULT_OUTPUT_VIDEO
    )
    parser.add_argument(
        "--output-stats", type=Path, default=DEFAULT_OUTPUT_STATS
    )
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--imgsz", type=int, default=320)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--tracker", default="bytetrack.yaml")
    parser.add_argument("--vid-stride", type=int, default=1)
    return parser.parse_args()


def get_class_name(names: Any, class_id: int) -> str:
    if isinstance(names, dict):
        return str(names.get(class_id, class_id))
    if isinstance(names, (list, tuple)) and 0 <= class_id < len(names):
        return str(names[class_id])
    return str(class_id)


def draw_text(
    frame: Any,
    text: str,
    position: tuple[int, int],
    color: tuple[int, int, int],
    scale: float = 0.6,
) -> None:
    cv2.putText(
        frame,
        text,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        2,
        cv2.LINE_AA,
    )


def validate_args(args: argparse.Namespace) -> None:
    if not args.model.is_file():
        raise FileNotFoundError(f"Model not found: {args.model}")
    if not args.video.is_file():
        raise FileNotFoundError(f"Video not found: {args.video}")
    if not 0.0 <= args.conf <= 1.0:
        raise ValueError("--conf must be between 0 and 1")
    if args.imgsz <= 0:
        raise ValueError("--imgsz must be greater than zero")
    if args.vid_stride < 1:
        raise ValueError("--vid-stride must be at least 1")


def main() -> None:
    args = parse_args()
    validate_args(args)

    args.output_video.parent.mkdir(parents=True, exist_ok=True)
    args.output_stats.parent.mkdir(parents=True, exist_ok=True)

    capture = cv2.VideoCapture(str(args.video))
    if not capture.isOpened():
        raise RuntimeError(f"Could not open video: {args.video}")

    source_fps = capture.get(cv2.CAP_PROP_FPS)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    input_frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    capture.release()

    if source_fps <= 0:
        source_fps = 25.0
    if width <= 0 or height <= 0:
        raise RuntimeError("Could not determine video dimensions.")

    effective_fps = source_fps / args.vid_stride
    writer = cv2.VideoWriter(
        str(args.output_video),
        cv2.VideoWriter_fourcc(*"mp4v"),
        effective_fps,
        (width, height),
    )
    if not writer.isOpened():
        raise RuntimeError(f"Could not create output video: {args.output_video}")

    estimator = SpeedEstimator(
        fps=effective_fps,
        pixels_per_meter=PIXELS_PER_METER,
        history_size=SPEED_HISTORY_SIZE,
    )
    all_ids: set[int] = set()
    violation_ids: set[int] = set()
    max_speed_by_id: dict[int, float] = {}
    detection_count_by_class: Counter[str] = Counter()
    unique_ids_by_class: defaultdict[str, set[int]] = defaultdict(set)
    processed_frames = 0
    total_detection_instances = 0

    print(f"Loading model: {args.model}")
    model = YOLO(str(args.model))
    print("Starting video inference and tracking...")

    try:
        results = model.track(
            source=str(args.video),
            stream=True,
            persist=True,
            tracker=args.tracker,
            conf=args.conf,
            imgsz=args.imgsz,
            device=args.device,
            vid_stride=args.vid_stride,
            verbose=False,
        )

        for processed_frames, result in enumerate(results, start=1):
            frame = result.plot()
            boxes = result.boxes
            ids = boxes.id.int().cpu().tolist() if boxes.id is not None else []
            class_ids = boxes.cls.int().cpu().tolist() if boxes.cls is not None else []
            coordinates = boxes.xyxy.cpu().tolist()
            names = getattr(result, "names", model.names)
            total_detection_instances += len(coordinates)

            for index, (x1, y1, x2, y2) in enumerate(coordinates):
                class_id = class_ids[index] if index < len(class_ids) else -1
                class_name = get_class_name(names, class_id)
                detection_count_by_class[class_name] += 1
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                track_id = ids[index] if index < len(ids) else None
                speed = 0.0

                if track_id is not None:
                    all_ids.add(track_id)
                    unique_ids_by_class[class_name].add(track_id)
                    speed = estimator.update(
                        track_id, center_x, center_y, processed_frames
                    )
                    max_speed_by_id[track_id] = max(
                        speed, max_speed_by_id.get(track_id, 0.0)
                    )
                    if speed > SPEED_LIMIT_KMH:
                        violation_ids.add(track_id)

                color = VIOLATION_COLOR if speed > SPEED_LIMIT_KMH else NORMAL_COLOR
                label = f"{class_name} {speed:.1f} km/h"
                if track_id is not None:
                    label = f"ID {track_id} | {label}"
                draw_text(frame, label, (int(x1), max(20, int(y1) - 8)), color)

            draw_text(
                frame,
                f"Frame: {processed_frames} | Violations: {len(violation_ids)}",
                (10, 25),
                INFO_COLOR,
            )
            writer.write(frame)

    finally:
        writer.release()

    statistics = {
        "input_video": str(args.video),
        "output_video": str(args.output_video),
        "source_fps": source_fps,
        "effective_fps": effective_fps,
        "input_frame_count": input_frame_count,
        "processed_frames": processed_frames,
        "total_detection_instances": total_detection_instances,
        "unique_tracks": len(all_ids),
        "violations": len(violation_ids),
        "speed_limit_kmh": SPEED_LIMIT_KMH,
        "pixels_per_meter": PIXELS_PER_METER,
        "detections_by_class": dict(detection_count_by_class),
        "unique_tracks_by_class": {
            name: len(track_ids)
            for name, track_ids in unique_ids_by_class.items()
        },
        "max_speed_by_track": {
            str(track_id): round(speed, 2)
            for track_id, speed in max_speed_by_id.items()
        },
    }
    args.output_stats.write_text(
        json.dumps(statistics, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Saved video: {args.output_video}")
    print(f"Saved statistics: {args.output_stats}")


if __name__ == "__main__":
    main()
