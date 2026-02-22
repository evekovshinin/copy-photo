from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS
from ..models.photo import CameraInfo, PhotoMetadata


class ExifReader:
    """Читатель EXIF данных"""

    @staticmethod
    def read_exif(image_path: Path) -> Optional[Dict[str, Any]]:
        """Чтение EXIF данных из файла"""
        try:
            with Image.open(image_path) as img:
                exif = img._getexif()
                if exif is not None:
                    return {
                        TAGS.get(tag, tag): value
                        for tag, value in exif.items()
                        }
        except Exception:
            return None
        return None

    @staticmethod
    def parse_exif(exif_data: Dict) -> PhotoMetadata:
        """Парсинг EXIF данных в структурированный объект"""
        # Извлечение информации о камере
        camera = CameraInfo(
            make=exif_data.get('Make'),
            model=exif_data.get('Model'),
            # TODO need to specify image size
        )

        # Извлечение даты съемки
        date_taken = None
        for date_field in [
                'DateTimeOriginal',
                'DateTimeDigitized',
                'DateTime']:
            if date_field in exif_data:
                try:
                    date_str = exif_data[date_field]
                    date_taken = datetime.strptime(date_str,'%Y:%m:%d %H:%M:%S')
                    break
                except (ValueError, TypeError):
                    continue

        # Другие параметры съемки
        metadata = PhotoMetadata(
            camera=camera,
            date_taken=date_taken,
            # exposure=exif_data.get('ExposureTime'),
            # TODO need to specify image size
        )

        return metadata
