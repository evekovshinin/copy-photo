import os
import json
from pathlib import Path

DEFAULT_CONFIG = {
    "mount_patterns": [
        "/media/{user}/{label}",
        "/run/media/{user}/{label}"
    ],
    "source_patterns": ["DCIM/*"],
    "photo_extensions-raw": [".cr2", ".cr3", ".raw", ".nef", "arw", "raf", "rw2", ".orf", ".x3f", ".dng"],
    "photo_extensions-jpg": [".jpg", ".jpeg"],
    "destination_template": "{date}-{camera}-{name}",
    "subfolders": ["camera-raw","camera-jpg","selected-raw","selected-jpg","exported-jpg","exported-jpg-print","exported-jpg-telegram","exported-jpg-vk"],
    "subfolders-raw": ["camera-raw"],
    "subfolders-jpg": ["camera-jpg"]
}

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "photo_copy" / "config.json"

def load_config(config_path):
    """Загрузка конфигурации из JSON файла."""
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
    else:
        config_path = Path(config_path).expanduser()

    config_path.parent.mkdir(parents=True, exist_ok=True)

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
