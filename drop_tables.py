
#!/usr/bin/env python3
"""
Скрипт для удаления всех таблиц в базе данных
Таблицы будут пересозданы автоматически при следующем запуске приложения
"""

import logging
import psycopg2
from psycopg2.extras import RealDictCursor

from src.utils.env_loader import EnvLoader

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def drop_all_tables():
    """Удаляет все таблицы в базе данных"""
    
    try:
        connection = psycopg2.connect(
            host=EnvLoader.get_env_var('PGHOST', 'localhost'),
            port=EnvLoader.get_env_var('PGPORT', '5432'),
            database=EnvLoader.get_env_var('PGDATABASE', 'Project03'),
            user=EnvLoader.get_env_var('PGUSER', 'postgres'),
            password=EnvLoader.get_env_var('PGPASSWORD', '')
        )
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        print("🗑️  УДАЛЕНИЕ ВСЕХ ТАБЛИЦ")
        print("=" * 50)
        
        # Отключаем проверки внешних ключей
        cursor.execute("SET session_replication_role = replica;")
        
        # Получаем список всех таблиц
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        
        if not tables:
            print("✅ Таблицы не найдены")
            return
        
        print(f"📋 Найдено таблиц для удаления: {len(tables)}")
        for table in tables:
            print(f"  - {table['table_name']}")
        
        # Подтверждение удаления
        confirm = input("\nВы уверены, что хотите удалить ВСЕ таблицы? (yes/no): ")
        if confirm.lower() not in ['yes', 'y', 'да']:
            print("❌ Операция отменена")
            return
        
        # Удаляем все таблицы
        print("\n🗑️  Удаляем таблицы...")
        for table in tables:
            table_name = table['table_name']
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
                print(f"✅ Удалена таблица: {table_name}")
            except Exception as e:
                print(f"❌ Ошибка при удалении таблицы {table_name}: {e}")
        
        # Включаем обратно проверки внешних ключей
        cursor.execute("SET session_replication_role = DEFAULT;")
        
        connection.commit()
        
        # Проверяем результат
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
        """)
        
        remaining_tables = cursor.fetchone()['count']
        
        print(f"\n✅ ОПЕРАЦИЯ ЗАВЕРШЕНА")
        print(f"Осталось таблиц: {remaining_tables}")
        
        if remaining_tables == 0:
            print("🎉 Все таблицы успешно удалены!")
            print("💡 При следующем запуске приложения таблицы будут созданы заново с правильной структурой")
        else:
            print("⚠️  Некоторые таблицы не были удалены")
            
    except psycopg2.Error as e:
        logger.error(f"Ошибка при работе с БД: {e}")
        print(f"❌ Ошибка базы данных: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        print(f"❌ Неожиданная ошибка: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()


if __name__ == "__main__":
    drop_all_tables()
