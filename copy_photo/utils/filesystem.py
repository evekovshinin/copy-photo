import os
import glob
from pathlib import Path

def find_mount_point(config, label, user):
    """Поиск точки монтирования по метке диска."""
    for pattern in config["mount_patterns"]:
        mount_point = pattern.format(user=user, label=label)
        if os.path.ismount(mount_point):
            return mount_point
    raise FileNotFoundError(
        f"Диск с меткой {label} не найден. Проверенные пути: {config['mount_patterns']}"
    )


def find_source_dirs(config):
    """Поиск исходных директорий по шаблонам из конфига."""
    user = os.getenv("USER", "")
    label = config.get("label", "*")

    mount_patterns = config.get("mount_patterns", [])
    source_patterns = config.get("source_patterns", ["DCIM/*"])

    source_dirs = []

    for mount_pattern in mount_patterns:
        formatted_mount = mount_pattern.format(user=user, label=label)

        for mount_path in glob.glob(formatted_mount):
            for source_pattern in source_patterns:
                full_pattern = str(Path(mount_path) / source_pattern)
                for source_path in glob.glob(full_pattern):
                    if os.path.isdir(source_path):
                        source_dirs.append(Path(source_path))

    # Убираем дубликаты, сохраняя порядок
    source_dirs = list(dict.fromkeys(source_dirs))

    if not source_dirs:
        raise FileNotFoundError(
            "Не удалось найти директории с фото по шаблонам "
            f"mount_patterns={mount_patterns}, source_patterns={source_patterns}."
        )

    return source_dirs

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
