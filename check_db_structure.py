
import psycopg2
from psycopg2.extras import RealDictCursor
from src.utils.env_loader import EnvLoader

def check_db_structure():
    """Проверяет реальную структуру БД и выводит информацию о таблицах"""
    
    # Подключение к БД
    try:
        connection = psycopg2.connect(
            host=EnvLoader.get_env_var('PGHOST', 'localhost'),
            port=EnvLoader.get_env_var('PGPORT', '5432'),
            database=EnvLoader.get_env_var('PGDATABASE', 'Project03'),
            user=EnvLoader.get_env_var('PGUSER', 'postgres'),
            password=EnvLoader.get_env_var('PGPASSWORD', '')
        )
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        print("🔍 АНАЛИЗ СТРУКТУРЫ БАЗЫ ДАННЫХ")
        print("=" * 50)
        
        # Проверяем существующие таблицы
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"📋 Найдено таблиц: {len(tables)}")
        for table in tables:
            print(f"  - {table['table_name']}")
        
        print("\n" + "=" * 50)
        
        # Анализируем структуру каждой таблицы
        for table in tables:
            table_name = table['table_name']
            print(f"\n📊 СТРУКТУРА ТАБЛИЦЫ: {table_name}")
            print("-" * 40)
            
            # Получаем информацию о колонках
            cursor.execute("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position;
            """, (table_name,))
            
            columns = cursor.fetchall()
            
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                length = f"({col['character_maximum_length']})" if col['character_maximum_length'] else ""
                default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                
                print(f"  {col['column_name']:<20} {col['data_type']}{length:<15} {nullable}{default}")
            
            # Проверяем внешние ключи
            cursor.execute("""
                SELECT
                    tc.constraint_name,
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_name = %s;
            """, (table_name,))
            
            foreign_keys = cursor.fetchall()
            if foreign_keys:
                print("\n  🔗 Внешние ключи:")
                for fk in foreign_keys:
                    print(f"    {fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}")
            
            # Получаем количество записей
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cursor.fetchone()['count']
            print(f"\n  📈 Количество записей: {count}")
        
        # Проверяем данные в таблице vacancies
        print("\n" + "=" * 50)
        print("🔍 АНАЛИЗ ДАННЫХ В ТАБЛИЦЕ VACANCIES")
        print("-" * 40)
        
        # Проверяем заполненность полей company и company_id
        cursor.execute("""
            SELECT 
                COUNT(*) as total_vacancies,
                COUNT(company_id) as with_company_id,
                COUNT(employer) as with_employer,
                COUNT(CASE WHEN company_id IS NOT NULL AND company_id != '' THEN 1 END) as with_non_empty_company_id,
                COUNT(CASE WHEN employer IS NOT NULL AND employer != '' THEN 1 END) as with_non_empty_employer
            FROM vacancies;
        """)
        
        stats = cursor.fetchone()
        print(f"Всего вакансий: {stats['total_vacancies']}")
        print(f"С company_id: {stats['with_company_id']} (не пустых: {stats['with_non_empty_company_id']})")
        print(f"С employer: {stats['with_employer']} (не пустых: {stats['with_non_empty_employer']})")
        
        # Примеры данных
        cursor.execute("""
            SELECT 
                vacancy_id,
                title,
                employer,
                company_id,
                source
            FROM vacancies 
            LIMIT 5;
        """)
        
        examples = cursor.fetchall()
        print(f"\n📝 Примеры записей:")
        for ex in examples:
            print(f"  ID: {ex['vacancy_id']}")
            print(f"  Название: {ex['title'][:50]}...")
            print(f"  Employer: {ex['employer']}")
            print(f"  Company_ID: {ex['company_id']}")
            print(f"  Источник: {ex['source']}")
            print("  " + "-" * 30)
        
        # Проверяем таблицу companies если существует
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'companies';
        """)
        
        if cursor.fetchone():
            print(f"\n🏢 АНАЛИЗ ТАБЛИЦЫ COMPANIES")
            print("-" * 40)
            
            cursor.execute("SELECT COUNT(*) as count FROM companies")
            companies_count = cursor.fetchone()['count']
            print(f"Всего компаний: {companies_count}")
            
            if companies_count > 0:
                cursor.execute("""
                    SELECT hh_id, company_id, name 
                    FROM companies 
                    LIMIT 5;
                """)
                
                company_examples = cursor.fetchall()
                print("Примеры компаний:")
                for comp in company_examples:
                    print(f"  HH_ID: {comp['hh_id']}, Company_ID: {comp['company_id']}, Name: {comp['name']}")
        
        cursor.close()
        connection.close()
        
        print("\n" + "=" * 50)
        print("✅ Анализ структуры БД завершен")
        
    except Exception as e:
        print(f"❌ Ошибка при анализе БД: {e}")

if __name__ == "__main__":
    check_db_structure()
