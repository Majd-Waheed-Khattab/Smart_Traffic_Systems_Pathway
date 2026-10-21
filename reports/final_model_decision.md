# Final model decision

## Selected model

`models/best.pt` remains the selected final model. It is the original model,
preserved unchanged after the improvement experiment.

## Evidence

Both models were evaluated on the exact same `data/dataset/data.yaml` test
split:

| Metric | Original baseline | Improved experiment |
|---|---:|---:|
| Precision | 0.4017 | 0.4316 |
| Recall | 0.3513 | 0.3162 |
| mAP50 | 0.2911 | 0.2702 |
| mAP50-95 | 0.1741 | 0.1519 |

The improved model increased precision by 0.0299, but regressed recall by
0.0351, mAP50 by 0.0210, and mAP50-95 by 0.0221. Because the important
overall detection metrics regressed, the improved model was rejected.

## Preserved artifacts

- Baseline backup: `models/best_before_improvement.pt`
- Rejected experiment: `models/best_improved.pt`
- Detailed metrics: `reports/model_comparison.json`
- Video comparison: `reports/video_comparison.md`

## Limitations

The improved experiment was trained for 3 epochs on 25% of the training
images because this CPU-only machine required more than 17 minutes for the
first attempted full-data epoch. The result is therefore a bounded experiment,
not evidence that longer or GPU training could not improve the model.
The police-motorcycle class has only 109 mapped annotations and the baseline
has no reliable precision/recall for that class on this test split.
