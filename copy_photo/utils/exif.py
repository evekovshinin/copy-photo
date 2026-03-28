from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS
import exiftool
from ..models.photo import CameraInfo, PhotoMetadata


class ExifReader:
    """Читатель EXIF данных"""

    RAW_EXTENSIONS = {'.cr2', '.cr3', '.raw', '.nef', '.arw', '.raf', '.rw2', '.orf', '.x3f', '.dng'}

    @staticmethod
    def read_exif(image_path: Path) -> Optional[Dict[str, Any]]:
        """Чтение EXIF данных из файла"""
        ext = image_path.suffix.lower()
        if ext in ExifReader.RAW_EXTENSIONS:
            return ExifReader._read_exif_exiftool(image_path)
        else:
            return ExifReader._read_exif_pil(image_path)

    @staticmethod
    def _read_exif_pil(image_path: Path) -> Optional[Dict[str, Any]]:
        """Чтение EXIF с помощью PIL"""
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
    def _read_exif_exiftool(image_path: Path) -> Optional[Dict[str, Any]]:
        """Чтение EXIF с помощью exiftool"""
        try:
            with exiftool.ExifToolHelper() as et:
                metadata = et.get_metadata(str(image_path))[0]
                # Преобразуем ключи exiftool в стандартные
                exif_dict = {}
                for key, value in metadata.items():
                    if key.startswith('EXIF:'):
                        clean_key = key[5:]
                        exif_dict[clean_key] = value
                    elif key in ['Make', 'Model', 'DateTimeOriginal', 'DateTimeDigitized', 'DateTime']:
                        exif_dict[key] = value
                return exif_dict if exif_dict else None
        except Exception:
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
