# Model comparison

| Model | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|
| baseline | 0.4017 | 0.3513 | 0.2911 | 0.1741 |
| improved | 0.4316 | 0.3162 | 0.2702 | 0.1519 |

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
| car | 0.5342 | 0.5448 | 0.2833 |
| van | 0.5210 | 0.0491 | 0.0579 |
| bus | 0.2835 | 0.3838 | 0.1547 |
| truck | 0.2724 | 0.3327 | 0.1405 |
| motorcycle | 0.5467 | 0.2704 | 0.1233 |
| motorcycle_traffic_police | n/a | n/a | 0.1519 |
