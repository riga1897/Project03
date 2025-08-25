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
        all_vacancies = self.db_manager.get_all_vacancies()

        if not all_vacancies:
            print("Вакансии не найдены.")
            return

        # Сортируем вакансии: сначала по убыванию зарплаты, потом по названию
        def get_salary_value(vacancy):
            """Извлекает числовое значение зарплаты для сортировки"""
            salary_info = vacancy.get('salary_info', 'Не указана')
            if salary_info == 'Не указана':
                return 0

            # Извлекаем числа из строки зарплаты
            import re
            numbers = re.findall(r'\d+', salary_info)
            if numbers:
                # Берем максимальное значение (если есть диапазон)
                return max(int(num) for num in numbers)
            return 0

        sorted_vacancies = sorted(all_vacancies,
                                key=lambda x: (-get_salary_value(x), x.get('title', '')))

        print(f"{'№':<3} {'Название':<30} {'Компания':<25} {'Зарплата':<20}")
        print("-" * 85)

        # Показываем все вакансии (не ограничиваем до 15, так как целевых компаний всего 15)
        for i, vacancy in enumerate(sorted_vacancies[:15], 1):
            title = vacancy['title'][:29] if len(vacancy['title']) > 29 else vacancy['title']
            company = vacancy['company_name'][:24] if len(vacancy['company_name']) > 24 else vacancy['company_name']
            salary = vacancy['salary_info'][:19] if len(vacancy['salary_info']) > 19 else vacancy['salary_info']

            print(f"{i:<3} {title:<30} {company:<25} {salary:<20}")

        if len(sorted_vacancies) > 15:
            print(f"... и еще {len(sorted_vacancies) - 15} вакансий")

        print(f"\nВсего вакансий: {len(all_vacancies)}")

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
        print("-" * 90)

        try:
            high_salary_vacancies = self.db_manager.get_vacancies_with_higher_salary()

            if not high_salary_vacancies:
                print("Вакансии с зарплатой выше средней не найдены.")
                return

            # Сортируем по убыванию зарплаты, потом по названию
            def get_salary_value(vacancy):
                """Извлекает числовое значение зарплаты для сортировки"""
                # Проверяем, что vacancy - это словарь
                if not isinstance(vacancy, dict):
                    return 0
                    
                salary_info = vacancy.get('salary_info', 'Не указана')
                if salary_info == 'Не указана' or not salary_info:
                    return 0

                import re
                numbers = re.findall(r'\d+', str(salary_info))
                if numbers:
                    return max(int(num) for num in numbers)
                return 0

            # Фильтруем только валидные словари
            valid_vacancies = [v for v in high_salary_vacancies if isinstance(v, dict)]
            
            if not valid_vacancies:
                print("Нет валидных данных о вакансиях с высокой зарплатой.")
                return

            sorted_vacancies = sorted(valid_vacancies,
                                    key=lambda x: (-get_salary_value(x), x.get('title', '')))

            print(f"{'№':<3} {'Название':<35} {'Компания':<25} {'Зарплата':<20}")
            print("-" * 90)

            # Показываем все вакансии с высокой зарплатой
            for i, vacancy in enumerate(sorted_vacancies, 1):
                title = str(vacancy.get('title', 'Не указано'))[:34]
                company = str(vacancy.get('company_name', 'Не указана'))[:24]
                salary = str(vacancy.get('salary_info', 'Не указана'))[:19]

                print(f"{i:<3} {title:<35} {company:<25} {salary:<20}")

            print(f"\nВсего вакансий с высокой зарплатой: {len(valid_vacancies)}")
            
        except Exception as e:
            logger.error(f"Ошибка при демонстрации вакансий с высокой зарплатой: {e}")
            print(f"Ошибка при получении вакансий с высокой зарплатой: {e}")

    def _demo_vacancies_with_keyword(self) -> None:
        """Демонстрирует метод get_vacancies_with_keyword()"""
        print("\n7. get_vacancies_with_keyword() - Поиск вакансий по ключевому слову:")
        print("-" * 80)

        keywords = ["python", "java", "разработчик", "менеджер"]

        for keyword in keywords:
            try:
                print(f"\nПоиск по ключевому слову '{keyword}':")
                keyword_vacancies = self.db_manager.get_vacancies_with_keyword(keyword)

                if keyword_vacancies:
                    # Сортируем по убыванию зарплаты, потом по названию
                    def get_salary_value(vacancy):
                        """Извлекает числовое значение зарплаты для сортировки"""
                        if not isinstance(vacancy, dict):
                            return 0
                            
                        salary_info = vacancy.get('salary_info', 'Не указана')
                        if salary_info == 'Не указана' or not salary_info:
                            return 0

                        import re
                        numbers = re.findall(r'\d+', str(salary_info))
                        if numbers:
                            return max(int(num) for num in numbers)
                        return 0

                    # Фильтруем только валидные словари
                    valid_vacancies = [v for v in keyword_vacancies if isinstance(v, dict)]
                    
                    if not valid_vacancies:
                        print(f"Нет валидных данных для ключевого слова '{keyword}'")
                        continue

                    sorted_vacancies = sorted(valid_vacancies,
                                            key=lambda x: (-get_salary_value(x), x.get('title', '')))

                    print(f"Найдено {len(sorted_vacancies)} вакансий")
                    print(f"{'№':<3} {'Название':<40} {'Компания':<25} {'Зарплата':<15}")
                    print("-" * 88)

                    # Показываем максимум 15 вакансий
                    for i, vacancy in enumerate(sorted_vacancies[:15], 1):
                        title = str(vacancy.get('title', 'Не указано'))[:39]
                        company = str(vacancy.get('company_name', 'Не указана'))[:24]
                        salary = str(vacancy.get('salary_info', 'Не указана'))[:14]
                        print(f"{i:<3} {title:<40} {company:<25} {salary:<15}")

                    if len(sorted_vacancies) > 15:
                        print(f"  ... и еще {len(sorted_vacancies) - 15} вакансий")
                else:
                    print(f"Вакансии с ключевым словом '{keyword}' не найдены")
                    
            except Exception as e:
                logger.error(f"Ошибка при поиске по ключевому слову '{keyword}': {e}")
                print(f"Ошибка при поиске по ключевому слову '{keyword}': {e}")

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