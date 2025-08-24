
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
Пользователь → ConsoleInterface → VacancyOperations → PostgresSaver
                     ↓
               SearchUtils → VacancyOperations → VacancyFormatter
                     ↓
               Paginator → VacancyDisplayHandler → Пользователь
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
     ↓
APIConfig → HeadHunterAPI/SuperJobAPI
     ↓
UIConfig → ConsoleInterface → VacancyDisplayHandler
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

#### Interaction с базой данных
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
```

#### Преобразование данных
```python
class Vacancy:
    @classmethod
    def from_dict(cls, data):
        # Универсальное преобразование из разных API
        title = data.get('name') or data.get('profession')
        url = data.get('alternate_url') or data.get('link')
        
        # Создание унифицированного объекта
        return cls(title=title, url=url, ...)
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

#### Отображение данных
```python
class VacancyDisplayHandler:
    def show_vacancies(self, vacancies):
        formatted = self.formatter.format_list(vacancies)
        paginated = self.paginator.paginate(formatted)
        
        for page in paginated:
            self._display_page(page)
            user_action = self._get_user_input()
            if user_action == 'quit':
                break
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
