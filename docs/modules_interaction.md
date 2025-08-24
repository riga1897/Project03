
# Схема взаимодействия модулей

## Диаграмма взаимодействия

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   main.py        │    │  ConsoleInterface│    │  MenuManager     │
│  (точка входа)   │───▶│  (главный UI)    │───▶│  (управление     │
└──────────────────┘    └──────────────────┘    │   меню)          │
                                 │              └──────────────────┘
                                 ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ SourceSelector   │    │VacancySearchHandler│   │VacancyDisplayHandler│
│ (выбор источника)│◀───│ (обработка поиска) │───│ (отображение)    │
└──────────────────┘    └──────────────────┘    └──────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   UnifiedAPI     │    │ VacancyOperations│    │ VacancyFormatter │
│ (единый API)     │    │ (операции с      │    │ (форматирование) │
│                  │    │  вакансиями)     │    │                  │
└──────────────────┘    └──────────────────┘    └──────────────────┘
         │                        │                        
         ▼                        ▼                        
┌──────────────────┐    ┌──────────────────┐              
│  HeadHunterAPI   │    │  PostgresSaver   │              
│  SuperJobAPI     │    │  JSONSaver       │              
│  (конкретные API)│    │  (хранилища)     │              
└──────────────────┘    └──────────────────┘              
         │                        │                        
         ▼                        ▼                        
┌──────────────────┐    ┌──────────────────┐              
│   CachedAPI      │    │  Vacancy Model   │              
│  (кэширование)   │    │  Salary Model    │              
└──────────────────┘    └──────────────────┘              
```

## Потоки данных

### 1. Поиск новых вакансий

```
Пользователь → ConsoleInterface → SourceSelector → UnifiedAPI
                     ↓
               HeadHunterAPI/SuperJobAPI → CachedAPI → Внешний API
                     ↓
               Vacancy.from_dict() → VacancyOperations → PostgresSaver
                     ↓
               VacancyFormatter → VacancyDisplayHandler → Пользователь
```

**Описание потока**:
1. Пользователь вводит поисковый запрос
2. Система предлагает выбрать источники данных
3. UnifiedAPI координирует запросы к выбранным API
4. Данные кэшируются для оптимизации
5. Сырые данные преобразуются в объекты Vacancy
6. Вакансии сохраняются в базу данных
7. Результаты форматируются и отображаются

### 2. Работа с сохраненными вакансиями

```
Пользователь → ConsoleInterface → VacancyOperationsCoordinator
                     ↓
               VacancyDisplayHandler → VacancyOperations → PostgresSaver
                     ↓                      ↓
               VacancyFormatter ← SearchUtils (ui_helpers)
                     ↓
               Paginator → VacancyDisplayHandler → Пользователь
```

### 4. Удаление вакансий

```
Пользователь → ConsoleInterface → VacancyOperationsCoordinator
                     ↓
               MenuManager → _handle_delete_by_keyword()
                     ↓
               ui_helpers.filter_vacancies_by_keyword → VacancyOperations.search_vacancies_advanced
                     ↓
               PostgresSaver.delete_vacancies_by_keyword → Пользователь
```

### 5. Кэширование и оптимизация

```
API Request → CachedAPI → Cache.get()
                ↓              ↓
        APIConnector ← Cache miss → External API
                ↓              ↓
        Cache.set() ← Response data → Vacancy.from_dict()
                ↓
        Return cached data
```

**Описание потока**:
1. Пользователь выбирает операцию с сохраненными данными
2. VacancyOperations загружает данные из хранилища
3. Применяются фильтры и поиск
4. Результаты пагинируются и форматируются
5. Данные отображаются пользователю

### 3. Конфигурация системы

```
EnvLoader → DatabaseConfig → PostgresSaver
     ↓              ↓
APIConfig → HeadHunterAPI/SuperJobAPI → CachedAPI
     ↓              ↓
UIConfig → ConsoleInterface → VacancyDisplayHandler → Paginator
                    ↓
        VacancyOperationsCoordinator → MenuManager
```

#### Детальное взаимодействие конфигураций
```python
# EnvLoader загружает переменные окружения
class EnvLoader:
    @staticmethod
    def load_environment():
        load_dotenv()
        return {
            'db_config': DatabaseConfig().get_config(),
            'api_config': APIConfig().get_config(),
            'ui_config': UIConfig().get_pagination_config()
        }

# DatabaseConfig используется в PostgresSaver
class PostgresSaver:
    def __init__(self, db_config=None):
        self.config = db_config or DatabaseConfig().get_config()
        self.connection = self._create_connection()

# APIConfig влияет на все API модули
class HeadHunterAPI:
    def __init__(self):
        self.config = HHAPIConfig()
        self.base_url = self.config.get_base_url()
        self.timeout = APIConfig().get_timeout()

