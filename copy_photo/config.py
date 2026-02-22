import os
import json

DEFAULT_CONFIG = {
    "mount_patterns": [
        "/media/{user}/{label}",
        "/run/media/{user}/{label}"
    ],
    "source_patterns": ["DCIM/*"],
    "photo_extensions": [".jpg", ".jpeg", ".cr2", ".cr3", ".raw", ".nef", "arw", "raf", "rw2", ".orf", ".x3f", ".dng"],
    "destination_template": "{date}-{camera}-{name}",
    "subfolders": ["selected", "selected/exported","raw-camera","jpg-camera","raw-selected","jpg-selected","jpg-exported","jpg-exported-print","jpg-exported-telegram","jpg-exported-vk"]
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
