from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
from enum import Enum


class MediaType(Enum):
    """Типы медиафайлов"""
    PHOTO = "photo"
    RAW = "raw"
    VIDEO = "video"


@dataclass
class CameraInfo:
    """Информация о камере"""
    make: Optional[str] = None
    model: Optional[str] = None

    @property
    def full_model(self) -> str:
        """Полное название модели"""
        if self.make and self.model:
            return f"{self.make} {self.model}".strip()
        return self.model or self.make or "Unknown"

    def sanitize_for_filename(self) -> str:
        """Очистка для использования в имени файла"""
        name = self.full_model
        return "".join(c if c.isalnum() else "_" for c in name)


@dataclass
class PhotoMetadata:
    """Метаданные фотографии"""
    camera: CameraInfo = field(default_factory=CameraInfo)
    date_taken: Optional[datetime] = None
    size: Optional[int] = None

    @classmethod
    def from_exif(cls, exif_data: Dict) -> 'PhotoMetadata':
        """Создание из EXIF данных"""
        from ..utils.exif import ExifReader  # Импорт здесь чтобы избежать циклических зависимостей
        return ExifReader.parse_exif(exif_data)


@dataclass
class PhotoFile:
    """Класс, представляющий файл фотографии"""
    path: Path
    metadata: Optional[PhotoMetadata] = None

    def __post_init__(self):
        self.path = Path(self.path)

    @property
    def filename(self) -> str:
        return self.path.name

    @property
    def extension(self) -> str:
        return self.path.suffix.lower()

    @property
    def size(self) -> int:
        return self.path.stat().st_size

    @property
    def modification_date(self) -> datetime:
        return datetime.fromtimestamp(self.path.stat().st_mtime)

    @property
    def date_for_sorting(self) -> datetime:
        """Дата для сортировки (предпочтительно из EXIF, иначе из файла)"""
        if self.metadata and self.metadata.date_taken:
            return self.metadata.date_taken
        return self.modification_date

    def get_target_filename(self, template: str = "{date}_{original}") -> str:
        date_str = self.date_for_sorting.strftime("%Y%m%d_%H%M%S")

        # Проверяем наличие metadata и camera ДО обращения к ним
        camera_str = (
            self.metadata.camera.sanitize_for_filename()
            if self.metadata and self.metadata.camera
            else "Unknown"
        )

        return template.format(
            date=date_str,
            camera=camera_str,
            original=Path(self.filename).stem,  # Без расширения
            ext=self.extension[1:] if self.extension else ""
        ) + self.extension


class PhotoCollection:
    """Коллекция фотографий с методами для группировки и фильтрации"""

    def __init__(self, photos: List[PhotoFile] = None):
        self.photos = photos or []

    def add(self, photo: PhotoFile):
        """Добавление фотографии в коллекцию"""
        self.photos.append(photo)

    def add_many(self, photos: List[PhotoFile]):
        """Добавление нескольких фотографий"""
        self.photos.extend(photos)

    def filter_by_camera(self, camera_model: str) -> 'PhotoCollection':
        """Фильтрация по модели камеры"""
        filtered = [p for p in self.photos
            if p.metadata and p.metadata.camera.full_model == camera_model]

        return PhotoCollection(filtered)

    def filter_by_date_range(self, start_date: datetime, end_date: datetime) -> 'PhotoCollection':
        """Фильтрация по диапазону дат"""
        filtered = [p for p in self.photos
             if start_date <= p.date_for_sorting <= end_date]

        return PhotoCollection(filtered)

    def group_by_camera_and_date(self) -> Dict[tuple, List[PhotoFile]]:
        """Группировка по камере и дате"""
        groups = {}

        for photo in self.photos:
            camera = photo.metadata.camera.full_model if photo.metadata else "Unknown"
            date_key = photo.date_for_sorting.strftime("%Y%m%d")
            key = (date_key, camera)

            if key not in groups:
                groups[key] = []
            groups[key].append(photo)

        return groups

    def __len__(self):
        return len(self.photos)

    def __iter__(self):
        return iter(self.photos)

    def __getitem__(self, index):
        return self.photos[index]
