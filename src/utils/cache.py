import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional

# Configure logger
logger = logging.getLogger(__name__)


class FileCache:
    """Класс для файлового кэширования API-ответов"""

    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self._ensure_dir_exists()

    def _ensure_dir_exists(self) -> None:
        """Создает все необходимые директории"""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _generate_params_hash(params: Dict[str, Any]) -> str:
        """
        Генерация хеша параметров
        :param params: Словарь параметров запроса
        :return: Строка с hex-представлением MD5 хеша
        """
        params_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(params_str.encode()).hexdigest()

    def save_response(self, prefix: str, params: Dict, data: Dict) -> None:
        """
        Сохранение ответа API в кэш

        Args:
            prefix: Префикс для имени файла (hh, sj и т.д.)
            params: Параметры запроса (для создания уникального ключа)
            data: Данные ответа API
        """
        try:
            # Не сохраняем пустые страницы или некорректные данные
            if not self._is_valid_response(data, params):
                logger.debug(f"Пропускаем сохранение некорректного ответа в кэш: {params}")
                return

            # Дедупликация: проверяем, нет ли уже таких же данных в кэше
            deduplicated_data = self._deduplicate_vacancies(data, prefix)
            
            cache_key = self._generate_params_hash(params)
            file_path = self.cache_dir / f"{prefix}_{cache_key}.json"

            cache_data = {"timestamp": time.time(), "meta": {"params": params}, "data": deduplicated_data}

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)

            logger.debug(f"Ответ сохранен в кэш: {file_path}")

        except Exception as e:
            logger.error(f"Ошибка сохранения в кэш: {e}")

    def _is_valid_response(self, data: Dict, params: Dict) -> bool:
        """
        Проверка валидности ответа перед сохранением в кэш

        Args:
            data: Данные ответа API
            params: Параметры запроса

        Returns:
            bool: True если ответ валиден для кэширования
        """
        try:
            # Базовая проверка структуры
            if not isinstance(data, dict):
                return False

            # Для HH/SJ API проверяем специфичную логику
            items = data.get("items", [])
            found = data.get("found", 0)
            page = params.get("page", 0)
            pages = data.get("pages", 1)

            # Не сохраняем пустые страницы, если запрашиваем страницу больше доступных
            if page > 0 and not items and page >= pages:
                logger.debug(f"Пропускаем пустую страницу {page} из {pages}")
                return False

            # Не сохраняем страницы без найденных результатов (кроме первой)
            if found == 0 and page > 0:
                logger.debug(f"Пропускаем страницу {page} - нет результатов")
                return False

            return True

        except Exception as e:
            logger.warning(f"Ошибка валидации ответа: {e}")
            return False

    def load_response(self, source: str, params: Dict[str, Any]) -> Optional[Dict]:
        """Загрузка кэшированного ответа с проверкой целостности"""
        try:
            params_hash = self._generate_params_hash(params)
            filename = f"{source}_{params_hash}.json"
            filepath = self.cache_dir / filename

            if not filepath.exists():
                return None

            # Проверяем размер файла - слишком маленькие файлы могут быть повреждены
            file_size = filepath.stat().st_size
            if file_size < 50:  # Минимальный размер для валидного JSON с мета-данными
                logger.warning(f"Файл кэша слишком маленький ({file_size} байт), удаляем: {filepath}")
                filepath.unlink()
                return None

            with open(filepath, "r", encoding="utf-8") as f:
                cached_data = json.load(f)

            # Проверяем структуру кэшированных данных
            if not self._validate_cached_structure(cached_data):
                logger.warning(f"Некорректная структура кэша, удаляем: {filepath}")
                filepath.unlink()
                return None

            return cached_data

        except (json.JSONDecodeError, OSError, Exception) as e:
            logger.warning(f"Ошибка чтения кэша {filepath}: {e}")
            # При ошибке декодирования или доступа к файлу, считаем кэш невалидным
            if filepath.exists():
                try:
                    filepath.unlink()  # Удаляем некорректный файл
                    logger.info(f"Удален поврежденный файл кэша: {filepath}")
                except OSError as e:
                    logger.error(f"Ошибка удаления некорректного файла кэша {filepath}: {e}")
            return None

    def _validate_cached_structure(self, cached_data: Dict) -> bool:
        """
        Валидация структуры кэшированных данных

        Args:
            cached_data: Загруженные из кэша данные

        Returns:
            bool: True если структура валидна
        """
        try:
            # Проверяем наличие обязательных полей кэша
            if not isinstance(cached_data, dict):
                return False

            required_fields = ["timestamp", "data", "meta"]
            for field in required_fields:
                if field not in cached_data:
                    logger.warning(f"Отсутствует обязательное поле кэша: {field}")
                    return False

            # Проверяем структуру данных
            data = cached_data.get("data", {})
            if not isinstance(data, dict):
                return False

            # Для API данных проверяем наличие items
            if "items" in data and not isinstance(data["items"], list):
                logger.warning("Поле items должно быть списком")
                return False

            return True

        except Exception as e:
            logger.error(f"Ошибка валидации структуры кэша: {e}")
            return False

    def _deduplicate_vacancies(self, data: Dict, prefix: str) -> Dict:
        """
        Дедупликация вакансий по отношению к существующим файлам кэша
        
        Args:
            data: Данные для сохранения
            prefix: Префикс источника (hh, sj)
        
        Returns:
            Dict: Очищенные от дубликатов данные
        """
        try:
            # Извлекаем новые вакансии
            new_items = data.get('items', [])
            if not new_items:
                return data
            
            # Собираем ID всех существующих вакансий в кэше
            existing_vacancy_ids = set()
            
            for cache_file in self.cache_dir.glob(f"{prefix}_*.json"):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cached_data = json.load(f)
                    
                    cached_items = cached_data.get('data', {}).get('items', [])
                    for item in cached_items:
                        vacancy_id = item.get('id')
                        if vacancy_id:
                            existing_vacancy_ids.add(str(vacancy_id))
                            
                except Exception as e:
                    logger.debug(f"Ошибка чтения файла кэша {cache_file}: {e}")
            
            # Офильтровываем новые вакансии, исключая дубликаты
            unique_items = []
            duplicates_found = 0
            
            for item in new_items:
                vacancy_id = item.get('id')
                if vacancy_id and str(vacancy_id) not in existing_vacancy_ids:
                    unique_items.append(item)
                    existing_vacancy_ids.add(str(vacancy_id))  # Добавляем к списку существующих
                elif vacancy_id:
                    duplicates_found += 1
                else:
                    unique_items.append(item)  # Вакансии без ID сохраняем
            
            if duplicates_found > 0:
                logger.debug(f"Обнаружено {duplicates_found} дубликатов, сохраняем {len(unique_items)} уникальных вакансий")
            
            # Обновляем данные с очищенным списком
            deduplicated_data = data.copy()
            deduplicated_data['items'] = unique_items
            return deduplicated_data
            
        except Exception as e:
            logger.error(f"Ошибка дедупликации: {e}")
            return data  # Возвращаем оригинальные данные при ошибке

    def clear(self, source: Optional[str] = None) -> None:
        """Очистка кэша"""
        pattern = f"{source}_*.json" if source else "*.json"
        for file in self.cache_dir.glob(pattern):
            file.unlink()
