# Smart Traffic Systems Pathway

## About

مشروع لاكتشاف وتتبع المركبات باستخدام YOLO11n، مع حفظ فيديو inference وإحصاءات أساسية عن المركبات، إضافة إلى تقدير تقريبي للسرعة وتمييز المركبات المتجاوزة لحد السرعة.

## فكرة المشروع

يستخدم المشروع نموذج YOLO11n مدربًا على مجموعة من فئات المركبات، ثم يطبّق النموذج على فيديو مروري لاكتشاف المركبات وتتبعها عبر الإطارات.

يشمل المشروع:

- اكتشاف المركبات.
- تصنيف المركبات حسب الفئة.
- تتبع المركبات باستخدام ByteTrack.
- إعطاء ID لكل مركبة أثناء التتبع.
- حفظ فيديو جديد يحتوي على النتائج.
- حساب عدد المركبات المكتشفة.
- حساب عدد المركبات حسب الفئة.
- حساب عدد المركبات الفريدة حسب ID.
- تقدير سرعة تقريبية للمركبات.
- تمييز المركبات المتجاوزة للسرعة باللون الأحمر.
- حفظ الإحصاءات في ملف JSON.

## الفئات المستخدمة

الفئات الأساسية في النموذج هي:

1. `car`
2. `van`
3. `bus`
4. `truck`
5. `motorcycle`
6. `motorcycle_traffic_police`

يمكن مراجعة الفئات في الملف:

```text
classes.txt
```

## متطلبات التشغيل

- Python 3
- بيئة افتراضية Python
- OpenCV
- PyTorch
- Ultralytics YOLO
- ByteTrack من خلال Ultralytics

يتم تثبيت المكتبات باستخدام:

```bash
pip install -r requirements.txt
```

## تفعيل البيئة الافتراضية

على Linux:

```bash
source .venv/bin/activate
```

## ملفات المشروع الأساسية

```text
models/best_continued.pt
```

النموذج النهائي المستخدم في inference. النموذج السابق للمقارنة محفوظ في
`models/best.pt`.

```text
src/inference_video.py
```

الملف الرئيسي لتشغيل النموذج على الفيديو، وإضافة التتبع والـ IDs والسرعة والألوان والإحصاءات.

```text
src/speed_logic.py
```

يحتوي على منطق تقدير السرعة اعتمادًا على حركة مركز المركبة بين الإطارات.

```text
src/violation_config.py
```

يحتوي على الألوان، حد السرعة، ومعامل معايرة البكسل إلى متر.

```text
train_yolo11n.py
```

يحتوي على إعدادات تدريب نموذج YOLO11n.

```text
classes.txt
```

يحتوي على أسماء الفئات.

```text
tests/test_libraries.py
```

يتحقق من إمكانية استيراد المكتبات الأساسية.

## تشغيل inference على الفيديو

يجب أن يكون النموذج موجودًا في:

```text
models/best_continued.pt
```

ويجب أن يكون فيديو الاختبار موجودًا في:

```text
data/input/training_h264.mp4
```

شغّل:

```bash
python src/inference_video.py \
  --model models/best_continued.pt \
  --video data/input/training_h264.mp4
```

يمكن تحديد مسارات أخرى:

```bash
python src/inference_video.py \
  --model models/best_continued.pt \
  --video data/input/training_h264.mp4 \
  --output-video outputs/inference/tracked_speed_video.mp4 \
  --output-stats outputs/inference/speed_statistics.json
```

## ملفات النتائج

بعد انتهاء التشغيل، يتم إنشاء:

```text
outputs/inference/tracked_speed_video.mp4
outputs/inference/speed_statistics.json
```

الفيديو الناتج لا يغيّر الفيديو الأصلي، بل ينشئ نسخة جديدة تحتوي على:

- مربعات حول المركبات.
- اسم الفئة.
- ID المركبة.
- السرعة التقريبية.
- اللون الأخضر للمركبات العادية.
- اللون الأحمر للمركبات المتجاوزة لحد السرعة.
- عدد المركبات الفريدة.
- عدد المخالفات.

لفتح الفيديو على Linux:

```bash
xdg-open outputs/inference/tracked_speed_video.mp4
```

لعرض الإحصاءات:

```bash
cat outputs/inference/speed_statistics.json
```

## الإحصاءات المحفوظة

يحتوي ملف JSON على معلومات مثل:

- عدد الإطارات المعالجة.
- عدد مرات الكشف لكل فئة.
- عدد المركبات الفريدة حسب ID.
- عدد المركبات الفريدة حسب الفئة.
- عدد المركبات المخالفة.
- IDs للمركبات المخالفة.
- أعلى سرعة لكل ID.
- حد السرعة المستخدم.
- معامل المعايرة.

يجب التفريق بين نوعين من العد:

### Detection instances

عدد مرات ظهور المركبات عبر جميع الإطارات. قد تظهر المركبة نفسها مئات المرات لأنها موجودة في عدة إطارات.

### Unique vehicles

عدد IDs الفريدة التي أنشأها نظام التتبع، وهو أقرب إلى عدد المركبات المستقلة.

## تقدير السرعة

