import os
from pathlib import Path
from typing import List, Optional
import logging
from ..models.photo import PhotoFile, PhotoMetadata
from ..utils.exif import ExifReader

logger = logging.getLogger(__name__)


class ScannerService:
    """Сервис для сканирования и анализа фотографий"""

    def __init__(self, exif_reader: Optional[ExifReader] = None):
        self.exif_reader = exif_reader or ExifReader()

    def scan_directory(self, directory: Path, extensions: List[str]) -> List[PhotoFile]:
        """Сканирование директории на наличие фотографий"""
        photos = []
        extensions = tuple(ext.lower() for ext in extensions)

        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(extensions):
                    file_path = Path(root)/file

                    try:
                        # Чтение EXIF данных
                        exif_data = self.exif_reader.read_exif(file_path)
                        metadata = PhotoMetadata.from_exif(exif_data) if exif_data else None

                        # Создание объекта фото
                        photo = PhotoFile(path=file_path, metadata=metadata)
                        photos.append(photo)

                        logger.debug(f"Найдена: {file_path}")

                    except Exception as e:
                        logger.warning(f"Ошибка обработки {file_path}: {e}")

        logger.info(f"Сканирование завершено. Найдено {len(photos)} файлов")
        return photos
