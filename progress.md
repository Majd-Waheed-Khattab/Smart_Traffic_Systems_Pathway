## Video inference and tracking

- Model: `models/best.pt`
- Input video: `data/input/training_h264.mp4`
- Processed frames: 7500
- Resolution: 1280x720
- FPS: 25
- Output video: `outputs/inference/tracked_video.mp4`
- Statistics: `outputs/inference/statistics.json`
- Unique tracker IDs: 1199

### Detection instances by class

- Car: 49,899
- Truck: 4,409
- Bus: 377
- Motorcycle: 21
- Van: 31

### Unique IDs by class

- Car: 1,113
- Truck: 150
- Bus: 44
- Motorcycle: 1
- Van: 12

Note: detection-instance counts represent appearances across frames, while unique vehicle counts represent tracker IDs.