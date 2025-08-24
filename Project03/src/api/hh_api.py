
"""
Модуль для взаимодействия с API HeadHunter с многоуровневым кэшированием
"""

import requests
import time
from typing import List, Dict, Optional
from datetime import datetime
from tqdm import tqdm
import logging
from pathlib import Path
import concurrent.futures
from threading import Lock

from ..utils.cache import FileCache, simple_cache

# Настраиваем логгер для API
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class OptimizedVacancy:
    """Оптимизированный класс для временного хранения данных вакансии"""
    
    __slots__ = ('id', 'name', 'employer_name', 'salary', 'area', 'published_at', 
                 'url', 'alternate_url', 'snippet', '_cached_details')
    
    def __init__(self, data: Dict):
        self.id = data.get('id')
        self.name = data.get('name', '')
        self.employer_name = data.get('employer', {}).get('name', '') if data.get('employer') else ''
        self.salary = data.get('salary')
        self.area = data.get('area', {}).get('name', '') if data.get('area') else ''
        self.published_at = data.get('published_at')
        self.url = data.get('url', '')
        self.alternate_url = data.get('alternate_url', '')
        self.snippet = data.get('snippet', {})
        self._cached_details = None


class HHApi:
    """
    Класс для работы с API HeadHunter с многоуровневым кэшированием.
    
    Реализует получение данных о компаниях и вакансиях через публичное API HH.ru
    с использованием двухуровневого кэша: в памяти и файловый.
    """
    
    __slots__ = ('base_url', 'headers', 'request_delay', 'cache_dir', 'cache', 
                 'target_companies', '_session', '_detail_cache', '_cache_lock')
    
    def __init__(self, cache_dir: str = "cache") -> None:
        """Инициализация API клиента с кэшем."""
        self.base_url: str = "https://api.hh.ru"
        self.headers: Dict[str, str] = {
            'User-Agent': 'HH-User-Agent'
        }
        self.request_delay: float = 0.7  # Увеличили задержку до 0.7s для избежания rate limiting
        
        # Инициализация кэша
        self.cache_dir = Path(cache_dir)
        self._init_cache()
        
        # Сессия для переиспользования соединений
        self._session = requests.Session()
        self._session.headers.update(self.headers)
        
        # Кэш деталей вакансий в памяти
        self._detail_cache = {}
        self._cache_lock = Lock()
        
        # Список целевых компаний для сбора данных
        self.target_companies: List[int] = [
            1740,    # Яндекс
            3529,    # Сбербанк  
            15478,   # VK
            64174,   # 2ГИС
            78638,   # Т-Банк (Тинькофф)
            1057,    # Лаборатория Касперского
            4934,    # билайн
            3776,    # МТС
            4181,    # Банк ВТБ (ПАО)
            3127,    # МегаФон
            2180,    # JetBrains
        ]
    
    def _init_cache(self) -> None:
        """Инициализация файлового кэша"""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache = FileCache(str(self.cache_dir))
        logger.info(f"Кэш инициализирован в директории: {self.cache_dir}")
    
    @simple_cache(ttl=300)  # Кэш в памяти на 5 минут
    def _cached_api_request(self, url: str, params: Dict, api_prefix: str) -> Dict:
        """
        Кэшированный API запрос в памяти
        
        Args:
            url: URL для запроса
            params: Параметры запроса  
            api_prefix: Префикс для логирования
            
        Returns:
            Dict: Ответ API
        """
        try:
            response = self._session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Данные получены из API для {api_prefix} (кэш в памяти)")
                time.sleep(self.request_delay)
                return data
            else:
                logger.warning(f"API ответ {response.status_code} для {api_prefix}")
                return {}
        except requests.RequestException as e:
            logger.error(f"Ошибка API запроса: {e}")
            return {}
    
    def _connect_to_api(self, url: str, params: Dict, api_prefix: str) -> Dict:
        """
        Подключение к API с многоуровневым кэшированием
        
        Реализует стратегию кэширования в три уровня:
        1. Проверка кэша в памяти (самый быстрый)
        2. Проверка файлового кэша (средний по скорости)  
        3. Реальный запрос к API с сохранением в оба кэша
        
        Args:
            url: URL для запроса
            params: Параметры запроса
            api_prefix: Префикс для кэша
            
        Returns:
            Dict: Ответ API или пустая структура при ошибке
        """
        # 1. Проверяем кэш в памяти (быстрее всего)
        try:
            memory_result = self._cached_api_request(url, params, api_prefix)
            if memory_result:
                logger.debug(f"Данные получены из кэша в памяти для {api_prefix}")
                return memory_result
        except Exception as e:
            # Логируем только в debug режиме, чтобы не мешать прогресс-барам
            logger.debug(f"Ошибка кэша памяти: {str(e)}. Переключаемся на файловый кэш")

        # 2. Проверяем файловый кэш
        cached_response = self.cache.load_response(api_prefix, params)
        if cached_response is not None:
            logger.debug(f"Данные получены из файлового кэша для {api_prefix}")
            data = cached_response.get("data", {})
            return data

        # 3. Делаем реальный запрос к API с кэшированием
        try:
            response = self._session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Данные получены из API для {api_prefix}")
                
                # Сохраняем в файловый кэш только валидные данные
                if data:
                    self.cache.save_response(api_prefix, params, data)
                    logger.debug(f"Данные сохранены в файловый кэш для {api_prefix}")
                
                time.sleep(self.request_delay)
                return data
            elif response.status_code == 403:
                # Rate limiting - делаем экспоненциальную задержку как в Project02
                retry_delay = min(self.request_delay * 6, 3.0)  # Увеличили до 6x и макс 3 сек
                logger.warning(f"Rate limiting (403) для {api_prefix}, пауза {retry_delay}s")
                time.sleep(retry_delay)
                
                # Второй шанс после паузы
                try:
                    retry_response = self._session.get(url, params=params, timeout=20)
                    if retry_response.status_code == 200:
                        data = retry_response.json()
                        if data:
                            self.cache.save_response(api_prefix, params, data)
                        return data
                    else:
                        logger.warning(f"Повторный запрос тоже неудачен: {retry_response.status_code}")
                except requests.RequestException as e:
                    logger.warning(f"Ошибка повторного запроса: {e}")
                
                return {}
            elif response.status_code == 404:
                logger.warning(f"Компания/ресурс не найден (404) для {api_prefix}")
                return None  # Возвращаем None для явного указания на отсутствие данных
            else:
                logger.warning(f"API ответ {response.status_code} для {api_prefix}")
                return {}
                
        except requests.RequestException as e:
            logger.error(f"Ошибка многоуровневого кэширования: {e}")
            return {}
    
    def get_company(self, company_id: int) -> Optional[Dict]:
        """
        Получает информацию о компании по ID с кэшированием.
        
        Args:
            company_id: ID компании в системе HH
            
        Returns:
            Optional[Dict]: Данные о компании или None при ошибке
        """
        url = f"{self.base_url}/employers/{company_id}"
        params = {}
        api_prefix = f"hh_company_{company_id}"
        
        data = self._connect_to_api(url, params, api_prefix)
        return data if data else None
    
    def get_vacancies(self, company_id: int, per_page: int = 100, max_pages: int = 10, keyword: str = None, period: int = 15) -> List[OptimizedVacancy]:
        """
        Получает список вакансий компании с кэшированием и возможностью поиска по ключевому слову.
        Возвращает оптимизированные объекты вакансий.
        
        Args:
            company_id: ID компании
            per_page: Количество вакансий на страницу
            max_pages: Максимальное количество страниц для загрузки
            keyword: Ключевое слово для поиска вакансий (опционально)
            period: Период публикации вакансий в днях (по умолчанию 15)
            
        Returns:
            List[OptimizedVacancy]: Список оптимизированных объектов вакансий
        """
        vacancies = []
        page = 0
        
        while page < max_pages:
            url = f"{self.base_url}/vacancies"
            params = {
                'employer_id': company_id,
                'page': page,
                'per_page': per_page,
                'area': 113,  # Россия
                'period': period  # Период публикации в днях
            }
            
            # Добавляем ключевое слово в поиск если указано
            if keyword:
                params['text'] = keyword
                
            # Обновляем префикс кэша с учетом ключевого слова
            api_prefix = f"hh_vacancies_{company_id}_page_{page}"
            if keyword:
                # Создаем безопасный суффикс из ключевого слова
                keyword_suffix = keyword.lower().replace(' ', '_').replace('-', '_')[:20]
                api_prefix += f"_keyword_{keyword_suffix}"
            
            data = self._connect_to_api(url, params, api_prefix)
            
            if not data:
                break
                
            page_vacancies = data.get('items', [])
            if not page_vacancies:
                break
            
            # Создаем оптимизированные объекты вакансий
            for vacancy_data in page_vacancies:
                optimized_vacancy = OptimizedVacancy(vacancy_data)
                vacancies.append(optimized_vacancy)
            
            if page >= data.get('pages', 1) - 1:
                break
                
            page += 1
        
        return vacancies
    
    def get_vacancy_details_batch(self, vacancy_ids: List[str], batch_size: int = 10) -> Dict[str, Dict]:
        """
        Получает детальную информацию о вакансиях батчами с использованием ThreadPoolExecutor
        
        Args:
            vacancy_ids: Список ID вакансий
            batch_size: Размер батча для параллельной обработки
            
        Returns:
            Dict[str, Dict]: Словарь с деталями вакансий {vacancy_id: details}
        """
        results = {}
        
        def get_single_detail(vacancy_id: str) -> tuple:
            """Получение деталей одной вакансии"""
            with self._cache_lock:
                # Проверяем кэш в памяти
                if vacancy_id in self._detail_cache:
                    return vacancy_id, self._detail_cache[vacancy_id]
            
            details = self.get_vacancy_details(vacancy_id)
            if details:
                with self._cache_lock:
                    self._detail_cache[vacancy_id] = details
                return vacancy_id, details
            return vacancy_id, None
        
        # Используем ThreadPoolExecutor для параллельных запросов
        with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
            # Отправляем все задачи
            future_to_id = {executor.submit(get_single_detail, vid): vid for vid in vacancy_ids}
            
            # Собираем результаты
            for future in concurrent.futures.as_completed(future_to_id):
                vacancy_id, details = future.result()
                if details:
                    results[vacancy_id] = details
        
        return results
    
    def get_vacancy_details(self, vacancy_id: str) -> Optional[Dict]:
        """
        Получает детальную информацию о вакансии с кэшированием.
        
        Args:
            vacancy_id: ID вакансии
            
        Returns:
            Optional[Dict]: Детальная информация о вакансии или None
        """
        url = f"{self.base_url}/vacancies/{vacancy_id}"
        params = {}
        api_prefix = f"hh_vacancy_details_{vacancy_id}"
        
        data = self._connect_to_api(url, params, api_prefix)
        return data if data else None
    
    def collect_data(self, keyword: str = None, period: int = 15, existing_vacancy_ids: set = None) -> Dict[str, List[Dict]]:
        """
        Собирает данные по всем целевым компаниям с оптимизированным кэшированием.
        
        Args:
            keyword: Ключевое слово для фильтрации вакансий (опционально)
            period: Период публикации вакансий в днях (по умолчанию 15)
            existing_vacancy_ids: Множество ID уже существующих вакансий для исключения
        
        Returns:
            Dict[str, List[Dict]]: Словарь с компаниями и вакансиями
        """
        keyword_info = f" по ключевому слову '{keyword}'" if keyword else ""
        period_info = f" за последние {period} дней"
        print(f"🔄 Начинаем сбор данных по {len(self.target_companies)} компаниям{keyword_info}{period_info}...")
        
        # Этап 1: Собираем информацию о компаниях и списки вакансий
        print(f"\n📊 Этап 1: Сбор информации о компаниях и списков вакансий{keyword_info}...")
        companies_cache = []
        optimized_vacancies = []
        
        # Общий прогресс-бар для компаний
        with tqdm(total=len(self.target_companies), desc="📈 Общий прогресс", 
                  position=0, leave=True,
                  bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} компаний [{elapsed}<{remaining}]") as main_pbar:
            
            for company_id in self.target_companies:
                # Получаем данные компании
                company_info = self.get_company(company_id)
                if company_info:
                    company_name = company_info.get('name', f'ID: {company_id}')
                    main_pbar.set_description(f"📈 Получение вакансий: {company_name[:25]}")
                    
                    companies_cache.append(company_info)
                    
                    # Получаем список вакансий с использованием оптимизированных объектов
                    company_vacancies = self.get_vacancies_with_progress(company_id, company_name, keyword=keyword, period=period)
                    optimized_vacancies.extend(company_vacancies[:50])  # Ограничиваем 50 вакансиями на компанию
                    
                    main_pbar.set_postfix_str(f"✅ {len(company_vacancies)} вакансий")
                else:
                    main_pbar.set_description(f"📈 Ошибка: ID {company_id}")
                    main_pbar.set_postfix_str("❌ Не удалось получить данные")
                
                main_pbar.update(1)
        
        print(f"\n✅ Этап 1 завершен: {len(companies_cache)} компаний, {len(optimized_vacancies)} вакансий для детализации")
        
        # Этап 2: Фильтруем и получаем детальную информацию о вакансиях БАТЧАМИ
        # Сначала исключаем уже существующие вакансии
        if existing_vacancy_ids is None:
            existing_vacancy_ids = set()
        
        new_vacancies = []
        excluded_count = 0
        
        for v in optimized_vacancies:
            if v.id and str(v.id) not in existing_vacancy_ids:
                new_vacancies.append(v)
            else:
                excluded_count += 1
        
        if excluded_count > 0:
            print(f"⚡ Исключено {excluded_count} уже существующих вакансий из обработки")
        
        # Отбираем вакансии с зарплатой или с важными ключевыми словами или недавно опубликованные
        important_keywords = ['senior', 'lead', 'principal', 'architect', 'manager', 'director', 'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node', 'django', 'flask', 'spring']
        
        filtered_vacancies = []
        for i, v in enumerate(new_vacancies):
            has_salary = v.salary is not None
            has_important_keyword = any(kw in v.name.lower() for kw in important_keywords) if v.name else False
            # Берем первые 30% вакансий (обычно самые свежие и релевантные)
            is_top_vacancy = i < len(new_vacancies) * 0.3
            
            if has_salary or has_important_keyword or is_top_vacancy:
                filtered_vacancies.append(v)
        
        print(f"\n🔍 Этап 2: Ускоренное получение деталей о {len(filtered_vacancies)} вакансиях (из {len(optimized_vacancies)} отфильтровано)")
        detailed_vacancies = []
        
        # Извлекаем ID вакансий только отфильтрованных
        vacancy_ids = [v.id for v in filtered_vacancies if v.id]
        
        # Обрабатываем батчами для ускорения
        batch_size = 20  # Увеличили размер батча
        total_batches = (len(vacancy_ids) + batch_size - 1) // batch_size
        
        with tqdm(total=len(vacancy_ids), desc="🔍 Детализация важных вакансий ",
                  bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as details_pbar:
            
            for i in range(0, len(vacancy_ids), batch_size):
                batch_ids = vacancy_ids[i:i + batch_size]
                batch_results = self.get_vacancy_details_batch(batch_ids, batch_size=10)
                
                # Добавляем результаты
                for vacancy_id, details in batch_results.items():
                    if details:
                        detailed_vacancies.append(details)
                
                details_pbar.update(len(batch_ids))
                details_pbar.set_postfix_str(f"Батч {i//batch_size + 1}/{total_batches}")
        
        all_data = {
            'companies': companies_cache,
            'vacancies': detailed_vacancies
        }
        
        print(f"\n✅ Ускоренный сбор завершен: {len(all_data['companies'])} компаний, {len(all_data['vacancies'])} детализированных вакансий")
        
        return all_data
    
    def get_vacancies_with_progress(self, company_id: int, company_name: str, per_page: int = 100, max_pages: int = 10, keyword: str = None, period: int = 15) -> List[OptimizedVacancy]:
        """
        Получает список вакансий компании с прогресс-баром и кэшированием.
        Возвращает оптимизированные объекты вакансий.
        
        Args:
            company_id: ID компании
            company_name: Название компании для отображения
            per_page: Количество вакансий на страницу
            max_pages: Максимальное количество страниц для загрузки
            keyword: Ключевое слово для поиска вакансий (опционально)
            period: Период публикации вакансий в днях (по умолчанию 15)
            
        Returns:
            List[OptimizedVacancy]: Список оптимизированных объектов вакансий
        """
        vacancies = []
        
        # Сначала получаем общее количество вакансий из кэша или API
        url = f"{self.base_url}/vacancies"
        params = {
            'employer_id': company_id,
            'page': 0,
            'per_page': 1,
            'area': 113,  # Россия
            'period': period  # Период публикации в днях
        }
        
        # Добавляем ключевое слово в поиск если указано
        if keyword:
            params['text'] = keyword
            
        # Обновляем префикс кэша с учетом ключевого слова
        api_prefix = f"hh_vacancies_info_{company_id}"
        if keyword:
            keyword_suffix = keyword.lower().replace(' ', '_').replace('-', '_')[:20]
            api_prefix += f"_keyword_{keyword_suffix}"
        
        data = self._connect_to_api(url, params, api_prefix)
        
        if not data:
            print(f"   ❌ Ошибка получения информации о вакансиях")
            return []
        
        total_found = data.get('found', 0)
        total_pages = min(data.get('pages', 1), max_pages)
        
        if total_found == 0:
            print(f"   📝 Вакансий не найдено")
            return []
        
        # Прогресс-бар для страниц вакансий  
        with tqdm(total=total_pages, desc=f"   📄 Страницы", 
                  bar_format="   {l_bar}{bar}| {n_fmt}/{total_fmt} стр. [{elapsed}]",
                  leave=False) as page_pbar:
            
            for page in range(total_pages):
                params = {
                    'employer_id': company_id,
                    'page': page,
                    'per_page': per_page,
                    'area': 113,
                    'period': period  # Период публикации в днях
                }
                
                # Добавляем ключевое слово в поиск если указано
                if keyword:
                    params['text'] = keyword
                    
                # Обновляем префикс кэша с учетом ключевого слова
                api_prefix = f"hh_vacancies_{company_id}_page_{page}"
                if keyword:
                    keyword_suffix = keyword.lower().replace(' ', '_').replace('-', '_')[:20]
                    api_prefix += f"_keyword_{keyword_suffix}"
                
                data = self._connect_to_api(url, params, api_prefix)
                
                if not data:
                    page_pbar.set_postfix_str(f"ошибка API")
                    break
                    
                page_vacancies = data.get('items', [])
                if not page_vacancies:
                    break
                
                # Создаем оптимизированные объекты вакансий
                for vacancy_data in page_vacancies:
                    optimized_vacancy = OptimizedVacancy(vacancy_data)
                    vacancies.append(optimized_vacancy)
                
                page_pbar.set_postfix_str(f"получено {len(vacancies)}")
                page_pbar.update(1)
        
        return vacancies
    
    def clear_cache(self, api_prefix: str = "hh") -> None:
        """
        Очистка кэша для HH API
        
        Args:
            api_prefix: Префикс API для очистки
        """
        try:
            # Очищаем файловый кэш
            self.cache.clear(api_prefix)
            
            # Очищаем кэш в памяти
            if hasattr(self._cached_api_request, "clear_cache"):
                self._cached_api_request.clear_cache()
            
            # Очищаем кэш деталей
            with self._cache_lock:
                self._detail_cache.clear()
                
            logger.info(f"Кэш {api_prefix} очищен (файловый и в памяти)")
            print(f"✅ Кэш {api_prefix} очищен")
        except Exception as e:
            logger.error(f"Ошибка очистки кэша {api_prefix}: {e}")
            print(f"❌ Ошибка очистки кэша: {e}")
    
    def get_cache_status(self) -> Dict:
        """
        Получение статуса кэша для диагностики
        
        Returns:
            Dict: Информация о состоянии кэша
        """
        try:
            cache_files = self.cache.get_cache_files("hh")
            memory_info = {}
            if hasattr(self._cached_api_request, "cache_info"):
                memory_info = self._cached_api_request.cache_info()

            status = {
                "cache_dir": str(self.cache_dir),
                "cache_dir_exists": self.cache_dir.exists(),
                "file_cache_count": len(cache_files),
                "cache_files": [f.name for f in cache_files],
                "memory_cache": memory_info,
                "detail_cache_size": len(self._detail_cache),
            }
            
            logger.info(f"Статус кэша: {status}")
            return status
        except Exception as e:
            logger.error(f"Ошибка получения статуса кэша: {e}")
            return {"error": str(e)}
    
    def __del__(self):
        """Закрытие сессии при удалении объекта"""
        if hasattr(self, '_session') and self._session:
            self._session.close()
