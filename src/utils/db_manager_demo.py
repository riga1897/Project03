
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
    print("ДЕМОНСТРАЦИЯ: Целевые компании и количество вакансий")
    print("="*60)
    
    companies_stats = db_manager.get_companies_and_vacancies_count()
    
    if not companies_stats:
        print("❌ Нет данных о целевых компаниях в базе данных")
        return
    
    print(f"📊 Статистика по {len(TARGET_COMPANIES)} целевым компаниям:")
    print()
    print(f"{'№':<3} {'Название компании':<40} {'Количество вакансий':<20}")
    print("-" * 70)
    
    # Показываем все 15 целевых компаний
    for i, (company_name, vacancy_count) in enumerate(companies_stats, 1):
        status = "✅" if vacancy_count > 0 else "❌"
        print(f"{i:<3} {status} {company_name:<37} {vacancy_count:<20}")
    
    total_vacancies = sum(count for _, count in companies_stats)
    companies_with_vacancies = sum(1 for _, count in companies_stats if count > 0)
    
    print()
    print(f"📈 Итоговая статистика:")
    print(f"   • Компаний с вакансиями: {companies_with_vacancies} из {len(companies_stats)}")
    print(f"   • Всего вакансий от целевых компаний: {total_vacancies}")
    
    if total_vacancies == 0:
        print("⚠️  Рекомендация: Выполните поиск вакансий от целевых компаний для получения данных")
    
    print(f"\nВсего целевых компаний: {len(companies_stats)}")
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
"""
Демонстрационный модуль для работы с классом DBManager

Показывает использование всех методов DBManager согласно требованиям проекта.
Позволяет протестировать функциональность работы с базой данных.
"""

import logging
from typing import Optional

from src.config.target_companies import TargetCompanies
from src.storage.db_manager import DBManager

logger = logging.getLogger(__name__)