# UIConfig используется в пагинации и отображении
class VacancyDisplayHandler:
    def show_all_saved_vacancies(self):
        items_per_page = ui_pagination_config.get_items_per_page("saved")
        quick_paginate(vacancies, items_per_page=items_per_page)
```

### Координация операций

#### VacancyOperationsCoordinator - медиатор системы
```python
class VacancyOperationsCoordinator:
    def __init__(self, unified_api, storage):
        self.unified_api = unified_api
        self.storage = storage
        # Создание зависимых обработчиков
        self.search_handler = VacancySearchHandler(unified_api, storage)
        self.display_handler = VacancyDisplayHandler(storage)
    
    def handle_vacancy_search(self):
        # Делегирует поиск VacancySearchHandler
        self.search_handler.search_vacancies()
    
    def handle_delete_by_keyword(self, vacancies):
        # Использует ui_helpers для фильтрации
        filtered_vacancies = filter_vacancies_by_keyword(vacancies, keyword)
        # Координирует удаление через storage
        deleted_count = self.storage.delete_vacancies_by_keyword(keyword)
```

#### Взаимодействие VacancySearchHandler с хранилищем
```python
class VacancySearchHandler:
    def _check_existing_vacancies(self, vacancies):
        # Batch проверка существования для PostgreSQL
        if hasattr(self.json_saver, 'check_vacancies_exist_batch'):
            existence_map = self.json_saver.check_vacancies_exist_batch(vacancies)
        else:
            # Fallback для других хранилищ
            for vacancy in vacancies:
                if self.json_saver.is_vacancy_exists(vacancy):
                    duplicates.append(vacancy)
```

## Детальное взаимодействие модулей

### API слой

#### UnifiedAPI - центральный координатор
```python
class UnifiedAPI:
    def __init__(self):
        self.hh_api = HeadHunterAPI()      # Подключение HH API
        self.sj_api = SuperJobAPI()        # Подключение SJ API
    
    def search_vacancies(self, sources, query):
        results = []
        if 'hh' in sources:
            results.extend(self.hh_api.get_vacancies(query))
        if 'sj' in sources:
            results.extend(self.sj_api.get_vacancies(query))
        return self._deduplicate(results)
```

#### Взаимодействие с кэшем
```python
class CachedAPI:
    def __connect_to_api(self, url, params, source):
        cache_key = self._generate_cache_key(url, params)
        
        # Проверка кэша
        if cached_data := self._get_from_cache(cache_key):
            return cached_data
            
        # Запрос к API
        data = self.connector.connect(url, params)
        
        # Сохранение в кэш
        self._save_to_cache(cache_key, data)
        return data
```

### Слой данных

#### Взаимодействие с базой данных
```python
class PostgresSaver:
    def add_vacancy(self, vacancies):
        # Batch проверка существования
        existing = self._check_existing_batch(vacancies)
        
        # Разделение на новые и обновляемые
        new_vacancies = [v for v in vacancies if not existing[v.id]]
        update_vacancies = [v for v in vacancies if existing[v.id]]
        
        # Batch операции
        self._batch_insert(new_vacancies)
        self._batch_update(update_vacancies)

    def check_vacancies_exist_batch(self, vacancies):
        # Batch проверка для оптимизации
        vacancy_ids = [v.vacancy_id for v in vacancies]
        query = "SELECT vacancy_id FROM vacancies WHERE vacancy_id = ANY(%s)"
        existing_ids = self._execute_query(query, (vacancy_ids,))
        return {v_id: v_id in existing_ids for v_id in vacancy_ids}
```

#### Взаимодействие утилит с основными модулями
```python
# ui_helpers -> VacancyOperations
def filter_vacancies_by_keyword(vacancies, keyword):
    # Может делегировать сложный поиск в VacancyOperations
    if " AND " in keyword or " OR " in keyword:
        return VacancyOperations.search_vacancies_advanced(vacancies, keyword)
    else:
        # Простая фильтрация
        return [v for v in vacancies if vacancy_contains_keyword(v, keyword)]

# VacancyFormatter -> Salary утилиты
class VacancyFormatter:
    def format_salary(self, salary):
        # Использует утилиты из src.utils.salary
        return format_salary_range(salary.salary_from, salary.salary_to, salary.currency)

# SearchUtils -> VacancyOperations
def advanced_search(vacancies, criteria):
    # Комбинирует различные методы VacancyOperations
    result = VacancyOperations.filter_vacancies_by_salary_range(vacancies, min_sal, max_sal)
    result = VacancyOperations.search_vacancies_advanced(result, keywords)
    return VacancyOperations.sort_vacancies_by_salary(result)
