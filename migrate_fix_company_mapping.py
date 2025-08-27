
#!/usr/bin/env python3
"""
Скрипт для исправления сопоставления компаний в существующих вакансиях
"""

import logging
import sys
from src.storage.db_manager import DBManager
from src.config.db_config import DatabaseConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_company_mapping():
    """Исправляет сопоставление компаний для существующих вакансий"""
    try:
        db_manager = DBManager(DatabaseConfig())
        
        # Проверяем подключение
        if not db_manager.check_connection():
            logger.error("Нет подключения к базе данных")
            return False
            
        connection = db_manager._get_connection()
        
        try:
            cursor = connection.cursor()
            
            # Получаем все компании из БД
            cursor.execute("SELECT id, name, LOWER(name) as normalized_name FROM companies")
            companies = cursor.fetchall()
            
            company_patterns = {}
            for comp_id, original_name, normalized_name in companies:
                company_patterns[original_name] = comp_id
                
                # Добавляем альтернативные названия
                alternatives = {
                    "яндекс": ["yandex"],
                    "тинькофф": ["т-банк", "tinkoff", "t-bank", "tcs"],
                    "сбер": ["сбербанк", "sberbank", "sber"],
                    "wildberries": ["wb", "вайлдберриз"],
                    "ozon": ["озон"],
                    "vk": ["вконтакте", "вк", "mail.ru group", "vk group"],
                    "лаборатория касперского": ["kaspersky", "касперский"],
                    "авито": ["avito"],
                    "x5 retail group": ["x5", "x5 tech", "пятёрочка"],
                    "ростелеком": ["rostelecom", "ростелеком информационные технологии"],
                    "альфа-банк": ["alfa-bank", "alfabank"],
                    "jetbrains": ["джетбрейнс"],
                    "2gis": ["2гис", "дубльгис"],
                    "skyeng": ["скайэнг"],
                    "delivery club": ["деливери клаб"]
                }
                
                for main_name, alt_names in alternatives.items():
                    if main_name in normalized_name.lower():
                        for alt_name in alt_names:
                            company_patterns[alt_name] = comp_id
            
            # Получаем все вакансии без company_id
            cursor.execute("""
                SELECT id, vacancy_id, employer 
                FROM vacancies 
                WHERE company_id IS NULL AND employer IS NOT NULL AND employer != ''
            """)
            
            vacancies_to_update = cursor.fetchall()
            logger.info(f"Найдено {len(vacancies_to_update)} вакансий для обновления")
            
            updated_count = 0
            
            for vacancy_pk, vacancy_id, employer in vacancies_to_update:
                if not employer:
                    continue
                    
                employer_lower = employer.lower().strip()
                mapped_company_id = None
                
                # Поиск соответствующей компании
                for pattern_name, comp_id in company_patterns.items():
                    pattern_lower = pattern_name.lower()
                    if len(pattern_lower) > 3:
                        if pattern_lower in employer_lower or employer_lower in pattern_lower:
                            mapped_company_id = comp_id
                            break
                
                if mapped_company_id:
                    cursor.execute(
                        "UPDATE vacancies SET company_id = %s WHERE id = %s",
                        (mapped_company_id, vacancy_pk)
                    )
                    updated_count += 1
                    logger.info(f"✅ Обновлено: {employer} -> company_id: {mapped_company_id}")
                else:
                    logger.debug(f"❌ Не найдено соответствие для: {employer}")
            
            connection.commit()
            logger.info(f"✅ Обновлено {updated_count} вакансий")
            
            # Проверяем результат
            cursor.execute("""
                SELECT c.name, COUNT(v.id) as vacancy_count
                FROM companies c
                LEFT JOIN vacancies v ON c.id = v.company_id
                GROUP BY c.name, c.id
                ORDER BY vacancy_count DESC, c.name
            """)
            
            results = cursor.fetchall()
            logger.info("\n📊 Результат миграции:")
            for company_name, vacancy_count in results:
                status = "✅" if vacancy_count > 0 else "❌"
                logger.info(f"{status} {company_name}: {vacancy_count} вакансий")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка миграции: {e}")
            connection.rollback()
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()
            
    except Exception as e:
        logger.error(f"Ошибка подключения: {e}")
        return False

if __name__ == "__main__":
    logger.info("🔄 Запуск миграции сопоставления компаний...")
    success = migrate_company_mapping()
    
    if success:
        logger.info("✅ Миграция завершена успешно")
        sys.exit(0)
    else:
        logger.error("❌ Миграция завершилась с ошибками")
        sys.exit(1)
