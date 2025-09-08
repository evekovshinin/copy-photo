#!/usr/bin/env python3
import os
import sys
import json
import shutil
import argparse
import glob
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

# Заполнение конфига по умолчанию
DEFAULT_CONFIG = {
    "mount_patterns": [
        "/media/{user}/{label}",
        "/run/media/{user}/{label}"
    ],
    "source_patterns": ["DCIM/*"],  # Новое поле: маски для поиска директорий с фото
    "photo_extensions": [".jpg", ".jpeg", ".cr2", ".raw"],
    "destination_template": "{date}-canon600d-{name}",
    "subfolders": ["selected", "selected/exported"]
}


def load_config(config_path):
    """Загрузка конфигурации из JSON файла."""
    if not os.path.exists(config_path):
        print(f"Конфиг не найден, создан новый в {config_path}")
        with open(config_path, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG

    with open(config_path) as f:
        config = json.load(f)

    # Проверяем наличие всех необходимых полей
    for key in DEFAULT_CONFIG:
        if key not in config:
            config[key] = DEFAULT_CONFIG[key]

    return config


def find_mount_point(config, label, user):
    """Поиск точки монтирования по метке диска."""
    for pattern in config["mount_patterns"]:
        mount_point = pattern.format(user=user, label=label)
        if os.path.ismount(mount_point):
            return mount_point
    raise FileNotFoundError(
        f"Диск с меткой {label} не найден. Проверенные пути: {config['mount_patterns']}"
    )


def find_photo_directories(mount_point, source_patterns):
    """Поиск директорий с фотографиями по заданным маскам."""
    photo_dirs = []

    for pattern in source_patterns:
        full_pattern = os.path.join(mount_point, pattern)
        matched_dirs = glob.glob(full_pattern)

        for dir_path in matched_dirs:
            if os.path.isdir(dir_path):
                photo_dirs.append(dir_path)
                print(f"Найдена директория с фото: {dir_path}")

    if not photo_dirs:
        raise FileNotFoundError(
            f"Не найдено ни одной директории с фото по маскам: {source_patterns}"
        )

    return photo_dirs


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


def get_files_info(directories, extensions):
    """Получение информации о файлах: количество и общий размер."""
    file_count = 0
    total_size = 0
    extensions = tuple(ext.lower() for ext in extensions)

    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(extensions):
                    file_path = os.path.join(root, file)
                    file_count += 1
                    total_size += os.path.getsize(file_path)

    return file_count, total_size


def verify_copy(source_dirs, dest_dir, extensions):
    """Проверка корректности копирования."""
    src_count, src_size = get_files_info(source_dirs, extensions)
    dst_count, dst_size = get_files_info([dest_dir], extensions)

    print("\nПроверка результатов копирования:")
    print(f"Файлов в источнике: {src_count}, в приемнике: {dst_count}")
    print(f"Размер источника: {src_size / (1024 * 1024):.2f} MB, приемника: {dst_size / (1024 * 1024):.2f} MB")

    if src_count != dst_count:
        print(f"⚠️ Предупреждение: количество файлов не совпадает ({src_count} vs {dst_count})")
        return False

    if src_size != dst_size:
        print(f"⚠️ Предупреждение: общий размер файлов не совпадает ({src_size} vs {dst_size} bytes)")
        return False

    print("✓ Все файлы успешно скопированы, проверка пройдена")
    return True


def copy_with_progress(source_dirs, dest_dir, extensions):
    """Копирование файлов с прогресс-баром."""
    # Создаем список всех файлов для копирования
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

    # Копируем с прогресс-баром
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


def main():
    # Определяем путь к конфигу
    config_dir = os.path.expanduser("~/.config/photo_copy")
    config_path = os.path.join(config_dir, "config.json")

    # Создаем директорию для конфига если ее нет
    os.makedirs(config_dir, exist_ok=True)

    # Загружаем конфиг
    config = load_config(config_path)

    parser = argparse.ArgumentParser(description="Копирование фотографий с флешки фотоаппарата")
    parser.add_argument("name", help="Название папки для сохранения")
    parser.add_argument("--label", default="EOS_DIGITAL",
                        help="Метка диска (по умолчанию: EOS_DIGITAL)")
    parser.add_argument("--user", default=os.getenv("USER"),
                        help="Имя пользователя (по умолчанию: текущий пользователь)")
    parser.add_argument("--no-verify", action="store_true",
                        help="Пропустить проверку после копирования")

    args = parser.parse_args()

    try:
        # 1. Находим точку монтирования
        mount_point = find_mount_point(config, args.label, args.user)
        print(f"Найдена флешка в: {mount_point}")

        # 2. Ищем директории с фотографиями
        photo_dirs = find_photo_directories(mount_point, config["source_patterns"])
        print(f"Найдено директорий с фото: {len(photo_dirs)}")

        # 3. Получаем дату самого раннего фото
        date_str = get_earliest_photo_date(photo_dirs, config["photo_extensions"])
        print(f"Дата самого раннего фото: {date_str}")

        # 4. Создаем целевую директорию
        dest_folder = config["destination_template"].format(date=date_str, name=args.name)
        dest_dir = os.path.expanduser(f"~/Photos/{dest_folder}")
        print(f"Фотографии будут скопированы в: {dest_dir}")

        # 5. Создаем структуру папок
        setup_destination(dest_dir, config["subfolders"])

        # 6. Копируем файлы
        copy_success = copy_with_progress(photo_dirs, dest_dir, config["photo_extensions"])

        # 7. Проверяем результаты копирования
        if copy_success and not args.no_verify:
            verify_copy(photo_dirs, dest_dir, config["photo_extensions"])

        print("\nГотово!")
    except Exception as e:
        print(f"Ошибка: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()