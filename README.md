# 🚀 Universal Data Pipeline (منظومة معالجة البيانات الشاملة)

مشروع متكامل لهندسة ومعالجة البيانات (**ETL / ELT**) متعدد المصادر مبني باستخدام **Python** و **Pandas**، مصمم وفق مبادئ **الهندسة النظيفة (Clean Architecture)** وفصل المسؤوليات، دون الاعتماد على أطر ويب ثقيلة (بدون Flask أو FastAPI).

---

## 👥 فريق العمل (Team)

### **اسم الفريق:** |

| الرقم | اسم العضو                    | الدور والمسؤولية                                                 |
| :---: | :--------------------------- | :--------------------------------------------------------------- |
| **1** | **طه فؤاد الشاوش**           | قواعد الأعمال، قواعد البيانات والاختبارات (Validation & Storage) |
| **2** | **علي احمد الحوثي**          | توحيد الـ Schema، تنظيف البيانات والتحقق (Matching & Cleaning)   |
| **3** | **اكرم عبدالكريم علي لقمان** | هندسة البيانات وتطوير خط المعالجة (Pipeline & Ingestion)         |

---

## 🌟 نظرة عامة على المشروع (Overview)

تقوم المنظومة باستيعاب البيانات من مصادر غير متجانسة (ملفات، قواعد بيانات علائقية وغير علائقية، واجهات برمجية، وتجريف ويب)، ثم اكتشاف هياكلها (Schema Discovery)، وتوحيد الحقول المشتركة دلالياً (Semantic Matching)، وحفظ نسخة خام غير معدلة (Raw/Landing Layer) في SQLite للتدقيق والاسترجاع، ثم تنظيف البيانات وتطبيق قواعد تحقق صارمة (**Business Rules**) وحفظ البيانات الصالحة في **MongoDB** وتصدير ملفات تقارير للأخطاء المكتشفة مع تتبع مصدر وتاريخ المعالجة (**Data Lineage**).

---

## 🏗️ المخطط المعماري للـ Pipeline

```text
 ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
 │     CSV      │   │  PostgreSQL  │   │   MongoDB    │   │   REST API   │   │ Web Scraping │
 │ (Customers / │   │(Netflix/Prod/│   │  (Students)  │   │ (sample_api) │   │   (Books)    │
 │   Orders)    │   │  Customers)  │   │              │   │              │   │              │
 └──────┬───────┘   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
        │                  │                  │                  │                  │
        └──────────────────┼──────────────────┼──────────────────┼──────────────────┘
                           ▼
               1. محولات المصادر (Source Adapters)
                           │
                           ▼
               2. فحص واكتشاف الـ Schema (Schema Discovery)
                  (تخزين كتالوج الهيكل في جدول schema)
                           │
                           ▼
               3. مطابقة وتجميع الجداول (Semantic Schema Matcher)
                  (دمج الجداول المتشابهة بناءً على دلالات الأعمدة)
                           │
                           ▼
               4. طبقة الهبوط الخام (Raw Landing Store - SQLite)
                  (حفظ البيانات الأصلية كما هي في data/raw/raw.db)
                           │
                           ▼
               5. تنظيف وتوحيد البيانات (Pandas Cleaner & Normalizer)
                  (معالجة الفراغات، تحويل الأنواع، إزالة التكرار، ملء القيم المفقودة)
                           │
                           ▼
               6. محرك قواعد الأعمال (Configurable Validation Engine)
                  (Required Columns, Allowed Values, Numeric Ranges, Regex)
                           ├──► [أخطاء التحقق] ──► حفظ data/processed/{table}_errors.csv
                           ▼
               7. طبقة البيانات المعالجة والخط الزمني (Processed Layer)
                  (إضافة _ingested_at, _source, _pipeline_version)
                           │
                           ▼
               ┌──────────────────────────────────────────────┐
               │ MongoDB Database (Collections) & CSV Exports │
               └──────────────────────────────────────────────┘
```

---

## 🔌 المصادر المدعومة في هذه النسخة

1. **ملفات CSV**:
   - قراءة مصادر متعددة وتوحيد الجداول المشابهة مثل `customers_a.csv` و `customers_b.csv` رغم اختلاف أسماء الحقول (`customer_id` مقابل `id`، و `name` مقابل `full_name`).
   - ملف `orders.csv` لاختبار الطلبات والمعاملات المالية.
2. **قواعد بيانات PostgreSQL**:
   - استخراج الجداول عبر `information_schema` تلقائياً واسترجاع البيانات عبر محول `PostgreSQLSource`.
3. **قواعد بيانات NoSQL (MongoDB Source)**:
   - قراءة الـ Collections وتحويل الوثائق المتداخلة (`nested documents`) إلى جداول مسطحة عبر `pd.json_normalize` والتعامل الآمن مع `_id`.
