import os
import glob
import shutil
from datetime import datetime
from tqdm import tqdm
from .utils import find_mount_point

def find_photo_directories(mount_point, config_source_patterns, config_photo_extensions):
    """Поиск директорий с фотографиями по заданным маскам."""
    photo_dirs = []
    extensions = tuple(ext.lower() for ext in config_photo_extensions)

    for pattern in config_source_patterns:
        full_pattern = os.path.join(mount_point, pattern)
        matched_dirs = glob.glob(full_pattern)

        for dir_path in matched_dirs:
            if os.path.isdir(dir_path):
                if _contains_photos(dir_path, extensions):
                    photo_dirs.append(dir_path)
                    print(f"Найдена директория с фото: {dir_path}")

    if not photo_dirs:
        raise FileNotFoundError(
            f"Не найдено ни одной директории с фото по маскам: {config_source_patterns} "
            f"содержащей файлы с расширениями: {', '.join(extensions)}"
        )

    return photo_dirs

def _contains_photos(directory, extensions):
    """Проверяет, содержит ли директория файлы с заданными расширениями."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(extensions):
                return True
    return False

def get_earliest_photo_date(photo_dirs, extensions):
    """Получение даты самого раннего фото в директориях."""
    earliest_date = None
    extensions = tuple(ext.lower() for ext in extensions)

    for photo_dir in photo_dirs:
        for root, _, files in os.walk(photo_dir):
            for file in files:
                if file.lower().endswith(extensions):
                    file_path = os.path.join(root, file)
                    file_date = datetime.fromtimestamp(os.path.getmtime(file_path))

                    if earliest_date is None or file_date < earliest_date:
                        earliest_date = file_date

    if earliest_date is None:
        raise FileNotFoundError(
            f"Не найдено ни одного фото с расширениями: {', '.join(extensions)}"
        )

    return earliest_date.strftime("%Y%m%d")

def copy_with_progress(source_dirs, dest_dir, extensions):
    """Копирование файлов с прогресс-баром."""
    all_files = []
    extensions = tuple(ext.lower() for ext in extensions)

    for source_dir in source_dirs:
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.lower().endswith(extensions):
                    all_files.append(os.path.join(root, file))

    if not all_files:
        print("Нет файлов для копирования!")
        return False

    for file in tqdm(all_files, desc="Копирование файлов", unit="file"):
        try:
            shutil.copy2(file, dest_dir)
        except Exception as e:
            tqdm.write(f"Ошибка при копировании {file}: {str(e)}")

    return True

def setup_destination(dest_path, subfolders):
    """Создание целевой директории и поддиректорий."""
    os.makedirs(dest_path, exist_ok=True)
    for folder in subfolders:
        os.makedirs(os.path.join(dest_path, folder), exist_ok=True)
