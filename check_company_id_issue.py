
#!/usr/bin/env python3
"""
Скрипт для диагностики проблемы с полем company_id в таблицах
"""

import psycopg2
import logging
from src.utils.env_loader import EnvLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_company_id_issue():
    """Проверяет структуру таблиц и ищет проблемы с полем company_id"""
    
    try:
        connection = psycopg2.connect(
            host=EnvLoader.get_env_var('PGHOST', 'localhost'),
            port=EnvLoader.get_env_var('PGPORT', '5432'),
            database=EnvLoader.get_env_var('PGDATABASE', 'Project03'),
            user=EnvLoader.get_env_var('PGUSER', 'postgres'),
            password=EnvLoader.get_env_var('PGPASSWORD', '')
        )
        
        cursor = connection.cursor()
        
        print("🔍 ДИАГНОСТИКА СТРУКТУРЫ ТАБЛИЦ")
        print("=" * 50)
        
        # 1. Проверяем структуру таблицы companies
        print("\n📋 СТРУКТУРА ТАБЛИЦЫ COMPANIES:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'companies' 
            ORDER BY ordinal_position
        """)
        
        companies_columns = cursor.fetchall()
        for col_name, data_type, nullable, default in companies_columns:
            print(f"  - {col_name}: {data_type} (nullable: {nullable}, default: {default})")
        
        # 2. Проверяем структуру таблицы vacancies
        print("\n📋 СТРУКТУРА ТАБЛИЦЫ VACANCIES:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'vacancies' 
            ORDER BY ordinal_position
        """)
        
        vacancies_columns = cursor.fetchall()
        for col_name, data_type, nullable, default in vacancies_columns:
            print(f"  - {col_name}: {data_type} (nullable: {nullable}, default: {default})")
        
        # 3. Ищем подозрительные поля
        print("\n🚨 ПОИСК ПОДОЗРИТЕЛЬНЫХ ПОЛЕЙ:")
        suspicious_fields = []
        
        for col_name, _, _, _ in companies_columns + vacancies_columns:
            if 'company_id' in col_name.lower() and col_name != 'company_id':
                suspicious_fields.append(col_name)
        
        if suspicious_fields:
            print(f"Найдены подозрительные поля: {', '.join(suspicious_fields)}")
        else:
            print("Подозрительных полей не найдено")
        
        # 4. Проверяем внешние ключи
        print("\n🔗 ВНЕШНИЕ КЛЮЧИ:")
        cursor.execute("""
            SELECT 
                constraint_name,
                table_name,
                column_name,
                foreign_table_name,
                foreign_column_name
            FROM information_schema.key_column_usage kcu
            JOIN information_schema.referential_constraints rc 
                ON kcu.constraint_name = rc.constraint_name
            JOIN information_schema.key_column_usage kcu2 
                ON rc.unique_constraint_name = kcu2.constraint_name
            WHERE kcu.table_name IN ('companies', 'vacancies')
        """)
        
        foreign_keys = cursor.fetchall()
        for constraint, table, column, foreign_table, foreign_column in foreign_keys:
            print(f"  - {table}.{column} -> {foreign_table}.{foreign_column} ({constraint})")
        
        # 5. Проверяем индексы
        print("\n📊 ИНДЕКСЫ:")
        cursor.execute("""
            SELECT indexname, tablename, indexdef
            FROM pg_indexes 
            WHERE tablename IN ('companies', 'vacancies')
            AND schemaname = 'public'
            ORDER BY tablename, indexname
        """)
        
        indexes = cursor.fetchall()
        for index_name, table_name, index_def in indexes:
            print(f"  - {table_name}.{index_name}: {index_def}")
        
        # 6. Статистика данных
        print("\n📈 СТАТИСТИКА ДАННЫХ:")
        cursor.execute("SELECT COUNT(*) FROM companies")
        companies_count = cursor.fetchone()[0]
        print(f"Компаний в БД: {companies_count}")
        
        cursor.execute("SELECT COUNT(*) FROM vacancies")
        vacancies_count = cursor.fetchone()[0]
        print(f"Вакансий в БД: {vacancies_count}")
        
        cursor.execute("""
            SELECT COUNT(*) FROM vacancies 
            WHERE company_id IS NOT NULL
        """)
        vacancies_with_company = cursor.fetchone()[0]
        print(f"Вакансий с company_id: {vacancies_with_company}")
        
        print(f"\n✅ Диагностика завершена")
        
    except Exception as e:
        logger.error(f"Ошибка при диагностике: {e}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    check_company_id_issue()