4. **واجهات REST API**:
   - جلب بيانات حية من روابط JSON (مثل JSONPlaceholder Users) مع معالجة استثناءات الاتصال والتجاوز التلقائي عند انقطاع الإنترنت.
5. **تجريف الويب (Web Scraping)**:
   - استخراج بيانات المواقع باستخدام `BeautifulSoup` (مثل أسعار وتوفر الكتب من Books to Scrape).

> **قابلية التوسع (Extensibility):** التصميم يعتمد كلياً على نمط **Adapter Pattern**؛ لذلك يمكن إضافة أي محرك جديد (مثل MySQL, Oracle, SQL Server, Parquet, Kafka) بإضافة كلاس Adapter دون لمس أي سطر في مراحل التنظيف أو التحقق أو التخزين.

---

## 🛠️ مراحل المعالجة (Pipeline Lifecycle)

### 1. اكتشاف ومطابقة الـ Schema (Schema Discovery & Matching)

- فحص كل حقل: النوع البرمجي (`pandas_dtype`)، إمكانية قبول قيم فارغة (`nullable`)، عدد القيم الفارغة (`null_count`)، والقيم الفريدة وموقع العمود.
- توحيد المترادفات الدلالية في `SchemaMatcher.SYNONYMS`، مثل:
  - `id`, `customer_id`, `client_id`, `user_id` ⬅️ `identifier`
  - `name`, `full_name`, `customer_name` ⬅️ `name`
  - `email`, `email_address` ⬅️ `email`
  - `amount`, `total`, `price` ⬅️ `amount`
  - `date`, `created_at`, `order_date` ⬅️ `date`
- حساب نسبة التشابه بين الجداول (`table_similarity`) ودمج الجداول المتشابهة بنسبة تتجاوز الحد الأدنى المسموح به (`min_table_similarity`).

### 2. طبقة الهبوط الخام (Raw SQLite Store)

- يتم حفظ جميع البيانات الخام في `data/raw/raw.db` مع تحويل الهياكل المعقدة (`list`, `dict`) إلى نصوص JSON آمنة.
- حفظ كتالوج الهياكل الكامل في جدول `schema` داخل SQLite للرجوع إليه وتدقيق التغييرات.

### 3. التنظيف والتوحيد (Cleaning & Normalization)

- تنظيف المسافات الزائدة للنصوص (`strip_strings`).
- تحويل تمثيلات القيم الفارغة النصية (`""`, `"null"`, `"NULL"`, `"N/A"`, `"not_available"`, `"unknown"`) إلى `pd.NA`.
- تحويل الأعمدة الرقمية والتواريخ قسرياً (`pd.to_numeric`, `pd.to_datetime`) مع تحويل القيم التالفة إلى Null.
- إزالة الصفوف المكررة بالكامل (`drop_duplicates`).
- ملء القيم الرقمية الفارغة بالوسيط الحسابي (`median`)، والقيم النصية بالقيمة الافتراضية المحددة في الإعدادات (`string_fill: "Unknown"`).

### 4. قواعد الأعمال والتحقق (Business Rules Engine)

تُدار قواعد التحقق مركزياً عبر ملف الإعدادات (`config/pipeline_config.json` أو `config/pipeline.json`) دون أي تعديل في الكود البرمجي:

- **`required_columns`**: التأكد من وجود الحقول الأساسية والإلزامية لكل جدول.
- **`allowed_values`**: حصر القيم المسموحة لحقول التصنيف أو الحالة (مثل `orders.status` أو `netflix_shows.type`).
- **`ranges`**: تحديد الحدود الدنيا والقصوى للقيم الرقمية (مثل الأعمار، المبالغ المالية، المعدل الجامعي GPA، ونسب الحضور).
- **`regex`**: التحقق من التنسيقات باستخدام التعابير القياسية (مثل صحة البريد الإلكتروني، وتنسيق التواريخ).
- **ملفات الأخطاء**: أي صف ينتهك قاعدة يتم عزله وتسجيله في ملف `data/processed/{table}_errors.csv` مع تحديد السطر والحقل ونوع الخطأ بدقة.

### 5. تخزين البيانات وتتبع المسار (Processed Storage & Lineage)

- حفظ البيانات المعالجة والنظيفة في قاعدة بيانات **MongoDB** المخصصة للبيانات الجاهزة.
- تصدير نسخة نهائية كملفات CSV في مجلد `data/processed/`.
- إضافة أعمدة تتبع المصدر والنسخة تلقائياً لكل صف:
  - `_ingested_at`: التوقيت الزمني لعملية الاستيراد (UTC).
  - `_source`: المصدر الأصلي للبيانات (مثل `csv`, `postgresql`, `mongodb`, `web`, `api`).
  - `_pipeline_version`: رقم إصدار منظومة البيانات (مثل `1.0.0`).

