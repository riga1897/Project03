"""
Модуль для загрузки данных из API в базу данных
"""

import json
import os
import time
from typing import Dict, List
from datetime import datetime, timedelta

from src.api import HHApi
from src.database import DatabaseSetup, DBManager


class DataLoader:
    """
    Класс для загрузки данных в базу данных.

    Координирует процесс получения данных из API HeadHunter
    и их загрузку в PostgreSQL базу данных.
    """

    def __init__(self, db_manager: DBManager = None, api: HHApi = None) -> None:
        """Инициализация загрузчика данных."""
        self.api: HHApi = api or HHApi()
        self.db_setup: DatabaseSetup = DatabaseSetup()
        self.db_manager: DBManager = db_manager or DBManager()
        # Создаем папку для кэша если её нет
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.cache_dir: str = os.path.join(project_root, "cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.cache_file: str = os.path.join(self.cache_dir, "hh_data_cache.json")
        self.cache_meta_file: str = os.path.join(self.cache_dir, "cache_metadata.json")
        self.cache_expiry_hours: int = 24  # Кэш действует 24 часа

    def show_progress_bar(self, current: int, total: int, prefix: str = "", suffix: str = "", length: int = 40) -> None:
        """
        Отображает прогресс-бар в консоли.

        Args:
            current: Текущий прогресс
            total: Общее количество
            prefix: Префикс для прогресс-бара
            suffix: Суффикс для прогресс-бара  
            length: Длина прогресс-бара
        """
        if total == 0:
            return

        percent = current / total
        filled_length = int(length * percent)
        bar = '█' * filled_length + '░' * (length - filled_length)

        print(f'\r{prefix} |{bar}| {current}/{total} ({percent:.1%}) {suffix}', end='', flush=True)

        if current == total:
            print()  # Новая строка в конце

    def is_cache_valid(self) -> bool:
        """
        Проверяет, действителен ли кэш.

        Returns:
            bool: True если кэш действителен
        """
        if not os.path.exists(self.cache_file) or not os.path.exists(self.cache_meta_file):
            return False

        try:
            with open(self.cache_meta_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            cache_time = datetime.fromisoformat(metadata.get('created_at', ''))
            expiry_time = cache_time + timedelta(hours=self.cache_expiry_hours)

            is_valid = datetime.now() < expiry_time

            if is_valid:
                time_left = expiry_time - datetime.now()
                hours_left = int(time_left.total_seconds() / 3600)
                print(f"📂 Кэш действителен еще {hours_left} часов")
            else:
                print("⏰ Кэш устарел, будут загружены новые данные")

            return is_valid

        except Exception as e:
            print(f"⚠️ Ошибка проверки кэша: {e}")
            return False

    def save_cache_metadata(self, companies_count: int, vacancies_count: int) -> None:
        """
        Сохраняет метаданные кэша.

        Args:
            companies_count: Количество компаний
            vacancies_count: Количество вакансий
        """
        metadata = {
            'created_at': datetime.now().isoformat(),
            'companies_count': companies_count,
            'vacancies_count': vacancies_count,
            'expiry_hours': self.cache_expiry_hours
        }

        try:
            with open(self.cache_meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Ошибка сохранения метаданных: {e}")

    def load_cache_metadata(self) -> Dict:
        """
        Загружает метаданные кэша.

        Returns:
            Dict: Метаданные кэша
        """
        try:
            if os.path.exists(self.cache_meta_file):
                with open(self.cache_meta_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Ошибка загрузки метаданных: {e}")

        return {}

    def setup_database(self) -> bool:
        """
        Настраивает базу данных (создает таблицы).

        Returns:
            bool: True если настройка прошла успешно
        """
        print("\n📦 Настройка базы данных...")

        if not self.db_setup.test_connection():
            print("✗ Не удалось подключиться к БД")
            return False

        if not self.db_setup.create_tables():
            print("✗ Не удалось создать таблицы")
            return False

        return True

    def collect_data(self, use_cache: bool = True, keyword: str = None, period: int = 15) -> Dict[str, List[Dict]]:
        """
        Собирает данные из базы данных, файлового кэша и API в правильном порядке.

        Args:
            use_cache: Использовать кэшированные данные если доступны
            keyword: Ключевое слово для поиска
            period: Период публикации вакансий в днях

        Returns:
            Dict[str, List[Dict]]: Словарь с компаниями и вакансиями
        """
        # 1. Сначала инициализируем базу данных если нужно
        print("\n📦 Проверка инициализации базы данных...")
        if not self.setup_database():
            print("⚠️ Ошибка инициализации базы данных, продолжаем без неё")

        # 2. Проверяем файловый кэш только если он свежий
        if use_cache and self._is_cache_valid():
            print(f"📂 Загрузка данных из файлового кэша: {self.cache_file}")
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✅ Загружено из кэша: {len(data.get('companies', []))} компаний, {len(data.get('vacancies', []))} вакансий")
                return data
            except Exception as e:
                print(f"⚠️ Ошибка чтения кэша: {e}")
                print("🔄 Переходим к загрузке из базы и API...")

        # 3. Получаем данные из базы данных для кэширования (базовый источник истины)
        print("\n🗃️ Загрузка существующих данных из базы в кэш...")
        db_cache = self.db_manager.get_database_cache(self.api.target_companies)
        existing_vacancy_ids = self.db_manager.get_existing_vacancy_ids(self.api.target_companies)
        existing_company_ids = self.db_manager.get_existing_company_ids()

        print(f"📊 В базе найдено: {len(db_cache.get('companies', []))} компаний, {len(db_cache.get('vacancies', []))} вакансий")

        # 4. Определяем, какие компании нужно загрузить из API
        companies_to_fetch = [cid for cid in self.api.target_companies if cid not in existing_company_ids]
        print(f"🆕 Нужно загрузить из API: {len(companies_to_fetch)} новых компаний")

        # 5. Получаем недостающие данные из API (только если нужно)
        if companies_to_fetch or len(db_cache.get('vacancies', [])) == 0:
            print(f"\n🌐 Получение {'новых ' if db_cache.get('vacancies') else ''}данных из API HeadHunter...")
            if existing_vacancy_ids:
                print(f"⚡ Будут исключены {len(existing_vacancy_ids)} уже существующих вакансий")
            
            api_data = self.api.collect_data(keyword=keyword, period=period, existing_vacancy_ids=existing_vacancy_ids)
        else:
            print(f"\n✅ Все необходимые данные уже есть в базе, API запросы не нужны")
            api_data = {'companies': [], 'vacancies': []}

        # 6. Объединяем данные из базы и API
        combined_data = self._merge_data(db_cache, api_data)
        
        # 7. Сохраняем объединенные данные в файловый кэш
        self._save_to_cache(combined_data)

        print(f"✅ Итого собрано: {len(combined_data.get('companies', []))} компаний, {len(combined_data.get('vacancies', []))} вакансий")

        return combined_data

    def _merge_data(self, db_data: Dict[str, List[Dict]], api_data: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """
        Объединяет данные из базы и API, избегая дублирования.

        Args:
            db_data: Данные из базы данных
            api_data: Данные из API

        Returns:
            Dict[str, List[Dict]]: Объединенные данные
        """
        # Объединяем компании, избегая дублирования по ID
        db_company_ids = {comp.get('id') for comp in db_data.get('companies', [])}
        api_companies = [comp for comp in api_data.get('companies', []) 
                        if comp.get('id') not in db_company_ids]
        
        combined_companies = list(db_data.get('companies', [])) + api_companies

        # Объединяем вакансии, избегая дублирования по ID
        db_vacancy_ids = {vac.get('id') for vac in db_data.get('vacancies', [])}
        api_vacancies = [vac for vac in api_data.get('vacancies', []) 
                        if vac.get('id') not in db_vacancy_ids]
        
        combined_vacancies = list(db_data.get('vacancies', [])) + api_vacancies

        if api_companies or api_vacancies:
            print(f"🔄 Объединение данных: +{len(api_companies)} компаний, +{len(api_vacancies)} вакансий из API")

        return {
            'companies': combined_companies,
            'vacancies': combined_vacancies
        }

    def _is_cache_valid(self) -> bool:
        """
        Проверяет валидность кэша.

        Returns:
            bool: True если кэш существует и валиден
        """
        if not os.path.exists(self.cache_file):
            return False

        try:
            # Проверяем возраст файла (кэш действителен 24 часа)
            import time
            file_age = time.time() - os.path.getmtime(self.cache_file)
            if file_age > 24 * 60 * 60:  # 24 часа в секундах
                print("⏰ Кэш устарел (старше 24 часов)")
                return False

            # Проверяем структуру данных
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, dict) or 'companies' not in data or 'vacancies' not in data:
                    print("🔍 Некорректная структура кэша")
                    return False

            return True
        except Exception:
            return False

    def _save_to_cache(self, data: Dict[str, List[Dict]]) -> None:
        """
        Сохраняет данные в кэш с метаданными.

        Args:
            data: Данные для сохранения
        """
        try:
            from datetime import datetime

            # Добавляем метаданные
            cache_data = {
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'companies_count': len(data.get('companies', [])),
                    'vacancies_count': len(data.get('vacancies', []))
                },
                'companies': data.get('companies', []),
                'vacancies': data.get('vacancies', [])
            }

            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2, default=str)

            print(f"💾 Данные сохранены в кэш: {self.cache_file}")
            print(f"📊 Кэш содержит: {cache_data['metadata']['companies_count']} компаний, {cache_data['metadata']['vacancies_count']} вакансий")

        except Exception as e:
            print(f"⚠️ Ошибка сохранения кэша: {e}")

    def load_to_database(self, data: Dict[str, List[Dict]]) -> bool:
        """
        Загружает данные в базу данных.

        Args:
            data: Словарь с компаниями и вакансиями

        Returns:
            bool: True если загрузка прошла успешно
        """
        print("\n📥 Загрузка данных в PostgreSQL...")

        companies = data.get('companies', [])
        vacancies = data.get('vacancies', [])

        if not companies or not vacancies:
            print("✗ Нет данных для загрузки")
            return False

        print(f"📊 Данные для загрузки:")
        print(f"  • Компаний: {len(companies)}")
        print(f"  • Вакансий: {len(vacancies)}")

        # Загружаем компании
        if not self.db_manager.insert_companies(companies):
            print("✗ Ошибка загрузки компаний")
            return False

        # Загружаем вакансии
        if not self.db_manager.insert_vacancies(vacancies):
            print("✗ Ошибка загрузки вакансий")
            return False

        return True

    def verify_data(self) -> None:
        """Проверяет и выводит статистику загруженных данных."""
        print("\n📊 Проверка загруженных данных...")

        # Получаем компании с количеством вакансий
        companies = self.db_manager.get_companies_and_vacancies_count()
        if companies:
            print(f"\n✓ Компании в базе данных ({len(companies)}):")
            for i, company in enumerate(companies[:5], 1):
                print(f"  {i}. {company['company_name']}: {company['vacancies_count']} вакансий")
            if len(companies) > 5:
                print(f"  ... и еще {len(companies) - 5} компаний")

        # Средняя зарплата
        avg_salary = self.db_manager.get_avg_salary()
        if avg_salary:
            print(f"\n💰 Средняя зарплата: {avg_salary:,.0f} руб.")

        # Примеры вакансий с Python
        python_vacancies = self.db_manager.get_vacancies_with_keyword("python")
        if python_vacancies:
            print(f"\n🐍 Найдено Python вакансий: {len(python_vacancies)}")
            for vacancy in python_vacancies[:3]:
                salary_info = ""
                if vacancy.get('salary_from') or vacancy.get('salary_to'):
                    if vacancy.get('salary_from'):
                        salary_info = f" (от {vacancy['salary_from']:,} руб.)"
                print(f"  • {vacancy['vacancy_name']} в {vacancy['company_name']}{salary_info}")

    def run_full_process(self, use_cache: bool = True) -> bool:
        """
        Запускает полный процесс загрузки данных.

        Args:
            use_cache: Использовать кэшированные данные если доступны

        Returns:
            bool: True если процесс завершен успешно
        """
        print("=" * 60)
        print("ЗАГРУЗКА ДАННЫХ HEADHUNTER В POSTGRESQL")
        print("=" * 60)

        # Настройка БД
        if not self.setup_database():
            return False

        # Сбор данных
        data = self.collect_data(use_cache)
        if not data:
            print("✗ Не удалось получить данные")
            return False

        # Загрузка в БД
        if not self.load_to_database(data):
            return False

        # Проверка данных
        self.verify_data()

        print("\n" + "=" * 60)
        print("✓ ЗАГРУЗКА ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 60)

        return True

    def run_full_process_with_params(self, use_cache: bool = True, keyword: str = None, period: int = 15) -> bool:
        """
        Запускает полный процесс загрузки данных с параметрами.

        Args:
            use_cache: Использовать кэшированные данные если доступны
            keyword: Ключевое слово для поиска
            period: Период публикации вакансий в днях

        Returns:
            bool: True если процесс завершен успешно
        """
        print("=" * 60)
        print("ЗАГРУЗКА ДАННЫХ HEADHUNTER В POSTGRESQL")
        print("=" * 60)

        # Сбор данных с параметрами (инициализация БД происходит внутри collect_data)
        data = self.collect_data(use_cache, keyword, period)
        if not data:
            print("✗ Не удалось получить данные")
            return False

        # Загрузка в БД только новых данных
        new_companies = [c for c in data.get('companies', []) 
                        if c.get('id') not in self.db_manager.get_existing_company_ids()]
        existing_vacancy_ids = self.db_manager.get_existing_vacancy_ids()
        new_vacancies = [v for v in data.get('vacancies', []) 
                        if v.get('id') not in existing_vacancy_ids]

        if new_companies or new_vacancies:
            filtered_data = {
                'companies': new_companies,
                'vacancies': new_vacancies
            }
            
            if not self.load_to_database(filtered_data):
                return False
        else:
            print("✓ Новых данных для загрузки не найдено")

        # Проверка данных
        self.verify_data()

        print("\n" + "=" * 60)
        print("✓ ЗАГРУЗКА ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 60)

        return True


    def clear_cache(self) -> bool:
        """
        Очищает кэш данных.

        Returns:
            bool: True если кэш успешно очищен
        """
        try:
            files_to_remove = [self.cache_file, self.cache_meta_file]
            removed_count = 0

            for file_path in files_to_remove:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    removed_count += 1

            if removed_count > 0:
                print(f"🗑️ Кэш очищен ({removed_count} файлов удалено)")
                return True
            else:
                print("📂 Кэш уже пуст")
                return False

        except Exception as e:
            print(f"❌ Ошибка очистки кэша: {e}")
            return False

    def get_cache_info(self) -> Dict:
        """
        Получает информацию о кэше.

        Returns:
            Dict: Информация о кэше
        """
        info = {
            'exists': os.path.exists(self.cache_file),
            'valid': False,
            'size_mb': 0,
            'created_at': None,
            'companies_count': 0,
            'vacancies_count': 0
        }

        if info['exists']:
            try:
                # Размер файла
                size_bytes = os.path.getsize(self.cache_file)
                info['size_mb'] = round(size_bytes / (1024 * 1024), 2)

                # Метаданные
                metadata = self.load_cache_metadata()
                if metadata:
                    info['created_at'] = metadata.get('created_at')
                    info['companies_count'] = metadata.get('companies_count', 0)
                    info['vacancies_count'] = metadata.get('vacancies_count', 0)

                # Проверка валидности
                info['valid'] = self.is_cache_valid()

            except Exception as e:
                print(f"⚠️ Ошибка получения информации о кэше: {e}")

        return info

    def load_data(self, use_cache: bool = True) -> bool:
        """
        Основной метод для загрузки данных (интерфейс для UI).
        
        Args:
            use_cache: Использовать кэшированные данные если доступны
            
        Returns:
            bool: True если загрузка прошла успешно
        """
        return self.run_full_process(use_cache)

    def load_data_with_params(self, use_cache: bool = True, keyword: str = None, period: int = 15) -> bool:
        """
        Основной метод для загрузки данных с параметрами (интерфейс для UI).
        
        Args:
            use_cache: Использовать кэшированные данные если доступны
            keyword: Ключевое слово для поиска
            period: Период публикации вакансий в днях
            
        Returns:
            bool: True если загрузка прошла успешно
        """
        return self.run_full_process_with_params(use_cache, keyword, period)