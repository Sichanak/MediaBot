import os
import shutil
import re
import json
import sys

# رنگ‌های ANSI (فقط در ترمینال پشتیبانی‌شده)
USE_COLOR = sys.stdout.isatty()
YELLOW = "\033[33m" if USE_COLOR else ""
RED = "\033[31m" if USE_COLOR else ""
GREEN = "\033[32m" if USE_COLOR else ""
CYAN = "\033[36m" if USE_COLOR else ""
MAGENTA = "\033[35m" if USE_COLOR else ""
WHITE = "\033[37m" if USE_COLOR else ""
RESET = "\033[0m" if USE_COLOR else ""

# ————————————————————————————————————————————————————————————————————————————————————————
# بارگذاری فایل پیکربندی (الزامی — ایجاد نمی‌شود)
# ————————————————————————————————————————————————————————————————————————————————————————
CONFIG_FILE = "mediabot.json"

if not os.path.exists(CONFIG_FILE):
    print(f"{RED}❌ Config file '{CONFIG_FILE}' not found. Please create it.{RESET}")
    exit(1)

try:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
    # اعتبارسنجی
    for key in ["default_path", "video_extensions", "subtitle_extensions"]:
        if key not in config:
            raise ValueError(f"Missing key: {key}")
except (json.JSONDecodeError, ValueError, KeyError) as e:
    print(f"{RED}❌ Invalid config file: {e}{RESET}")
    exit(1)

valid_video_ext = tuple(config["video_extensions"])
valid_sub_ext = tuple(config["subtitle_extensions"])
all_ext = valid_video_ext + valid_sub_ext

# ————————————————————————————————————————————————————————————————————————————————————————
# بررسی حالت Dry Run
# ————————————————————————————————————————————————————————————————————————————————————————
DRY_RUN = "--dry-run" in sys.argv

if DRY_RUN:
    print(f"{MAGENTA}🌀 Dry run mode enabled — no files will be moved.{RESET}\n")

# ————————————————————————————————————————————————————————————————————————————————————————
# مسیر ورودی
# ————————————————————————————————————————————————————————————————————————————————————————
default_path = config["default_path"]
if len(sys.argv) > 1 and sys.argv[1] != "--dry-run":
    path = sys.argv[1]
else:
    path = input(f"{YELLOW}Enter the folder path (default: {default_path}): {RESET}").strip() or default_path

if not os.path.exists(path):
    print(f"{RED}❌ Path not found.{RESET}")
    exit()
else:
    print(f"{GREEN}✅ Starting...{RESET}\n")

# ساخت پوشه‌های مقصد (در حالت dry-run هم ایجاد نمی‌شوند)
movies_folder = os.path.join(path, "Movies")
tv_shows_folder = os.path.join(path, "Series")
if not DRY_RUN:
    os.makedirs(movies_folder, exist_ok=True)
    os.makedirs(tv_shows_folder, exist_ok=True)

# ✅ لیست پوشه‌های مقصد برای اسکیپ
DEST_FOLDERS = [movies_folder, tv_shows_folder]

def is_inside_destination(path_to_check):
    """بررسی می‌کند که آیا مسیر در پوشه‌های مقصد است"""
    real_path = os.path.realpath(path_to_check)
    for dest in DEST_FOLDERS:
        dest_real = os.path.realpath(dest)
        if real_path == dest_real or real_path.startswith(dest_real + os.sep):
            return True
    return False

# الگوی تشخیص سریال
pattern = re.compile(
    r"(?i)"
    r"([A-Za-z0-9\s\.\-_]+?)"  # نام سریال (غیرحریص)
    r"(?:"
        r"[\s\.\-_]*S\d{1,2}[\s\.\-_]*E\d{1,2}|"      # S01E02 یا S01 - E02
        r"[\s\.\-_]*\d{1,2}x\d{1,2}|"                 # 01x02
        r"[\s\.\-_]*S\d{1,2}[\s\.\-_]*\d{1,2}|"       # S02.09
        r"[\s\.\-_]+E\d{1,2}(?!\d)"                   # E16 (با جداکننده قبل از E)
    r")"
)

moved_count = 0
processed_files = set()
handled_dirs = set()
move_log = []
deleted_dirs = []

# ————————————————————————————————————————————————————————————————————————————————————————
# تابع انتقال (در حالت dry-run فقط لاگ می‌شود)
# ————————————————————————————————————————————————————————————————————————————————————————
def safe_move_with_log(src, dst):
    global moved_count
    if DRY_RUN:
        print(f"{MAGENTA}🌀 [DRY] Would move: {src} → {dst}{RESET}")
        move_log.append((dst, src))
        moved_count += 1
        return True
    else:
        try:
            shutil.move(src, dst)
            move_log.append((dst, src))
            moved_count += 1
            return True
        except Exception as e:
            print(f"{RED}❌ Error moving {src} → {dst}: {e}{RESET}")
            return False

