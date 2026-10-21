# Model comparison

| Model | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|
| baseline | 0.4017 | 0.3513 | 0.2911 | 0.1741 |
| improved | 0.7692 | 0.6904 | 0.7574 | 0.5020 |

## Per-class metrics

### baseline

| Class | Precision | Recall | mAP50-95 |
|---|---:|---:|---:|
| car | 0.4089 | 0.4620 | 0.2186 |
| van | 0.3726 | 0.2469 | 0.1193 |
| bus | 0.3344 | 0.4369 | 0.2036 |
| truck | 0.3492 | 0.2574 | 0.1870 |
| motorcycle | 0.5432 | 0.3532 | 0.1418 |
| motorcycle_traffic_police | n/a | n/a | 0.1741 |
### improved

| Class | Precision | Recall | mAP50-95 |
|---|---:|---:|---:|
| car | 0.7666 | 0.7041 | 0.5044 |
| van | 0.7319 | 0.6085 | 0.4330 |
| bus | 0.8092 | 0.7712 | 0.6000 |
| truck | 0.7501 | 0.6911 | 0.5664 |
| motorcycle | 0.7882 | 0.6770 | 0.4059 |
| motorcycle_traffic_police | n/a | n/a | 0.5020 |
