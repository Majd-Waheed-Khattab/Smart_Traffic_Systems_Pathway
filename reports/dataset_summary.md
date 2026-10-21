# Dataset summary

- Images copied: **19834**
- Labels copied: **19834**
- Skipped files: **74214**

| Split | Images | Labels |
|---|---:|---:|
| train | 15864 | 15864 |
| val | 1987 | 1987 |
| test | 1983 | 1983 |

| Class | Count |
|---|---:|
| bus | 7870 |
| motorcycle | 25726 |
| car | 56774 |
| van | 7203 |
| truck | 4740 |
| motorcycle_traffic_police | 109 |

## Class mappings

- `Traffic surveillance system.v1i.yolov8`: bus->bus, car->car, motorbike->motorcycle, truck->truck
- `car detection 1.v1i.yolov8`: ambulance->SKIP, big car->car, car tracking 1->car, police car->car
- `police_motorcycles`: motorcycle_traffic_police->motorcycle_traffic_police
- `roboflow_01`: vehicle->car
- `roboflow_02`: bicycle->SKIP, bus->bus, car->car, motorcycle->motorcycle, person->SKIP, train->SKIP, truck->truck
- `roboflow_03`: Bus->bus, Car->car, Motorcycle->motorcycle, Taxi->car, Truck->truck, Van->van
- `roboflow_04`: 0->SKIP, 1->SKIP, 2->SKIP, 3->SKIP, 4->SKIP, 5->SKIP
- `roboflow_05`: bus->bus, car->car, motorcycle->motorcycle, pickup->van, truck->truck, van->van
- `roboflow_06`: bus->bus, car->car, microbus->van, motorbike->motorcycle, pickup-van->van, truck->truck
- `roboflow_07`: Bus->bus, Car->car, Van->van
- `roboflow_08`: bus-close->bus, bus-day->bus, bus-night->bus, car-close->car, car-day->car, car-night->car, motorcycle-close->motorcycle, motorcycle-day->motorcycle, motorcycle-night->motorcycle, pedestrian->SKIP, truck-close->truck, truck-day->truck, truck-night->truck
- `traffic.v1i.yolov8`: bus->bus, car->car, motor->motorcycle, truck->truck
