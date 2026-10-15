from __future__ import annotations

from collections import defaultdict, deque
from math import hypot
from typing import DefaultDict, Deque


class SpeedEstimator:
    def __init__(
        self,
        fps: float,
        pixels_per_meter: float,
        history_size: int = 8,
    ) -> None:
        if fps <= 0:
            raise ValueError("fps must be greater than zero")

        if pixels_per_meter <= 0:
            raise ValueError("pixels_per_meter must be greater than zero")

        self.fps = fps
        self.pixels_per_meter = pixels_per_meter
        self.positions: DefaultDict[int, Deque[tuple[int, float, float]]] = (
            defaultdict(lambda: deque(maxlen=history_size))
        )

    def update(self, track_id: int, center_x: float, center_y: float, frame_number: int) -> float:
        history = self.positions[track_id]
        history.append((frame_number, center_x, center_y))

        if len(history) < 2:
            return 0.0

        first_frame, first_x, first_y = history[0]
        last_frame, last_x, last_y = history[-1]

        frame_delta = last_frame - first_frame
        if frame_delta <= 0:
            return 0.0

        pixel_distance = hypot(last_x - first_x, last_y - first_y)
        meters = pixel_distance / self.pixels_per_meter
        seconds = frame_delta / self.fps

        meters_per_second = meters / seconds
        return meters_per_second * 3.6