---

## ⚙️ إعدادات قواعد الأعمال (`config/pipeline_config.json`)

فيما يلي القواعد المطبقة فعلياً حسب بيانات التنفيذ في المشروع:

```json
{
  "sqlite_path": "data/raw/raw.db",
  "mongo_database": "processed_data",
  "matching": {
    "min_table_similarity": 0.7
  },
  "cleaning": {
    "drop_duplicates": true,
    "strip_strings": true,
    "empty_strings_to_null": true,
    "string_fill": "Unknown"
  },
  "validation": {
    "required_columns": {
      "customers_a": ["identifier", "name", "email"],
      "customers": ["identifier", "name", "email", "status"],
      "orders": ["order_id", "identifier", "amount", "status", "date"],
      "students": ["student_id", "name"],
      "products": ["product_id", "product_name", "amount", "stock"],
      "netflix_shows": ["show_id", "type", "title"],
      "books": ["name", "availability"],
      "sample_api": ["identifier", "name", "email", "username"]
    },
    "allowed_values": {
      "customers_a.country": ["Yemen"],
      "customers.status": ["active", "inactive"],
      "orders.status": ["paid", "pending", "cancelled"],
      "students.city": ["Sanaa", "Ibb", "Taiz", "Dhamar", "Aden", "Unknown"],
      "netflix_shows.type": ["Movie", "TV Show"],
      "books.availability": ["In stock", "Out of stock"]
    },
    "ranges": {
      "customers_a.identifier": { "min": 1 },
      "customers_a.age": { "min": 18, "max": 100 },
      "customers.identifier": { "min": 1 },
      "customers.age": { "min": 18, "max": 100 },
      "orders.order_id": { "min": 1 },
      "orders.amount": { "min": 0.0 },
      "students.age": { "min": 17, "max": 60 },
      "students.attendance": { "min": 0.0, "max": 100.0 },
      "students.gpa": { "min": 0.0, "max": 4.0 },
      "students.academic_gpa": { "min": 0.0, "max": 4.0 },
      "students.academic_attendance": { "min": 0.0, "max": 100.0 },
      "products.amount": { "min": 0.0 },
      "products.stock": { "min": 0 },
      "netflix_shows.release_year": { "min": 1900, "max": 2030 },
      "sample_api.identifier": { "min": 1 }
    },
    "regex": {
      "customers_a.email": "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$",
      "customers.email": "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$",
      "orders.date": "^\\d{4}-\\d{2}-\\d{2}",
      "sample_api.email": "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$"
    }
  }
}
```

---

## 📁 هيكلية المجلدات والملفات (Project Structure)

```text
universal_data_pipeline_updated/
│
├── config/
│   ├── pipeline_config.json      # ملف الإعدادات وقواعد الأعمال الرئيسي
│   └── pipeline.json             # نسخة مطابقة لملف الإعدادات
│
├── data/
│   ├── sample/                   # البيانات التجريبية
│   │   ├── customers_a.csv       # بيانات عملاء مع قيم ناقصة وتكرار
│   │   ├── customers_b.csv       # بيانات عملاء بأسماء أعمدة مختلفة وقيم شاذة
│   │   └── orders.csv            # بيانات طلبات مع قيم نصية غير صالحة وتكرار
│   │
│   ├── raw/
│   │   └── raw.db                # قاعدة SQLite للبيانات الخام وكتالوج الـ Schema
│   │
│   └── processed/                # المخرجات المعالجة وتقارير الأخطاء
│       ├── customers_a.csv       # العملاء المدمجون والنظيفون
│       ├── orders.csv            # الطلبات النظيفة
│       ├── netflix_shows.csv     # بيانات عروض نتفليكس المعالجة
│       ├── books.csv             # بيانات الكتب المستخرجة من الويب
│       ├── students.csv          # بيانات الطلاب المستوردة من MongoDB
│       └── students_errors.csv   # تقرير الأخطاء المكتشفة في بيانات الطلاب
│
├── src/
│   ├── ingestion/                # محولات استيراد البيانات (Adapters)
│   │   ├── csv_source.py         # قراءة ملفات CSV
│   │   ├── postgres_source.py    # قراءة جداول PostgreSQL
│   │   ├── mongo_source.py       # قراءة MongoDB Collections وتسطيح الوثائق
│   │   ├── api_source.py         # قراءة واجهات REST API
│   │   └── web_source.py         # تجريف الويب عبر BeautifulSoup
│   │
│   ├── schema/                   # اكتشاف ومطابقة المخططات
│   │   ├── inspector.py          # فحص الحقول والأنواع والـ Nulls
│   │   └── matcher.py            # توحيد الأسماء والمترادفات وحساب التشابه
│   │
│   ├── transform/                # تحويل وتنظيف البيانات
│   │   ├── cleaner.py            # تنظيف الفراغات، ملء النواقص وإزالة التكرار
│   │   └── normalizer.py         # إعادة تسمية الأعمدة وفق المترادفات
│   │
│   ├── validation/               # محرك قواعد التحقق
│   │   └── rules.py              # فحص الحقول المطلوبة، النطاقات، القيم المسموحة و Regex
│   │
│   ├── storage/                  # التخزين والحفظ
│   │   ├── sqlite_store.py       # تخزين البيانات الخام والـ Schema في SQLite
│   │   └── mongo_store.py        # تخزين البيانات المعالجة في MongoDB
│   │
│   └── pipeline.py               # المنظم الرئيسي ومحرك التنفيذ (Pipeline Orchestration)
│
├── tests/                        # الاختبارات الآلية (Unit Tests)
│   ├── test_cleaner.py           # اختبار عمليات التنظيف
│   ├── test_matcher.py           # اختبار دقة المطابقة وتوحيد الأعمدة
│   ├── test_mongo_source.py      # اختبار قراءة مصادر MongoDB
│   └── test_rules.py             # اختبار قواعد الأعمال والتحقق
│
├── main.py                       # نقطة الانطلاق الرئيسية لتشغيل المشروع
├── requirements.txt              # الحزم والمكتبات المطلوبة
├── .env                          # متغيرات البيئة السرية ومنافذ الاتصال
└── README.md                     # التوثيق الشامل للمشروع
```

