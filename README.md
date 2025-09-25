# MediaBot
سازماندهی هوشمند فیلم/سریال/انیمه و همچنین زیرنویس مربوط به همان در پوشه اختصاصی خودش

![MediaBot](MediaBot.png)

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
1. پکیج گیت را نصب کنید (اگر قبلا نصب نکرده‌اید)
 ```bash
   python mediabot.py
   ```  
2. دستور زیر را کپی و اجرا کنید تا مدیابات کلون شود
   ```bash
    git clone https://github.com/Sichanak/MediaBot
   ```
3. مسیر پیش فرض پوشه را میتوانید در فایل `mediabot.json` تغییر دهید.
4. اسکریپت را اجرا کنید:
   ```bash
   python mediabot.py
   ```
 گزینه‌های پایانی اسکریپت:
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
1. Install Git pkg if you didn't
   ```bash
    pkg install git
   ```
2. Run to clone MediaBot code
   ```bash
    git clone https://github.com/Sichanak/MediaBot
   ```
3. You can change default directory path `mediabot.json` in file
   but it's not necessary because while running code it will ask you again.
4. Run the script:
   ```bash
   python mediabot.py
   ```
4. Final options:
   - `0`: Exit without doing anything
   - `1`: Exit and clean up empty folders
   - `2`: Undo all operations

### Dry Run Mode
```bash
python mediabot.py --dry-run
```
