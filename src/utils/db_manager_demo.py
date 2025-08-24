
"""
Демонстрационные функции для работы с классом DBManager.

Показывает примеры использования всех методов DBManager
согласно требованиям проекта.
"""

import logging
from typing import List, Dict, Any
from src.storage.db_manager import DBManager
from src.config.target_companies import TARGET_COMPANIES

logger = logging.getLogger(__name__)


def demo_companies_and_vacancies_count(db_manager: DBManager) -> None:
    """
    Демонстрация метода get_companies_and_vacancies_count()
    """
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ: Компании и количество вакансий")
    print("="*60)
    
    companies_stats = db_manager.get_companies_and_vacancies_count()
    
    if not companies_stats:
        print("❌ Нет данных о компаниях в базе данных")
        return
    
    print(f"📊 Найдено {len(companies_stats)} компаний в базе данных:")
    print()
    
    for i, company in enumerate(companies_stats[:10], 1):  # Показываем топ-10
        print(f"{i:2d}. {company['company_name']:<40} - {company['vacancy_count']:>3} вакансий")
    
    if len(companies_stats) > 10:
        print(f"... и еще {len(companies_stats) - 10} компаний")


def demo_all_vacancies(db_manager: DBManager) -> None:
    """
    Демонстрация метода get_all_vacancies()
    """
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ: Все вакансии")
    print("="*60)
    
    all_vacancies = db_manager.get_all_vacancies()
    
    if not all_vacancies:
        print("❌ Нет вакансий в базе данных")
        return
    
    print(f"📋 Найдено {len(all_vacancies)} вакансий в базе данных:")
    print()
    
    # Показываем первые 5 вакансий
    for i, vacancy in enumerate(all_vacancies[:5], 1):
        print(f"{i}. {vacancy['vacancy_title']}")
        print(f"   Компания: {vacancy['company_name']}")
        print(f"   Зарплата: {vacancy['salary_info']}")
        print(f"   Ссылка: {vacancy['vacancy_url']}")
        print()
    
    if len(all_vacancies) > 5:
        print(f"... и еще {len(all_vacancies) - 5} вакансий")


def demo_avg_salary(db_manager: DBManager) -> None:
    """
    Демонстрация метода get_avg_salary()
    """
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ: Средняя зарплата")
    print("="*60)
    
    avg_salary = db_manager.get_avg_salary()
    
    if avg_salary is None:
        print("❌ Не удалось вычислить среднюю зарплату (недостаточно данных)")
        return
    
    print(f"💰 Средняя зарплата по всем вакансиям: {avg_salary:,.0f} руб.")
    
    # Дополнительная статистика
    stats = db_manager.get_database_stats()
    if stats:
        print(f"📊 Статистика:")
        print(f"   - Всего вакансий: {stats.get('total_vacancies', 0)}")
        print(f"   - С указанной зарплатой: {stats.get('vacancies_with_salary', 0)}")
        print(f"   - Без зарплаты: {stats.get('vacancies_without_salary', 0)}")


def demo_vacancies_with_higher_salary(db_manager: DBManager) -> None:
    """
    Демонстрация метода get_vacancies_with_higher_salary()
    """
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ: Вакансии с зарплатой выше средней")
    print("="*60)
    
    avg_salary = db_manager.get_avg_salary()
    if avg_salary is None:
        print("❌ Не удалось вычислить среднюю зарплату")
        return
    
    high_salary_vacancies = db_manager.get_vacancies_with_higher_salary()
    
    if not high_salary_vacancies:
        print("❌ Нет вакансий с зарплатой выше средней")
        return
    
    print(f"📈 Средняя зарплата: {avg_salary:,.0f} руб.")
    print(f"🎯 Найдено {len(high_salary_vacancies)} вакансий с зарплатой выше средней:")
    print()
    
    # Показываем топ-5 вакансий с высокой зарплатой
    for i, vacancy in enumerate(high_salary_vacancies[:5], 1):
        print(f"{i}. {vacancy['vacancy_title']}")
        print(f"   Компания: {vacancy['company_name']}")
        print(f"   Зарплата: {vacancy['salary_info']}")
        print(f"   Расчетная зарплата: {vacancy['calculated_salary']:,.0f} руб.")
        print()
    
    if len(high_salary_vacancies) > 5:
        print(f"... и еще {len(high_salary_vacancies) - 5} вакансий")