يتم تقدير السرعة من خلال:

1. حساب مركز المركبة في كل إطار.
2. حساب المسافة التي قطعها المركز بالبكسل.
3. تحويل البكسل إلى متر باستخدام معامل المعايرة.
4. استخدام معدل إطارات الفيديو لحساب الزمن.
5. تحويل السرعة إلى كيلومتر في الساعة.

المعامل الحالي هو:

```python
PIXELS_PER_METER = 8.0
```

وحد السرعة الحالي هو:

```python
SPEED_LIMIT_KMH = 50.0
```

السرعة الناتجة تقريبية؛ لأن الحصول على سرعة واقعية يتطلب معرفة مسافة حقيقية داخل المشهد ومعايرة الكاميرا.

## الاختبارات

## تحسين البيانات والتدريب

تم فحص 12 مجموعة بيانات داخل `data/source_datasets`، ومنها أحدث ثلاث مجموعات:

- `Traffic surveillance system.v1i.yolov8`
- `car detection 1.v1i.yolov8`
- `traffic.v1i.yolov8`

أنتج التحضير dataset موحدًا في `data/dataset` يضم 19,834 صورة و19,834
label، موزعة إلى 15,864 train و1,987 validation و1,983 test. تم استخدام
تقسيم deterministic مع seed ثابت، وإزالة الصور المتطابقة وإبقاء مجموعات
الأسماء المتسلسلة داخل split واحد لتقليل تسرب إطارات الفيديو.

الفئات النهائية هي الفئات الست الموجودة في `classes.txt`. التحويلات
المستخدمة موثقة في `reports/dataset_summary.md`، وتشمل `motorbike` إلى
`motorcycle` و`microbus` إلى `van`. الفئات غير المتوافقة مثل `person` و
`bicycle` و`ambulance` لم تُحوّل إلى فئة مركبة بالتخمين، وسُجلت الملفات
المتأثرة في تقرير التحضير.

أدوات reproducible workflow:

```bash
python scripts/validate_datasets.py
python scripts/prepare_dataset.py
python train_improved_model.py
python scripts/evaluate_models.py
```

### مواصلة تدريب النموذج الحالي

تم ضبط [train_yolo11n.py](./train_yolo11n.py) ليحمّل النموذج الحالي
`models/best.pt` ثم يواصل تدريبه على البيانات الموجودة في
`data/dataset/data.yaml`. لا يتم استبدال النموذج الأصلي؛ إذ تحفظ نتيجة
التدريب في:

```text
models/best_continued.pt
```

لتشغيل التدريب:

```bash
source .venv/bin/activate
python train_yolo11n.py
```

هذا الأسلوب يبدأ تجربة تدريب جديدة بأوزان `models/best.pt` ويحفظ نموذجًا
مستقلًا للمقارنة، وليس استكمالًا لحالة optimizer من تجربة سابقة. وللمقارنة
في inference، شغّل نفس الفيديو مرة باستخدام كل نموذج:

```bash
python src/inference_video.py \
  --model models/best.pt \
  --video data/input/training_h264.mp4 \
  --output-video outputs/inference/baseline_tracked_video.mp4 \
  --output-stats outputs/inference/baseline_statistics.json

python src/inference_video.py \
  --model models/best_continued.pt \
  --video data/input/training_h264.mp4 \
  --output-video outputs/inference/continued_tracked_video.mp4 \
  --output-stats outputs/inference/continued_statistics.json
```

التقارير:

- `reports/dataset_validation_report.json` و`reports/dataset_validation_report.md`
- `reports/dataset_summary.json` و`reports/dataset_summary.md`
- `reports/model_comparison.json` و`reports/model_comparison.md`
- `reports/final_model_decision.md`
- `reports/video_comparison.md`

كانت مقاييس baseline على test هي precision **0.4017** وrecall **0.3513**
وmAP50 **0.2911** وmAP50-95 **0.1741**. أما experiment المحسّن فكانت
0.4316 و0.3162 و0.2702 و0.1519 على الترتيب؛ لذلك بقي
`models/best_continued.pt` هو النموذج النهائي. النموذج السابق للمقارنة هو
`models/best.pt`، والنسخ التجريبية هي `models/best_before_improvement.pt`
و`models/best_improved.pt`.

تم التحقق من النموذجين على الفيديو نفسه. النتائج موجودة في:

```text
outputs/inference/baseline_tracked_video.mp4
outputs/inference/improved_tracked_video.mp4
outputs/inference/baseline_statistics.json
outputs/inference/improved_statistics.json
```

عدادات الفيديو ليست مقياس دقة رسميًا. التتبع يستخدم ByteTrack، والـ IDs قد
تتغير عند فقد المركبة. السرعة تقريبية وتعتمد على `PIXELS_PER_METER = 8.0`
ومعايرة الكاميرا؛ اللون الأحمر يعني تجاوز `SPEED_LIMIT_KMH = 50.0` وفق هذا
التقدير فقط.

اختبار المكتبات:

```bash
python tests/test_libraries.py
```

فحص صحة ملفات Python:

