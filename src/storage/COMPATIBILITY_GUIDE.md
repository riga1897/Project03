# Руководство по совместимости базы данных

## Проблемы совместимости и их решения

### 1. psycopg2 vs psycopg2-binary

**Проблема**: На разных платформах может быть установлен либо `psycopg2`, либо `psycopg2-binary`, что приводит к ошибкам импорта.

**Решение**: Система автоматически определяет доступную библиотеку через модуль `src/storage/db_psycopg2_compat.py`.

#### Установка зависимостей:

```bash
# Рекомендуется (содержит скомпилированные библиотеки):
pip install psycopg2-binary

# Альтернатива (требует dev-пакеты PostgreSQL):
pip install psycopg2
```

#### Проверка доступности:

```python
from src.storage.db_psycopg2_compat import is_available

if is_available():
    print("✅ psycopg2 готов к использованию")
else:
    print("❌ Нужно установить psycopg2-binary или psycopg2")
```

### 2. DATABASE_URL vs отдельные параметры

**Проблема**: Разные платформы используют разные способы конфигурации подключения к БД.

**Решение**: Система поддерживает множество форматов через `src/storage/db_connection_config.py`.

#### Поддерживаемые переменные окружения:

**Приоритет 1 - DATABASE_URL:**
```bash
DATABASE_URL=postgresql://user:password@host:port/database
DATABASE_URL=postgres://user:password@host:port/database  # Также поддерживается
```

**Приоритет 2 - PostgreSQL стандарт:**
```bash
PGHOST=localhost
PGPORT=5432
PGDATABASE=mydb
PGUSER=postgres
PGPASSWORD=secret
```

**Приоритет 3 - Docker/Cloud форматы:**
```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mydb           # или POSTGRES_DATABASE
POSTGRES_USER=postgres     # или POSTGRES_USERNAME
POSTGRES_PASSWORD=secret

DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=mydb
DATABASE_USER=postgres
DATABASE_PASSWORD=secret

DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydb
DB_USER=postgres
DB_PASSWORD=secret
```

#### Пример использования:

```python
from src.storage.db_connection_config import get_db_connection_params

# Автоматически определит доступные параметры
config = get_db_connection_params()
print(f"Подключение к: {config['host']}:{config['port']}")

# Явная конфигурация
custom_config = get_db_connection_params({
    'host': 'my-db-server.com',
    'port': '5432',
    'database': 'my_app_db',
    'user': 'my_user',
    'password': 'my_password'
})
```

### 3. Тестирование совместимости

Для проверки что система работает с вашей конфигурацией:

```python
# Тест 1: Проверка psycopg2
from src.storage.db_psycopg2_compat import is_available, get_psycopg2

if is_available():
    psycopg2 = get_psycopg2()
    print(f"psycopg2 версия: {psycopg2.__version__}")

# Тест 2: Проверка конфигурации БД  
from src.storage.db_connection_config import get_db_connection_params

config = get_db_connection_params()
required_params = ['host', 'port', 'database', 'user']

for param in required_params:
    if not config.get(param):
        print(f"❌ Не задан параметр: {param}")
    else:
        print(f"✅ {param}: {config[param]}")
```

### 4. Решение конкретных проблем

#### Ошибка: "No module named 'psycopg2'"
```bash
pip install psycopg2-binary
```

#### Ошибка: "pg_config executable not found"
```bash
# Ubuntu/Debian:
sudo apt-get install libpq-dev python3-dev

# Затем:
pip install psycopg2-binary  # Рекомендуется
```

#### Ошибка подключения: "connection refused"
Проверьте переменные окружения:
```bash
echo $DATABASE_URL
echo $PGHOST
echo $PGPORT
```

#### Ошибка: "database does not exist"
Убедитесь что база данных создана:
```sql
CREATE DATABASE your_database_name;
```

## Миграция с других конфигураций

### Из Django:
```bash
# Django обычно использует:
DATABASE_URL=postgres://user:password@host:port/dbname

# Это автоматически поддерживается
```

### Из Docker Compose:
```yaml
# docker-compose.yml
environment:
  POSTGRES_HOST: db
  POSTGRES_PORT: 5432
  POSTGRES_DB: myapp
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: password

# Автоматически поддерживается через альтернативные переменные
```

### Из Heroku:
```bash
# Heroku устанавливает DATABASE_URL автоматически
# Никаких изменений не требуется
```

## Отладка

Включите отладочные логи для диагностики:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Теперь система покажет какие параметры загружаются откуда
```