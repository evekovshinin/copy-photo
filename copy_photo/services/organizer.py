from pathlib import Path
from typing import Dict, List
import logging
from ..models.photo import PhotoFile, PhotoCollection

logger = logging.getLogger(__name__)


class OrganizerService:
    """Сервис для организации фотографий по папкам"""

    def __init__(self, base_output_dir: Path):
        self.base_output_dir = Path(base_output_dir)

    def generate_folder_structure(self, photos: PhotoCollection, session_name: str) -> Dict[tuple, Path]:
        """Генерация структуры папок на основе фотографий"""
        groups = photos.group_by_camera_and_date()
        folder_paths = {}

        for (date_str, camera_model), photo_group in groups.items():
            # Создаем безопасное имя папки
            safe_camera_name = "".join(c if c.isalnum() else "_" for c in camera_model)
            # TODO move template into config
            folder_name = f"{date_str}-{safe_camera_name}-{session_name}"
            folder_path = self.base_output_dir / folder_name

            # Создаем подпапки
            # TODO move subfolder list into config
            subfolders = [
                "raw-camera",
                "jpg-camera",
                "raw-selected",
                "jpg-export",
                "jpg-export-print",
                "jpg-export-telegram",
                "jpg-export-instagram",
                "jpg-export-vk"
                ]
            for subfolder in subfolders:
                (folder_path / subfolder).mkdir(parents=True, exist_ok=True)

            folder_paths[(date_str, camera_model)] = folder_path
            logger.info(f"Создана папка: {folder_path}")

        return folder_paths