```bash
python -m py_compile \
  src/inference_video.py \
  src/speed_logic.py \
  src/violation_config.py \
  train_yolo11n.py
```

## الملفات المستبعدة من Git

لا يجب رفع الملفات الكبيرة أو الملفات الناتجة مؤقتًا، مثل:

```text
.venv/
data/
runs/
outputs/
.git_backup/
*.mp4
*.avi
*.jpg
*.png
```

يتم الاحتفاظ بالنموذج النهائي فقط:

```text
models/best_continued.pt
```

ويتم رفعه باستخدام Git LFS.

## حدود المشروع

- تقدير السرعة تقريبي وليس قياسًا مروريًا رسميًا.
- قد يتغير ID إذا فقد المتتبع المركبة لعدة إطارات.
- قد تُحسب المركبة نفسها أكثر من مرة إذا فقدت ID ثم حصلت على ID جديد.
- جودة النتائج تعتمد على جودة الفيديو والإضاءة وموقع الكاميرا.
- التدريب تم باستخدام CPU، لذلك قد يكون التدريب وinference أبطأ من الأجهزة التي تحتوي على GPU.
- عدد مرات الكشف لا يساوي عدد المركبات الفريدة.

## حالة المشروع

المشروع النهائي يحتوي على:

- نموذج YOLO11n مدرب.
- inference للفيديو.
- تتبع للمركبات.
- IDs للمركبات.
- فيديو ناتج.
- إحصاءات JSON.
- تقدير سرعة تقريبي.
- تمييز للمخالفات.
- توثيق لطريقة التشغيل والنتائج.

## Documentation

### كيف عالجنا المشكلة

تم تحويل المشكلة إلى كشف وتصنيف للمركبات باستخدام YOLO11n، ثم استخدام
ByteTrack للحفاظ على هوية المركبة بين الإطارات. يحفظ النظام فيديوً موضحًا
عليه الصناديق والفئات وIDs، ويحسب إحصاءات الكشف والتتبع ويقدّر السرعة
تقريبيًا.

### البيانات ومصدرها

تم دمج 12 مجموعة بيانات مرورية متاحة للمشروع في مجموعة موحدة. بعد التحقق
وإزالة التكرارات وتقسيم البيانات، أصبحت المجموعة 19,834 صورة: 15,864
للتدريب، و1,987 للتحقق، و1,983 للاختبار. توجد تفاصيل التحضير والتحويلات في
`reports/dataset_summary.md` و`reports/dataset_validation_report.md`.

### التدريب وتكثير البيانات

بدأ التدريب من أوزان YOLO11n، ثم تمت مواصلة التدريب من `models/best.pt`.
استُخدمت 30 epoch، وصور بحجم 416، و`patience=8` للتوقف المبكر، وكان التدريب
على CPU. استخدمت Ultralytics عمليات augmentation الافتراضية، ومنها تغيير
الحجم، والتحويلات اللونية، والتكبير والتصغير، والإزاحة، والقلب الأفقي،
وMosaic.

### النتائج

تم تقييم النموذجين على نفس مجموعة الاختبار. حقق النموذج القديم
`models/best.pt` قيمًا مقدارها Precision=0.402 وRecall=0.351 وmAP50=0.291
وmAP50-95=0.174. حقق النموذج النهائي `models/best_continued.pt`
Precision=0.769 وRecall=0.690 وmAP50=0.757 وmAP50-95=0.502.
التفاصيل موجودة في `reports/continued_model_comparison.md`.

### المشاكل والتحديات

- اختلاف أسماء الفئات بين مصادر البيانات، وتم توحيدها في `classes.txt`.
- وجود صور متقاربة من فيديو واحد، لذلك استُخدم تقسيم ثابت لتقليل تسرب
  الإطارات بين مجموعات التدريب والاختبار.
- التدريب على CPU أبطأ من التدريب على GPU.
- انقطاع الكهرباء أثناء التدريب، ثم استُخدم `last.pt` لاستكمال التدريب.
- تقدير السرعة تقريبي ويتطلب معايرة حقيقية للكاميرا والمسافات.

### نقاط الضعف

- السرعة المقدرة ليست قياسًا مروريًا رسميًا.
- قد يتغير ID عند فقد المركبة لعدة إطارات.
- قد تُحسب المركبة نفسها أكثر من مرة إذا فقدت ID ثم حصلت على ID جديد.
- تعتمد النتائج على زاوية الكاميرا والإضاءة وجودة الفيديو.

### توزيع العمل


| عضو الفريق | المهمة |
|---|---|
| احمد زيتوني | تجهيز البيانات وتوحيد الفئات |
| مجد خطاب |,  التتبع، تقدير السرعة، ودمج النظام , الاختبار والتوثيق والعرض  تدريب النموذج وتقييمه |

### هيكلية المستودع

```text
src/                    # كود inference والتتبع والسرعة
models/                 # النموذج النهائي والنماذج المرجعية
scripts/                # تجهيز البيانات وتقييم النماذج
tests/                  # اختبارات المكتبات
train_yolo11n.py        # مواصلة تدريب النموذج
requirements.txt        # متطلبات Python
README.md               # التوثيق وطريقة التشغيل
```