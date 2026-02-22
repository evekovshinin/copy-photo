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
from copy_photo.utils import find_mount_point

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PhotoCopyApp:
    """Основной класс приложения"""

    def __init__(self, config_path: str = None):
        self.config = load_config(config_path) if config_path else {}
        self.scanner = ScannerService(ExifReader())
        self.photos = PhotoCollection()

    def run(self, session_name: str, source_dirs: List[Path], output_base: Path):
        """Основной процесс копирования"""
        logger.info(f"Начало обработки сессии: {session_name}")

        # 1. Сканирование
        logger.info("Этап 1: Сканирование фотографий")
        for source_dir in source_dirs:
            photos = self.scanner.scan_directory(
                source_dir,
                # TODO Think about use default values here
                self.config.get("photo_extensions", [".jpg", ".jpeg", ".raw"])
            )
            self.photos.add_many(photos)

        if len(self.photos) == 0:
            raise ValueError("Не найдено ни одной фотографии")

        logger.info(f"Найдено фотографий: {len(self.photos)}")

        # 2. Организация
        logger.info("Этап 2: Организация структуры папок")
        organizer = OrganizerService(output_base)
        folder_structure = organizer.generate_folder_structure(self.photos, session_name)

        # 3. Копирование
        logger.info("Этап 3: Копирование файлов")
        copier = CopierService(preserve_metadata=True)

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

        print(f"\nСозданные папки:")
        for (date, camera), path in folder_structure.items():
            print(f"  📁 {date}-{camera}")
            print(f"     {path}")

def main():
    # Конфигурация
    config_dir = Path.home() / ".config" / "photo_copy"
    config_path = config_dir / "config.json"
    config_dir.mkdir(exist_ok=True)

    # Аргументы командной строки
    parser = argparse.ArgumentParser(description="Копирование фотографий с организацией по метаданным")
    parser.add_argument("session", help="Название фотосессии")
    parser.add_argument("--source", "-s", action="append",
                       help="Исходные директории (можно указать несколько)")
    parser.add_argument("--output", "-o", default="~/Photos",
                       help="Базовая выходная директория")
    parser.add_argument("--camera", "-c", help="Фильтр по камере")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Создаем экземпляр приложения
        app = PhotoCopyApp(config_path)

        # Если source не указан, ищем точку монтирования
        if not args.source:
            config = load_config(config_path)
            mount_point = find_mount_point(config, "EOS_DIGITAL", os.getenv("USER"))
            source_dirs = [Path(mount_point)]
        else:
            source_dirs = [Path(src) for src in args.source]

        # Запускаем приложение
        output_dir = Path(args.output).expanduser()
        success = app.run(args.session, source_dirs, output_dir)

        sys.exit(0 if success else 1)

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=args.verbose)
        sys.exit(1)

if __name__ == "__main__":
    main()