```

#### Преобразование данных через парсеры
```python
# API -> Parser -> Vacancy
class HeadHunterAPI:
    def get_vacancies(self, query):
        raw_data = self._fetch_from_api(query)
        # Делегирует парсинг специализированному парсеру
        return [HHParser.parse_vacancy(item) for item in raw_data['items']]

class HHParser:
    @staticmethod
    def parse_vacancy(raw_vacancy):
        # Специализированный парсинг для HH.ru
        return Vacancy(
            title=raw_vacancy.get('name'),
            salary=HHParser.parse_salary(raw_vacancy.get('salary')),
            employer=HHParser.parse_employer(raw_vacancy.get('employer')),
            # ... другие поля
        )

class SuperJobAPI:
    def get_vacancies(self, query):
        raw_data = self._fetch_from_api(query)
        # Использует свой парсер
        return [SJParser.parse_vacancy(item) for item in raw_data['objects']]

# Универсальное создание через фабрику
class Vacancy:
    @classmethod
    def from_dict(cls, data, source='unknown'):
        # Определяет какой парсер использовать
        if source == 'hh':
            return HHParser.parse_vacancy(data)
        elif source == 'sj':
            return SJParser.parse_vacancy(data)
        else:
            # Универсальное преобразование
            return cls._generic_parse(data)
```

### UI слой

#### Управление интерфейсом
```python
class ConsoleInterface:
    def run(self):
        while True:
            choice = self.menu_manager.show_main_menu()
            
            if choice == '1':
                self.search_handler.handle_search()
            elif choice == '2':
                self.display_handler.show_saved_vacancies()
            # ... другие опции
```

#### Отображение данных и взаимодействие с VacancyOperations
```python
class VacancyDisplayHandler:
    def __init__(self, storage):
        self.storage = storage
        self.vacancy_ops = VacancyOperations()  # Создание экземпляра
    
    def show_top_vacancies_by_salary(self):
        vacancies = self.storage.get_vacancies()
        
        # Используем VacancyOperations для фильтрации
        vacancies_with_salary = self.vacancy_ops.get_vacancies_with_salary(vacancies)
        
        # Используем VacancyOperations для сортировки
        sorted_vacancies = self.vacancy_ops.sort_vacancies_by_salary(vacancies_with_salary)
        
        # Форматирование и отображение
        formatted = self.formatter.format_list(sorted_vacancies)
        paginated = self.paginator.paginate(formatted)
    
    def search_saved_vacancies_by_keyword(self):
        vacancies = self.storage.get_vacancies()
        
        # Делегируем поиск в VacancyOperations через ui_helpers
        filtered_vacancies = filter_vacancies_by_keyword(vacancies, keyword)
        
        # Отображение результатов
        formatted = self.formatter.format_list(filtered_vacancies)
```

## Жизненный цикл объектов

### 1. Создание вакансии
```
API Response → Vacancy.from_dict() → Validation → Database Storage
```

### 2. Поиск вакансий
```
Search Query → SearchUtils → Database Query → Vacancy Objects → Formatting
```

### 3. Кэширование
```
API Request → Cache Check → API Call (if miss) → Cache Store → Return Data
```

## Обработка ошибок

### Пирамида обработки ошибок
```
┌─────────────────────────────────────┐
│          UI Layer                   │ ← Отображение ошибок пользователю
├─────────────────────────────────────┤
│        Business Logic               │ ← Логические ошибки и валидация
├─────────────────────────────────────┤
│         API Layer                   │ ← Сетевые ошибки и таймауты
├─────────────────────────────────────┤
│        Data Layer                   │ ← Ошибки БД и файловой системы
└─────────────────────────────────────┘
```

### Распространение ошибок
```python
try:
    api_data = self.api.get_vacancies(query)
except APIError as e:
    logger.error(f"API Error: {e}")
    return []  # Graceful degradation
except Exception as e:
    logger.exception("Unexpected error")
    raise SystemError("Service unavailable")
```

## Конфигурация зависимостей

### Injection Container (концептуально)
```python
container = {
    'database': PostgresSaver(db_config),
    'hh_api': HeadHunterAPI(api_config),
    'sj_api': SuperJobAPI(sj_config),
    'unified_api': UnifiedAPI(container['hh_api'], container['sj_api']),
    'search_handler': VacancySearchHandler(container['unified_api']),
    'display_handler': VacancyDisplayHandler(container['database'])
}
```

## Масштабируемость

### Горизонтальное масштабирование
- Кэш может быть вынесен в Redis
- База данных может быть кластеризована
- API запросы могут быть распределены

### Вертикальное масштабирование
- Batch операции для больших объемов данных
- Асинхронные запросы к API
- Индексация базы данных для быстрого поиска

Эта архитектура обеспечивает гибкость, масштабируемость и поддерживаемость системы.
