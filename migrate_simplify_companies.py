
#!/usr/bin/env python3
"""
Скрипт миграции для упрощения структуры таблицы companies
Оставляет только поля id, name, description
"""

import psycopg2
import logging
from src.utils.env_loader import EnvLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_simplify_companies():
    """Миграция для упрощения структуры таблицы companies"""
    
    try:
        connection = psycopg2.connect(
            host=EnvLoader.get_env_var('PGHOST', 'localhost'),
            port=EnvLoader.get_env_var('PGPORT', '5432'),
            database=EnvLoader.get_env_var('PGDATABASE', 'Project03'),
            user=EnvLoader.get_env_var('PGUSER', 'postgres'),
            password=EnvLoader.get_env_var('PGPASSWORD', '')
        )
        
        cursor = connection.cursor()
        
        print("🔧 МИГРАЦИЯ: УПРОЩЕНИЕ СТРУКТУРЫ ТАБЛИЦЫ COMPANIES")
        print("=" * 60)
        
        # 1. Проверяем текущую структуру
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'companies' 
            ORDER BY ordinal_position
        """)
        
        current_columns = cursor.fetchall()
        print("Текущие поля в таблице companies:")
        for col_name, data_type in current_columns:
            print(f"  - {col_name}: {data_type}")
        
        # 2. Удаляем ненужные поля
        fields_to_remove = ['external_id', 'url', 'logo_url', 'site_url', 'source']
        
        for field in fields_to_remove:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'companies' AND column_name = %s
            """, (field,))
            
            if cursor.fetchone():
                print(f"Удаляем поле {field}...")
                cursor.execute(f"ALTER TABLE companies DROP COLUMN IF EXISTS {field}")
                print(f"✓ Поле {field} удалено")
        
        # 3. Добавляем поле description если его нет
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'companies' AND column_name = 'description'
        """)
        
        if not cursor.fetchone():
            print("Добавляем поле description...")
            cursor.execute("ALTER TABLE companies ADD COLUMN description TEXT")
            print("✓ Поле description добавлено")
        
        # 4. Добавляем уникальный индекс на name
        try:
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_companies_name_unique ON companies(name)")
            print("✓ Уникальный индекс на поле name создан")
        except psycopg2.Error as e:
            print(f"⚠️ Не удалось создать уникальный индекс: {e}")
        
        # 5. Удаляем старые индексы
        old_indexes = ['idx_companies_external_id', 'idx_companies_source', 'idx_companies_company_id']
        for index_name in old_indexes:
            try:
                cursor.execute(f"DROP INDEX IF EXISTS {index_name}")
                print(f"✓ Индекс {index_name} удален")
            except psycopg2.Error as e:
                print(f"⚠️ Не удалось удалить индекс {index_name}: {e}")
        
        # 6. Заполняем таблицу целевыми компаниями если она пуста
        cursor.execute("SELECT COUNT(*) FROM companies")
        companies_count = cursor.fetchone()[0]
        
        if companies_count == 0:
            print("Заполняем таблицу целевыми компаниями...")
            from src.config.target_companies import TARGET_COMPANIES
            
            for company in TARGET_COMPANIES:
                cursor.execute("""
                    INSERT INTO companies (name, description)
                    VALUES (%s, %s)
                    ON CONFLICT (name) DO NOTHING
                """, (
                    company["name"],
                    company.get("description", "")
                ))
            
            print(f"✓ Добавлено {len(TARGET_COMPANIES)} целевых компаний")
        
        # 7. Проверяем финальную структуру
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'companies' 
            ORDER BY ordinal_position
        """)
        
        final_columns = cursor.fetchall()
        print("\nФинальная структура таблицы companies:")
        for col_name, data_type in final_columns:
            print(f"  - {col_name}: {data_type}")
        
        # 8. Статистика
        cursor.execute("SELECT COUNT(*) FROM companies")
        final_count = cursor.fetchone()[0]
        print(f"\n📊 СТАТИСТИКА:")
        print(f"Общее количество компаний: {final_count}")
        
        connection.commit()
        print("\n✅ Миграция завершена успешно!")
        
    except Exception as e:
        logger.error(f"Ошибка миграции: {e}")
        connection.rollback()
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        connection.close()

if __name__ == "__main__":
    migrate_simplify_companies()