def demo_vacancies_with_keyword(db_manager: DBManager, keyword: str = "Python") -> None:
    """
    Демонстрация метода get_vacancies_with_keyword()
    """
    print("\n" + "="*60)
    print(f"ДЕМОНСТРАЦИЯ: Поиск вакансий по ключевому слову '{keyword}'")
    print("="*60)
    
    keyword_vacancies = db_manager.get_vacancies_with_keyword(keyword)
    
    if not keyword_vacancies:
        print(f"❌ Не найдено вакансий с ключевым словом '{keyword}'")
        return
    
    print(f"🔍 Найдено {len(keyword_vacancies)} вакансий с ключевым словом '{keyword}':")
    print()
    
    # Показываем первые 5 найденных вакансий
    for i, vacancy in enumerate(keyword_vacancies[:5], 1):
        print(f"{i}. {vacancy['vacancy_title']}")
        print(f"   Компания: {vacancy['company_name']}")
        print(f"   Зарплата: {vacancy['salary_info']}")
        print()
    
    if len(keyword_vacancies) > 5:
        print(f"... и еще {len(keyword_vacancies) - 5} вакансий")


def demo_database_stats(db_manager: DBManager) -> None:
    """
    Демонстрация общей статистики базы данных
    """
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ: Общая статистика базы данных")
    print("="*60)
    
    stats = db_manager.get_database_stats()
    
    if not stats:
        print("❌ Не удалось получить статистику базы данных")
        return
    
    print("📊 Общая статистика базы данных:")
    print(f"   • Всего вакансий: {stats.get('total_vacancies', 0):,}")
    print(f"   • Вакансий с зарплатой: {stats.get('vacancies_with_salary', 0):,}")
    print(f"   • Вакансий без зарплаты: {stats.get('vacancies_without_salary', 0):,}")
    print(f"   • Уникальных компаний: {stats.get('unique_companies', 0):,}")
    
    if stats.get('total_vacancies', 0) > 0:
        percentage_with_salary = (stats.get('vacancies_with_salary', 0) / stats.get('total_vacancies', 1)) * 100
        print(f"   • Процент вакансий с зарплатой: {percentage_with_salary:.1f}%")


def demo_target_companies(db_manager: DBManager) -> None:
    """
    Демонстрация работы с целевыми компаниями
    """
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ: Целевые компании")
    print("="*60)
    
    print(f"🎯 Настроено {len(TARGET_COMPANIES)} целевых компаний:")
    print()
    
    # Получаем статистику по всем компаниям
    companies_stats = db_manager.get_companies_and_vacancies_count()
    companies_dict = {comp['company_name']: comp['vacancy_count'] for comp in companies_stats}
    
    found_companies = 0
    total_vacancies_from_targets = 0
    
    for i, company in enumerate(TARGET_COMPANIES, 1):
        name = company['name']
        hh_id = company['hh_id']
        description = company['description']
        
        # Ищем компанию в базе данных (возможны вариации названий)
        vacancy_count = 0
        for db_company_name, count in companies_dict.items():
            if name.lower() in db_company_name.lower() or db_company_name.lower() in name.lower():
                vacancy_count = count
                found_companies += 1
                total_vacancies_from_targets += count
                break
        
        status = "✅" if vacancy_count > 0 else "❌"
        print(f"{i:2d}. {status} {name} (ID: {hh_id})")
        print(f"     📝 {description}")
        print(f"     📊 Вакансий в БД: {vacancy_count}")
        print()
    
    print(f"📈 Итого:")
    print(f"   • Найдено компаний в БД: {found_companies} из {len(TARGET_COMPANIES)}")
    print(f"   • Вакансий от целевых компаний: {total_vacancies_from_targets}")


def run_all_demos(db_manager: DBManager) -> None:
    """
    Запускает все демонстрации методов DBManager
    """
    print("🚀 ДЕМОНСТРАЦИЯ ВСЕХ МЕТОДОВ КЛАССА DBManager")
    print("="*80)
    
    try:
        demo_database_stats(db_manager)
        demo_companies_and_vacancies_count(db_manager)
        demo_avg_salary(db_manager)
        demo_vacancies_with_higher_salary(db_manager)
        demo_vacancies_with_keyword(db_manager, "Python")
        demo_all_vacancies(db_manager)
        demo_target_companies(db_manager)
        
        print("\n" + "="*80)
        print("✅ ВСЕ ДЕМОНСТРАЦИИ ЗАВЕРШЕНЫ УСПЕШНО!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ ОШИБКА ПРИ ВЫПОЛНЕНИИ ДЕМОНСТРАЦИИ: {e}")
        logger.error(f"Ошибка в демонстрации DBManager: {e}")


if __name__ == "__main__":
    # Пример использования
    logging.basicConfig(level=logging.INFO)
    
    db_manager = DBManager()
    run_all_demos(db_manager)
