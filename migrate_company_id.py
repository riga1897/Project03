
#!/usr/bin/env python3
"""
Скрипт для миграции поля company_id в таблице vacancies
Приводит типы данных к совместимости с внешним ключом
"""

import psycopg2
import logging
from src.utils.env_loader import EnvLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_company_id():
    """Миграция поля company_id к правильной структуре с внешним ключом"""
    
    try:
        connection = psycopg2.connect(
            host=EnvLoader.get_env_var('PGHOST', 'localhost'),
            port=EnvLoader.get_env_var('PGPORT', '5432'),
            database=EnvLoader.get_env_var('PGDATABASE', 'Project03'),
            user=EnvLoader.get_env_var('PGUSER', 'postgres'),
            password=EnvLoader.get_env_var('PGPASSWORD', '')
        )
        
        cursor = connection.cursor()
        
        print("🔧 МИГРАЦИЯ COMPANY_ID")
        print("=" * 50)
        
        # 1. Проверяем текущую структуру
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'vacancies' AND column_name = 'company_id'
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"Текущий тип company_id в vacancies: {result[1]}")
        
        # 2. Удаляем существующие внешние ключи если есть
        cursor.execute("""
            SELECT constraint_name 
            FROM information_schema.table_constraints
            WHERE table_name = 'vacancies' 
            AND constraint_type = 'FOREIGN KEY'
            AND constraint_name LIKE '%company%'
        """)
        
        constraints = cursor.fetchall()
        for constraint in constraints:
            print(f"Удаляем существующий внешний ключ: {constraint[0]}")
            cursor.execute(f"ALTER TABLE vacancies DROP CONSTRAINT {constraint[0]}")
        
        # 3. Обновляем данные: устанавливаем company_id = NULL там, где значения не соответствуют id в companies
        print("Очищаем некорректные значения company_id...")
        cursor.execute("""
            UPDATE vacancies 
            SET company_id = NULL 
            WHERE company_id::text NOT IN (
                SELECT id::text FROM companies WHERE id IS NOT NULL
            )
        """)
        
        updated_rows = cursor.rowcount
        print(f"Очищено некорректных значений: {updated_rows}")
        
        # 4. Убеждаемся, что company_id имеет тип INTEGER
        cursor.execute("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'vacancies' AND column_name = 'company_id'
        """)
        
        current_type = cursor.fetchone()[0]
        if current_type != 'integer':
            print(f"Приводим тип company_id с {current_type} к integer...")
            # Сначала делаем резервную копию
            cursor.execute("ALTER TABLE vacancies ADD COLUMN company_id_backup TEXT")
            cursor.execute("UPDATE vacancies SET company_id_backup = company_id::text")
            
            # Удаляем и пересоздаем колонку
            cursor.execute("ALTER TABLE vacancies DROP COLUMN company_id CASCADE")
            cursor.execute("ALTER TABLE vacancies ADD COLUMN company_id INTEGER")
            
            # Восстанавливаем данные
            cursor.execute("""
                UPDATE vacancies 
                SET company_id = CASE 
                    WHEN company_id_backup ~ '^[0-9]+$' THEN company_id_backup::integer 
                    ELSE NULL 
                END
            """)
            
            cursor.execute("ALTER TABLE vacancies DROP COLUMN company_id_backup")
            print("✅ Тип company_id изменен на INTEGER")
        
        # 5. Создаем внешний ключ
        print("Создаем внешний ключ...")
        cursor.execute("""
            ALTER TABLE vacancies 
            ADD CONSTRAINT fk_vacancies_company_id 
            FOREIGN KEY (company_id) REFERENCES companies(id)
            ON DELETE SET NULL
        """)
        
        print("✅ Внешний ключ создан успешно")
        
        # 6. Проверяем результат
        cursor.execute("""
            SELECT 
                COUNT(*) as total_vacancies,
                COUNT(company_id) as with_company_id
            FROM vacancies
        """)
        
        stats = cursor.fetchone()
        print(f"\n📊 СТАТИСТИКА ПОСЛЕ МИГРАЦИИ:")
        print(f"Всего вакансий: {stats[0]}")
        print(f"С company_id: {stats[1]}")
        print(f"Без company_id: {stats[0] - stats[1]}")
        
        connection.commit()
        print("\n✅ МИГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО")
        
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
    migrate_company_id()
