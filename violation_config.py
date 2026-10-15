from __future__ import annotations

# ألوان OpenCV بصيغة BGR
NORMAL_COLOR = (0, 255, 0)       # أخضر
VIOLATION_COLOR = (0, 0, 255)    # أحمر
TEXT_COLOR = (255, 255, 255)     # أبيض
INFO_COLOR = (255, 255, 0)       # أصفر

# يجب ضبط هذه القيمة حسب الفيديو والكاميرا.
# مثال: عدد البكسلات التي تعادل مترًا واحدًا.
PIXELS_PER_METER = 8.0

# السرعة القصوى المسموح بها
SPEED_LIMIT_KMH = 50.0

# عدد الإطارات المستخدمة لحساب السرعة
SPEED_HISTORY_SIZE = 8