class DBManagerDemo:
    """
    Демонстрационный класс для работы с DBManager
    
    Предоставляет методы для демонстрации всех возможностей
    класса DBManager согласно требованиям проекта.
    """
    
    def __init__(self, db_manager: Optional[DBManager] = None):
        """
        Инициализация демо-класса
        
        Args:
            db_manager: Экземпляр DBManager. Если None, создается новый
        """
        self.db_manager = db_manager or DBManager()
    
    def run_full_demo(self) -> None:
        """
        Запускает полную демонстрацию всех методов DBManager
        """
        print("=" * 80)
        print("ДЕМОНСТРАЦИЯ РАБОТЫ КЛАССА DBManager")
        print("🎯 АНАЛИЗ ДАННЫХ ТОЛЬКО ПО 15 ЦЕЛЕВЫМ КОМПАНИЯМ")
        print("📊 Все методы фильтруют результаты по целевым компаниям")
        print("=" * 80)
        
        # Проверяем подключение
        if not self._check_connection():
            return
        
        # Показываем информацию о целевых компаниях
        self._show_target_companies()
        
        # Демонстрируем все методы
        self._demo_companies_and_vacancies_count()
        self._demo_all_vacancies()
        self._demo_avg_salary()
        self._demo_vacancies_with_higher_salary()
        self._demo_vacancies_with_keyword()
        self._demo_database_stats()
        
        print("=" * 80)
        print("✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
        print("🎯 Показана статистика ТОЛЬКО по 15 целевым компаниям из конфигурации")
        print("📋 Все результаты отфильтрованы по списку TARGET_COMPANIES")
        print("🔍 Анализ исключает вакансии от других компаний")
        print("=" * 80)
    
    def _check_connection(self) -> bool:
        """
        Проверяет подключение к БД
        
        Returns:
            bool: True если подключение успешно
        """
        print("\n1. Проверка подключения к базе данных...")
        
        if self.db_manager.check_connection():
            print("✅ Подключение к базе данных успешно установлено")
            return True
        else:
            print("❌ Ошибка подключения к базе данных")
            print("Убедитесь, что PostgreSQL запущен и настроен корректно")
            return False
    
    def _show_target_companies(self) -> None:
        """Показывает информацию о целевых компаниях"""
        print("\n2. Целевые компании проекта (15 компаний):")
        print("-" * 60)
        
        from src.config.target_companies import TARGET_COMPANIES
        
        print("Анализ будет проводиться по следующим целевым компаниям:")
        print()
        
        for i, company in enumerate(TARGET_COMPANIES, 1):
            print(f"{i:2d}. {company['name']} (HH ID: {company['hh_id']})")
            print(f"    {company['description']}")
        
        print(f"\nВсего целевых компаний: {len(TARGET_COMPANIES)}")
    
    def _demo_companies_and_vacancies_count(self) -> None:
        """Демонстрирует метод get_companies_and_vacancies_count() для целевых компаний"""
        print("\n3. get_companies_and_vacancies_count() - Анализ вакансий по целевым компаниям:")
        print("-" * 80)
        
        from src.config.target_companies import TARGET_COMPANIES
        
        print("📋 Анализ показывает только данные от целевых компаний из конфигурации проекта")
        print("🎯 Метод фильтрует результаты и показывает статистику по всем 15 целевым компаниям")
        print()
        
        # Получаем данные специально по целевым компаниям
        companies_data = self.db_manager.get_target_companies_analysis()
        
        if not companies_data:
            print("❌ Нет данных о целевых компаниях")
            print("💡 Выполните поиск вакансий через пункт меню 1 для получения данных")
            return
        
        print(f"{'№':<3} {'Целевая компания':<35} {'Количество вакансий':<20}")
        print("-" * 80)
        
        total_vacancies = 0
        companies_with_vacancies = 0
        
        # Показываем результаты в том порядке, как они возвращены методом
        # (метод уже фильтрует и сопоставляет целевые компании)
        for i, (company_name, vacancy_count) in enumerate(companies_data, 1):
            status = "✅" if vacancy_count > 0 else "❌"
            print(f"{i:<3} {status} {company_name:<32} {vacancy_count:<20}")
            
            total_vacancies += vacancy_count
            if vacancy_count > 0:
                companies_with_vacancies += 1
        
        print("-" * 80)
        print(f"📊 АНАЛИЗ ПО ЦЕЛЕВЫМ КОМПАНИЯМ:")
        print(f"   • Целевых компаний с вакансиями: {companies_with_vacancies} из {len(TARGET_COMPANIES)}")
        print(f"   • Всего вакансий от целевых компаний: {total_vacancies}")
        print(f"   • Покрытие целевых компаний: {(companies_with_vacancies/len(TARGET_COMPANIES)*100):.1f}%")
        
        if total_vacancies == 0:
            print("💡 Для получения данных выполните поиск вакансий через пункт меню 1")
            print("   Выберите источник API и введите запрос для поиска")
        else:
            print(f"\n🔍 РЕЗУЛЬТАТ: Найдены вакансии от {companies_with_vacancies} целевых компаний")
            print("   Анализ показывает только данные от компаний из списка TARGET_COMPANIES")
    
    def _demo_all_vacancies(self) -> None:
        """Демонстрирует метод get_all_vacancies()"""
        print("\n4. get_all_vacancies() - Все вакансии:")
        print("-" * 80)
        
        vacancies = self.db_manager.get_all_vacancies()
        
        if not vacancies:
            print("Вакансии не найдены.")
            return
        
        print(f"{'№':<3} {'Название':<25} {'Компания':<20} {'Зарплата':<15}")
        print("-" * 80)
        
        for i, vacancy in enumerate(vacancies[:5], 1):
            title = vacancy['title'][:24] if len(vacancy['title']) > 24 else vacancy['title']
            company = vacancy['company_name'][:19] if len(vacancy['company_name']) > 19 else vacancy['company_name']
            salary = vacancy['salary_info'][:14] if len(vacancy['salary_info']) > 14 else vacancy['salary_info']
            
            print(f"{i:<3} {title:<25} {company:<20} {salary:<15}")
        
        if len(vacancies) > 5:
            print(f"... и еще {len(vacancies) - 5} вакансий")
        
        print(f"\nВсего вакансий: {len(vacancies)}")
    
    def _demo_avg_salary(self) -> None:
        """Демонстрирует метод get_avg_salary()"""
        print("\n5. get_avg_salary() - Средняя зарплата:")
        print("-" * 40)
        
        avg_salary = self.db_manager.get_avg_salary()
        
        if avg_salary is not None:
            print(f"Средняя зарплата по всем вакансиям: {avg_salary:,.0f} руб.")
        else:
            print("Не удалось рассчитать среднюю зарплату.")
            print("Возможно, нет вакансий с указанной зарплатой.")
    
    def _demo_vacancies_with_higher_salary(self) -> None:
        """Демонстрирует метод get_vacancies_with_higher_salary()"""
        print("\n6. get_vacancies_with_higher_salary() - Вакансии с зарплатой выше средней:")
        print("-" * 80)
        
        high_salary_vacancies = self.db_manager.get_vacancies_with_higher_salary()
        
        if not high_salary_vacancies:
            print("Вакансии с зарплатой выше средней не найдены.")
            return
        
        print(f"{'№':<3} {'Название':<25} {'Компания':<20} {'Зарплата':<15}")
        print("-" * 80)
        
        for i, vacancy in enumerate(high_salary_vacancies[:5], 1):
            title = vacancy['title'][:24] if len(vacancy['title']) > 24 else vacancy['title']
            company = vacancy['company_name'][:19] if len(vacancy['company_name']) > 19 else vacancy['company_name']
            salary = vacancy['salary_info'][:14] if len(vacancy['salary_info']) > 14 else vacancy['salary_info']
            
            print(f"{i:<3} {title:<25} {company:<20} {salary:<15}")
        
        if len(high_salary_vacancies) > 5:
            print(f"... и еще {len(high_salary_vacancies) - 5} вакансий")
        
        print(f"\nВсего вакансий с высокой зарплатой: {len(high_salary_vacancies)}")
    
    def _demo_vacancies_with_keyword(self) -> None:
        """Демонстрирует метод get_vacancies_with_keyword()"""
        print("\n7. get_vacancies_with_keyword() - Поиск вакансий по ключевому слову:")
        print("-" * 80)
        
        keywords = ["python", "java", "разработчик", "менеджер"]
        
        for keyword in keywords:
            print(f"\nПоиск по ключевому слову '{keyword}':")
            keyword_vacancies = self.db_manager.get_vacancies_with_keyword(keyword)
            
            if keyword_vacancies:
                print(f"Найдено {len(keyword_vacancies)} вакансий")
                
                # Показываем первые 3 вакансии
                for i, vacancy in enumerate(keyword_vacancies[:3], 1):
                    title = vacancy['title'][:35]
                    company = vacancy['company_name'][:25]
                    print(f"  {i}. {title} - {company}")
                
                if len(keyword_vacancies) > 3:
                    print(f"  ... и еще {len(keyword_vacancies) - 3} вакансий")
            else:
                print(f"Вакансии с ключевым словом '{keyword}' не найдены")
    
    def _demo_database_stats(self) -> None:
        """Демонстрирует получение статистики БД"""
        print("\n8. Статистика базы данных:")
        print("-" * 40)
        
        stats = self.db_manager.get_database_stats()
        
        if stats:
            print(f"Общее количество вакансий: {stats.get('total_vacancies', 0)}")
            print(f"Общее количество компаний: {stats.get('total_companies', 0)}")
            print(f"Вакансий с указанной зарплатой: {stats.get('vacancies_with_salary', 0)}")
            print(f"Дата последней вакансии: {stats.get('latest_vacancy_date', 'Не определена')}")
        else:
            print("Не удалось получить статистику базы данных")


def main():
    """
    Главная функция для запуска демонстрации
    """
    try:
        demo = DBManagerDemo()
        demo.run_full_demo()
    except Exception as e:
        logger.error(f"Ошибка при запуске демонстрации DBManager: {e}")
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()
