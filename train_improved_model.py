from __future__ import annotations

import os
from pathlib import Path

from ultralytics import YOLO


def main() -> None:
    device = "cuda:0" if os.environ.get("CUDA_VISIBLE_DEVICES", "") not in {"", "-1"} else "cpu"
    model = YOLO("yolo11n.pt")
    model.train(
        data="data/dataset/data.yaml",
        epochs=3,
        imgsz=320,
        batch=16 if device == "cpu" else -1,
        workers=2,
        patience=2,
        device=device,
        project=".",
        name="vehicle_yolo11n_improved",
        exist_ok=True,
        pretrained=True,
        plots=True,
        fraction=0.25 if device == "cpu" else 1.0,
        verbose=True,
    )


if __name__ == "__main__":
    main()