# ————————————————————————————————————————————————————————————————————————————————————————
# مرحله ۱: پردازش پوشه‌هایی که نامشان الگوی سریال + Sxx - Exx دارد
# ————————————————————————————————————————————————————————————————————————————————————————
print(f"{CYAN}🔍 Scanning for episode folders with pattern 'Show Sxx - Exx'...{RESET}")

for root, dirs, files in os.walk(path, topdown=False):
    if is_inside_destination(root):
        continue
    for dir_name in dirs:
        dir_path = os.path.join(root, dir_name)
        if not os.path.exists(dir_path):
            continue

        tv_show_match = pattern.search(dir_name)
        if not tv_show_match:
            continue

        has_media = False
        try:
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)
                if os.path.isfile(item_path) and item.lower().endswith(all_ext):
                    has_media = True
                    break
        except (OSError, PermissionError):
            continue

        if not has_media:
            continue

        show_name = tv_show_match.group(1).strip().replace(".", " ").replace("_", " ").title()
        dest_series_dir = os.path.join(tv_shows_folder, show_name)
        dest_sub_dir = os.path.join(dest_series_dir, dir_name)

        print(f"{CYAN}📁 {'[DRY] Would move' if DRY_RUN else 'Moving'} episode folder: {dir_name}{RESET}")

        if not DRY_RUN:
            os.makedirs(dest_series_dir, exist_ok=True)

        if os.path.exists(dest_sub_dir):
            print(f"{RED}⚠️  Folder exists, skipping: {dir_name}{RESET}")
        else:
            if safe_move_with_log(dir_path, dest_sub_dir):
                handled_dirs.add(os.path.realpath(dir_path))
                try:
                    for item in os.listdir(dest_sub_dir if not DRY_RUN else dir_path):
                        item_path = os.path.join(dest_sub_dir if not DRY_RUN else dir_path, item)
                        if os.path.isfile(item_path):
                            processed_files.add(os.path.realpath(item_path))
                except (OSError, PermissionError):
                    pass

# ————————————————————————————————————————————————————————————————————————————————————————
# مرحله ۲: فایل‌های زیرنویس تکی در پوشه‌های والد با الگوی سریال
# ————————————————————————————————————————————————————————————————————————————————————————
print(f"{CYAN}🔍 Scanning for loose subtitle files in non-matching folders...{RESET}")
for root, dirs, files in os.walk(path, topdown=False):
    if is_inside_destination(root):
        continue
    for file in files:
        if file.startswith(".") or not file.lower().endswith(valid_sub_ext):
            continue

        full_path = os.path.join(root, file)
        if os.path.realpath(full_path) in processed_files:
            continue

        parent_dir = os.path.basename(root)
        tv_show_match = pattern.search(parent_dir)
        if tv_show_match:
            show_name = tv_show_match.group(1).strip().replace(".", " ").replace("_", " ").title()
            dest_dir = os.path.join(tv_shows_folder, show_name)
            dest_path = os.path.join(dest_dir, file)

            print(f"{CYAN}📄 {'[DRY] Would move' if DRY_RUN else 'Moving'} subtitle file: {file}{RESET}")
            if not DRY_RUN:
                os.makedirs(dest_dir, exist_ok=True)

            if os.path.exists(dest_path):
                print(f"{RED}⚠️  File exists, skipping: {file}{RESET}")
            else:
                if safe_move_with_log(full_path, dest_path):
                    processed_files.add(os.path.realpath(full_path))

# ————————————————————————————————————————————————————————————————————————————————————————
# مرحله ۳: فایل‌های ویدیو/زیرنویس تکی با الگوی سریال در نام فایل
# ————————————————————————————————————————————————————————————————————————————————————————
print(f"{GREEN}🎬 Processing individual video and subtitle files with series pattern...{RESET}")
for root, dirs, files in os.walk(path, topdown=False):
    if is_inside_destination(root):
        continue
    for file in files:
        if file.startswith(".") or not file.lower().endswith(all_ext):
            continue

        full_path = os.path.join(root, file)
        if os.path.realpath(full_path) in processed_files:
            continue

        tv_show_match = pattern.search(file)
        if tv_show_match:
            show_name = tv_show_match.group(1).strip().replace(".", " ").replace("_", " ").title()
            dest_dir = os.path.join(tv_shows_folder, show_name)
            dest_path = os.path.join(dest_dir, file)

            print(f"{CYAN}📺 {'[DRY] Would move' if DRY_RUN else 'Moving'} media file: {file}{RESET}")
            if not DRY_RUN:
                os.makedirs(dest_dir, exist_ok=True)

            if os.path.exists(dest_path):
                print(f"{RED}⚠️  File exists, skipping: {file}{RESET}")
            else:
                if safe_move_with_log(full_path, dest_path):
                    processed_files.add(os.path.realpath(full_path))