---

## 🚀 التثبيت والتشغيل (Installation & Quick Start)

### 1. إنشاء وتفعيل البيئة الافتراضية (Virtual Environment)

```bash
# إنشاء البيئة الافتراضية
python -m venv .venv
```

**على أنظمة Windows:**

```powershell
.venv\Scripts\activate
```

**على أنظمة Linux / macOS:**

```bash
source .venv/bin/activate
```

### 2. تثبيت المكتبات المطلوبة

```bash
pip install -r requirements.txt
```

### 3. ضبط متغيرات البيئة (`.env`)

قم بإنشاء ملف `.env` وضبط بيانات الاتصال الخاصة بك:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=netflix
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

MONGO_SOURCE_URI=mongodb://localhost:27017/
MONGO_SOURCE_DATABASE=university_ai

MONGO_URI=mongodb://localhost:27017/
MONGO_DATABASE=processed_data
```

### 4. تشغيل خط معالجة البيانات (Run Pipeline)

يمكنك التشغيل إما عبر `main.py` أو كموديول بايثون:

```bash
python main.py
```

أو:

```bash
python -m src.pipeline
```

### 5. تشغيل الاختبارات الآلية (Run Automated Tests)

```bash
python -m pytest
```

---

## 📊 دراسة حالة من واقع التنفيذ الفعلي (Case Study)

أثناء تشغيل الـ Pipeline على البيانات الفعلية، قام النظام بالعمليات الآتية:

1. **استيعاب البيانات**: تحميل جداول من CSV و PostgreSQL و MongoDB و Web Scraping بنجاح.
2. **اكتشاف الهياكل**: فحص 42 عموداً عبر 6 جداول وتسجيل تفاصيل الهيكل في SQLite.
3. **تجميع الجداول**: دمج `customers_a` و `customers_b` وتوحيد مسميات الأعمدة إلى `identifier`, `name`, `email`, `age`, `country`.
4. **التنظيف الآلي**:
   - تحويل النص `not_available` في ملف العملاء إلى قيمة رقمية تم تعويضها بالوسيط (`29.0`).
   - إزالة الصف المكرر للطلب `1003`.
   - تحويل القيمة التالفة `invalid` في مبلغ الطلب إلى الوسيط (`32.75`).
5. **اكتشاف الشواذ في قواعد الأعمال (Validation Report)**:
   تم فحص جدول الطلاب (`students`) واكتشاف 3 مخالفات لقواعد العمل وتم تصديرها فوراً في `data/processed/students_errors.csv`:
   - **السطر 3 (الطالب 1005):** حقل `age` = `-5` ⬅️ خطأ `below_minimum` (العمر أقل من 17).
   - **السطر 4 (الطالب 1006):** حقل `attendance` = `105.0%` ⬅️ خطأ `above_maximum` (نسبة الحضور تتجاوز 100%).
   - **السطر 2 (الطالب 1004):** حقل `gpa` = `4.2` ⬅️ خطأ `above_maximum` (المعدل يتجاوز الحد الأقصى 4.0).

---

## 🏆 حقوق التطوير والملكية

تم تطوير هذا المشروع وتوثيقه بواسطة **فريق الأسطورة (The Legend)**:

- **طه فؤاد الشاوش**
- **اكرم عبدالكريم لقمان**
- **علي احمد الحوثي**

كافة الحقوق محفوظة © 2026.
