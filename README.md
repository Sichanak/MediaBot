# MediaBot
سازماندهی هوشمند فیلم/سریال/انیمه و همچنین زیرنویس مربوط به همان در پوشه اختصاصی خودش


## فارسی

**مدیابات** یک اسکریپت هوشمند پایتون برای سازماندهی خودکار فایل‌های رسانه (فیلم/سریال و زیرنویس) است.

### ویژگی‌ها
- تشخیص خودکار سریال‌ها بر اساس نام فایل یا پوشه
- جداسازی فیلم‌ها و سریال‌ها در پوشه‌های `Movies` و `Series`
- پشتیبانی از الگوهای مختلف نام‌گذاری (مثل `S01E02`, `E16`, `01x02`)
- حالت پیش‌نمایش (Dry Run) بدون اعمال تغییرات واقعی
- قابلیت Undo کامل تمام عملیات
- پیکربندی با فایل `mediabot.json`
- جلوگیری از پردازش مجدد فایل‌های قبلاً سازماندهی‌شده

### نصب و استفاده
1. مسیر پیش فرض پوشه را میتوانید در فایل `mediabot.json` تغییر دهید.
2. اسکریپت را اجرا کنید:
   ```bash
   python mediabot.py
   ```
3. گزینه‌های پایانی:
   - `0`: خروج بدون انجام کاری
   - `1`: خروج + پاک‌سازی پوشه‌های خالی
   - `2`: Undo کامل تمام عملیات

### حالت پیش‌نمایش
```bash
python mediabot.py --dry-run
```

---

## English

**MediaBot** is a smart Python script for automatic organization of media files (videos and subtitles).

### Features
- Automatic TV show detection based on file/folder names
- Separates movies and TV shows into `Movies` and `Series` folders
- Supports various naming patterns (e.g., `S01E02`, `E16`, `01x02`)
- Dry run mode without making actual changes
- Full undo capability for all operations
- Configurable via `mediabot.json` file
- Prevents reprocessing of already organized files

### Installation & Usage
1. You can change default directory path `mediabot.json` in file.
2. Run the script:
   ```bash
   python mediabot.py
   ```
3. Final options:
   - `0`: Exit without doing anything
   - `1`: Exit and clean up empty folders
   - `2`: Undo all operations

### Dry Run Mode
```bash
python mediabot.py --dry-run
```