# ————————————————————————————————————————————————————————————————————————————————————————
# مرحله ۴: انتقال فایل‌های باقی‌مانده (فیلم‌ها و زیرنویس‌های مرتبط) به پوشهٔ Movies
# ————————————————————————————————————————————————————————————————————————————————————————
print(f"{MAGENTA}🎞️  Moving remaining media files to Movies folder...{RESET}")
for root, dirs, files in os.walk(path, topdown=False):
    if is_inside_destination(root):
        continue
    for file in files:
        if file.startswith(".") or not file.lower().endswith(all_ext):
            continue

        full_path = os.path.join(root, file)
        if os.path.realpath(full_path) in processed_files:
            continue

        if not full_path.startswith(movies_folder) and not full_path.startswith(tv_shows_folder):
            dest_path = os.path.join(movies_folder, file)
            if os.path.exists(dest_path):
                print(f"{RED}⚠️  File exists in Movies, skipping: {file}{RESET}")
            else:
                print(f"{MAGENTA}🎞️  {'[DRY] Would move' if DRY_RUN else 'Moving'} to Movies: {file}{RESET}")
                safe_move_with_log(full_path, dest_path)

# ————————————————————————————————————————————————————————————————————————————————————————
# تابع پاک‌سازی پوشه‌های خالی (فقط در حالت واقعی)
# ————————————————————————————————————————————————————————————————————————————————————————
def remove_empty_dirs(path):
    removed = []
    for root, dirs, files in os.walk(path, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                if not os.listdir(dir_path):
                    if not DRY_RUN:
                        os.rmdir(dir_path)
                    removed.append(dir_path)
                    print(f"{WHITE}{'[DRY] Would remove' if DRY_RUN else '🧹 Removed'} empty directory: {dir_path}{RESET}")
            except (OSError, PermissionError):
                pass
    return removed

# ————————————————————————————————————————————————————————————————————————————————————————
# نتیجه‌گیری و گزینه‌های تعاملی جدید
# ————————————————————————————————————————————————————————————————————————————————————————
print(f"{GREEN}\n✅ Total moved: {moved_count}{RESET}")

if DRY_RUN:
    print(f"{MAGENTA}🌀 Dry run completed. No changes were made.{RESET}")
    exit()

if moved_count == 0:
    print(f"{YELLOW}ℹ️  No files were moved.{RESET}")
    while True:
        try:
            choice = input(f"\n{YELLOW}Choose an option:\n0 → Exit and do nothing\n1 → Exit and clean up empty folders\n{RESET}").strip()
            if choice == "0":
                print(f"{GREEN}✅ Exiting...{RESET}")
                break
            elif choice == "1":
                print(f"{WHITE}🧹 Cleaning up empty directories...{RESET}")
                remove_empty_dirs(path)
                print(f"{GREEN}✅ Cleanup completed.{RESET}")
                break
            else:
                print(f"{RED}❌ Invalid choice. Enter 0 or 1.{RESET}")
        except KeyboardInterrupt:
            print(f"\n{RED}⚠️  Operation cancelled.{RESET}")
            break
    exit()

# گزینه‌های جدید: 0, 1, 2
while True:
    try:
        choice = input(f"\n{YELLOW}Choose an option:\n0 → Exit and do nothing\n1 → Exit and clean up empty folders\n2 → Undo all operations\n{RESET}").strip()
        if choice == "0":
            print(f"{GREEN}✅ Exiting...{RESET}")
            break
        elif choice == "1":
            print(f"{WHITE}🧹 Cleaning up empty directories...{RESET}")
            deleted_dirs = remove_empty_dirs(path)
            print(f"{GREEN}✅ Cleanup completed.{RESET}")
            break
        elif choice == "2":
            print(f"{MAGENTA}↩️  Undoing all moves...{RESET}")
            undo_count = 0

            for dir_path in deleted_dirs:
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    print(f"{WHITE}🔄 Restored empty directory: {dir_path}{RESET}")
                except Exception as e:
                    print(f"{RED}❌ Failed to restore directory {dir_path}: {e}{RESET}")

            for dest, src in reversed(move_log):
                if os.path.exists(dest):
                    try:
                        if os.path.exists(src):
                            if os.path.isdir(src):
                                shutil.rmtree(src)
                            else:
                                os.remove(src)
                        shutil.move(dest, src)
                        undo_count += 1
                        print(f"{MAGENTA}↩️  Undone: {dest} → {src}{RESET}")
                    except Exception as e:
                        print(f"{RED}❌ Failed to undo {dest} → {src}: {e}{RESET}")
                else:
                    print(f"{YELLOW}⚠️  Source not found for undo: {dest}{RESET}")

            print(f"{GREEN}✅ Undo completed. {undo_count} items restored.{RESET}")
            break
        else:
            print(f"{RED}❌ Invalid choice. Enter 0, 1, or 2.{RESET}")
    except KeyboardInterrupt:
        print(f"\n{RED}⚠️  Operation cancelled.{RESET}")
        break