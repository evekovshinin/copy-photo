import shutil
from pathlib import Path
from typing import Dict, List
import logging
from tqdm import tqdm
from ..models.photo import PhotoFile, PhotoCollection

logger = logging.getLogger(__name__)


class CopyResult:
    """Результат операции копирования"""

    def __init__(self):
        self.total = 0
        self.success = 0
        self.failed = 0
        self.errors = []

    def add_success(self):
        self.total += 1
        self.success += 1

    def add_error(self, error_msg: str):
        self.total += 1
        self.failed += 1
        self.errors.append(error_msg)


class CopierService:
    """Сервис для копирования фотографий"""

    def __init__(self, config: Dict = None, preserve_metadata: bool = True):
        self.config = config or {}
        self.preserve_metadata = preserve_metadata

        self.jpg_extensions = set(self._normalize_extensions(
            self.config.get("photo_extensions-jpg", [".jpg", ".jpeg"])
        ))
        self.raw_extensions = set(self._normalize_extensions(
            self.config.get("photo_extensions-raw", [".raw"])
        ))

        raw_subfolders = self.config.get("subfolders-raw", ["raw-camera"])
        jpg_subfolders = self.config.get("subfolders-jpg", ["jpg-camera"])
        self.raw_target_subfolder = raw_subfolders[0] if raw_subfolders else "camera-raw"
        self.jpg_target_subfolder = jpg_subfolders[0] if jpg_subfolders else "camera-jpg"

    @staticmethod
    def _normalize_extensions(extensions: List[str]) -> List[str]:
        normalized = []
        for ext in extensions:
            value = ext.lower().strip()
            if not value:
                continue
            normalized.append(value if value.startswith(".") else f".{value}")
        return normalized

    def copy_photos(self, photos: PhotoCollection, target_dir: Path) -> CopyResult:
        """Копирование фотографий в целевую директорию"""
        result = CopyResult()

        # TODO requires sort raws and jpgs between directories
        for photo in tqdm(photos, desc="Копирование"):
            try:
                # Выбираем подпапку на основе типа файла
                if photo.extension in self.jpg_extensions:
                    subfolder = self.jpg_target_subfolder
                elif photo.extension in self.raw_extensions:
                    subfolder = self.raw_target_subfolder
                else:
                    subfolder = self.raw_target_subfolder

                target_path = target_dir / subfolder / photo.filename

                if self.preserve_metadata:
                    # Копируем с сохранением всех метаданных
                    shutil.copy2(photo.path, target_path)
                else:
                    # Простое копирование
                    shutil.copy(photo.path, target_path)

                # Проверяем целостность
                if self._verify_copy(photo.path, target_path):
                    result.add_success()
                else:
                    result.add_error(f"Ошибка проверки: {photo.filename}")

            except Exception as e:
                error_msg = f"{photo.filename}: {str(e)}"
                result.add_error(error_msg)
                logger.error(error_msg)

        return result

    # TODO make verification process by target directories
    def _verify_copy(self, source: Path, target: Path) -> bool:
        """Проверка целостности скопированного файла"""
        if not target.exists():
            return False

        # Сравниваем размеры
        if source.stat().st_size != target.stat().st_size:
            return False

        # Можно добавить проверку хешей для важных данных
        # if hash(source) != hash(target): ...

        return True
