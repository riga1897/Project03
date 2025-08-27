
#!/usr/bin/env python3
"""
Скрипт для удаления поля employer из таблицы vacancies
Информация о компаниях теперь берется только из таблицы companies
"""

import psycopg2
import logging
from src.utils.env_loader import EnvLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_remove_employer_field():
    """Миграция для удаления поля employer из таблицы vacancies"""
    
    try:
        connection = psycopg2.connect(
            host=EnvLoader.get_env_var('PGHOST', 'localhost'),
            port=EnvLoader.get_env_var('PGPORT', '5432'),
            database=EnvLoader.get_env_var('PGDATABASE', 'Project03'),
            user=EnvLoader.get_env_var('PGUSER', 'postgres'),
            password=EnvLoader.get_env_var('PGPASSWORD', '')
        )
        
        cursor = connection.cursor()
        
        print("🔧 МИГРАЦИЯ: УДАЛЕНИЕ ПОЛЯ EMPLOYER")
        print("=" * 50)
        
        # 1. Проверяем, есть ли поле employer
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'vacancies' AND column_name = 'employer'
        """)
        
        if cursor.fetchone():
            print("✓ Поле employer найдено, начинаем миграцию...")
            
            # 2. Создаем резервную копию данных из employer в companies если нужно
            cursor.execute("""
                SELECT COUNT(*) FROM vacancies 
                WHERE employer IS NOT NULL 
                AND employer != ''
                AND company_id IS NULL
            """)
            
            orphaned_count = cursor.fetchone()[0]
            print(f"Найдено {orphaned_count} вакансий с employer, но без company_id")
            
            if orphaned_count > 0:
                print("Создаем записи в companies для вакансий без company_id...")
                cursor.execute("""
                    INSERT INTO companies (name, source, external_id)
                    SELECT DISTINCT 
                        employer as name,
                        'legacy' as source,
                        'legacy_' || MD5(employer) as external_id
                    FROM vacancies 
                    WHERE employer IS NOT NULL 
                    AND employer != ''
                    AND company_id IS NULL
                    AND employer NOT IN (SELECT name FROM companies)
                """)
                
                # Обновляем company_id для этих вакансий
                cursor.execute("""
                    UPDATE vacancies v
                    SET company_id = c.id
                    FROM companies c
                    WHERE v.employer = c.name
                    AND v.company_id IS NULL
                    AND c.source = 'legacy'
                """)
                
                updated_count = cursor.rowcount
                print(f"✓ Обновлено {updated_count} записей с company_id")
            
            # 3. Удаляем индексы связанные с employer
            cursor.execute("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename = 'vacancies' 
                AND indexname LIKE '%employer%'
            """)
            
            employer_indexes = cursor.fetchall()
            for (index_name,) in employer_indexes:
                print(f"Удаляем индекс: {index_name}")
                cursor.execute(f"DROP INDEX IF EXISTS {index_name}")
            
            # 4. Удаляем поле employer
            print("Удаляем поле employer...")
            cursor.execute("ALTER TABLE vacancies DROP COLUMN IF EXISTS employer")
            
            print("✓ Поле employer успешно удалено")
        else:
            print("✓ Поле employer уже отсутствует в таблице")
        
        # 5. Проверяем финальную структуру
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'vacancies' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print("\n📊 ФИНАЛЬНАЯ СТРУКТУРА ТАБЛИЦЫ VACANCIES:")
        for col_name, col_type in columns:
            print(f"  - {col_name}: {col_type}")
        
        connection.commit()
        print("\n✅ Миграция завершена успешно!")
        
    except Exception as e:
        logger.error(f"Ошибка при миграции: {e}")
        connection.rollback()
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    migrate_remove_employer_field()
