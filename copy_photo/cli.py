import os
import sys
import argparse
import logging
from pathlib import Path
from typing import List
from datetime import datetime

# Импорт наших классов
from copy_photo.models.photo import PhotoCollection
from copy_photo.services.scanner import ScannerService
from copy_photo.services.organizer import OrganizerService
from copy_photo.services.copier import CopierService, CopyResult
from copy_photo.utils.exif import ExifReader
from copy_photo.config import load_config
from copy_photo.utils import find_source_dirs

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PhotoCopyApp:
    """Основной класс приложения"""

    def __init__(self, config_path: str = None):
        self.config = load_config(config_path) if config_path else load_config(None)
        self.scanner = ScannerService(ExifReader())
        self.photos = PhotoCollection()

    @staticmethod
    def _normalize_extensions(extensions: List[str]) -> List[str]:
        normalized = []
        for ext in extensions:
            value = ext.lower().strip()
            if not value:
                continue
            normalized.append(value if value.startswith(".") else f".{value}")
        return normalized

    def run(self, session_name: str, source_dirs: List[Path], output_base: Path):
        """Основной процесс копирования"""
        logger.info(f"Начало обработки сессии: {session_name}")

        # 1. Сканирование
        logger.info("Этап 1: Сканирование фотографий")
        raw_extensions = self._normalize_extensions(self.config.get("photo_extensions-raw", []))
        jpg_extensions = self._normalize_extensions(self.config.get("photo_extensions-jpg", [".jpg", ".jpeg"]))
        scan_extensions = list(dict.fromkeys(raw_extensions + jpg_extensions))

        for source_dir in source_dirs:
            photos = self.scanner.scan_directory(
                source_dir,
                scan_extensions
            )
            self.photos.add_many(photos)

        if len(self.photos) == 0:
            raise ValueError("Не найдено ни одной фотографии")

        logger.info(f"Найдено фотографий: {len(self.photos)}")

        # 2. Организация
        logger.info("Этап 2: Организация структуры папок")
        organizer = OrganizerService(output_base, self.config)
        folder_structure = organizer.generate_folder_structure(self.photos, session_name)

        # 3. Копирование
        logger.info("Этап 3: Копирование файлов")
        copier = CopierService(config=self.config, preserve_metadata=True)

        overall_result = CopyResult()

        for (date_str, camera_model), folder_path in folder_structure.items():
            # Фильтруем фото для этой группы
            group_photos = self.photos.filter_by_camera(camera_model)
            group_photos = group_photos.filter_by_date_range(
                datetime.strptime(date_str, "%Y%m%d"),
                datetime.strptime(date_str, "%Y%m%d").replace(hour=23, minute=59, second=59)
            )

            if len(group_photos) > 0:
                logger.info(f"Копирование {len(group_photos)} фото: {date_str}-{camera_model}")
                result = copier.copy_photos(group_photos, folder_path)

                # TODO Think about it
                # Собираем общую статистику
                overall_result.total += result.total
                overall_result.success += result.success
                overall_result.failed += result.failed
                overall_result.errors.extend(result.errors)

        # 4. Отчет
        self._print_report(overall_result, folder_structure)

        return overall_result.success > 0

    def _print_report(self, result, folder_structure):
        """Вывод отчета о выполнении"""
        print("\n" + "="*60)
        print("ОТЧЕТ О ВЫПОЛНЕНИИ")
        print("="*60)
        print(f"Всего обработано: {result.total} файлов")
        print(f"Успешно скопировано: {result.success} файлов")
        print(f"Не удалось скопировать: {result.failed} файлов")

        if result.errors:
            print(f"\nОшибки (первые 5):")
            for error in result.errors[:5]:
                print(f"  • {error}")


def main():
    """Main entry point for the command line interface"""
    parser = argparse.ArgumentParser(
        description="Professional photo copying and organization tool with EXIF support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    copy-photo session1
    copy-photo session1 /path/to/source1 /path/to/source2
    copy-photo --config /path/to/config.json session1
        """
    )

    parser.add_argument(
        "session_name",
        help="Name of the copying session (used in folder naming)"
    )

    parser.add_argument(
        "source_dirs",
        nargs="*",
        help="Source directories to scan for photos (optional; auto-detected from config if omitted)"
    )

    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output base directory (default: destination_path from config)"
    )

    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to configuration file"
    )

    args = parser.parse_args()

    # Create and run the app
    try:
        app = PhotoCopyApp(config_path=args.config)

        output_base = args.output
        if output_base is None:
            output_base = Path(app.config.get("destination_path", "~/Photos")).expanduser()
        else:
            output_base = output_base.expanduser()

        output_base.mkdir(parents=True, exist_ok=True)

        # Convert source dirs to Path objects or auto-discover from config
        if args.source_dirs:
            source_dirs = [Path(src) for src in args.source_dirs]
        else:
            source_dirs = find_source_dirs(app.config)
            logger.info(
                "Автоматически найдены исходные директории: %s",
                ", ".join(str(path) for path in source_dirs)
            )

        # Check if source directories exist
        for src_dir in source_dirs:
            if not src_dir.exists():
                print(f"Error: Source directory does not exist: {src_dir}")
                sys.exit(1)

        success = app.run(args.session_name, source_dirs, output_base)

        if success:
            print("\nКопирование завершено успешно!")
            sys.exit(0)
        else:
            print("\nКопирование завершено с ошибками.")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
