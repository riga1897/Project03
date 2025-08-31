import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from .decorators import simple_cache

logger = logging.getLogger(__name__)


class JSONFileHandler:
    """Класс для работы с JSON файлами"""
    
    def __init__(self):
        """Инициализация обработчика JSON"""
        pass
    
    def load_json(self, file_path):
        """Загрузка данных из JSON файла"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def save_json(self, file_path, data):
        """Сохранение данных в JSON файл"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except OSError:
            return False


class FileOperations:
    """Класс для файловых операций"""
    
    def __init__(self):
        """Инициализация файловых операций"""
        pass
    
    def file_exists(self, file_path):
        """Проверка существования файла"""
        from pathlib import Path
        return Path(file_path).exists()
    
    def create_directory(self, dir_path):
        """Создание директории"""
        from pathlib import Path
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def delete_file(self, file_path):
        """Удаление файла"""
        from pathlib import Path
        path = Path(file_path)
        if path.exists():
            path.unlink()
            return True
        return False
    
    def copy_file(self, source_path, dest_path):
        """Копирование файла"""
        import shutil
        from pathlib import Path
        if Path(source_path).exists():
            shutil.copy2(source_path, dest_path)
            return True
        return False
    """
    Обработчик JSON-файлов с улучшенной обработкой ошибок

    Предоставляет методы для безопасного чтения и записи JSON-файлов
    с кэшированием, атомарными операциями и обработкой ошибок.
    """

    @simple_cache(ttl=60)
    def read_json(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Читает JSON-файл с обработкой различных ошибок
        Args:
            file_path: Путь к JSON-файлу
        Returns:
            Список словарей с данными
        """
        try:
            if not file_path.exists() or file_path.stat().st_size == 0:
                return []

            with file_path.open("r", encoding="utf-8") as f:
                return json.load(f)

        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in {file_path}, returning empty list. Error: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return []

    def write_json(self, file_path: Path, data: List[Dict[str, Any]]) -> None:
        """
        Атомарная запись в JSON-файл с обработкой ошибок
        Args:
            file_path: Путь к файлу
            data: Данные для записи
        """
        temp_file = file_path.with_suffix(".tmp")
        try:
            # Создаем директорию, если её нет
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with temp_file.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # Атомарная замена файла
            temp_file.replace(file_path)
            self.read_json.clear_cache()  # Очищаем кэш

        except Exception as e:
            if temp_file.exists():
                temp_file.unlink()
            logger.error(f"Failed to write {file_path}: {e}")
            raise
        finally:
            if temp_file.exists():
                temp_file.unlink()


# Глобальный экземпляр обработчика JSON для использования во всем приложении
json_handler = JSONFileHandler()
