# Video comparison

Both models were run on `data/input/training_h264.mp4` with the same
`inference_video.py` command settings and `--vid-stride 2`. The video counts
below are operational tracking observations, not formal accuracy metrics.

| Model | Processed frames | Detection instances | Unique tracks | Violations |
|---|---:|---:|---:|---:|
| Baseline | 3750 | 25352 | 1101 | 919 |
| Improved | 3750 | 2142 | 95 | 67 |

| Model | Output video | Statistics JSON |
|---|---|---|
| Baseline | `outputs/inference/baseline_tracked_video.mp4` | `outputs/inference/baseline_statistics.json` |
| Improved | `outputs/inference/improved_tracked_video.mp4` | `outputs/inference/improved_statistics.json` |

Both output videos were readable as 1280x720 MP4 files with 3750 frames at
12.5 FPS, and both JSON files parsed successfully. The lower improved-model
counts are not evidence of better accuracy; the test-set metrics are the
decision criterion.
