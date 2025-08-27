"""
Демонстрационный модуль для работы с классом DBManager

Показывает использование всех методов DBManager согласно требованиям проекта.
Позволяет протестировать функциональность работы с базой данных.
"""

import logging
from typing import Optional
import re
from datetime import datetime

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
        print(" АНАЛИЗ ДАННЫХ ТОЛЬКО ПО 15 ЦЕЛЕВЫМ КОМПАНИЯМ")
        print(" Все методы фильтруют результаты по целевым компаниям")
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
        print(" ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
        print(" Показана статистика ТОЛЬКО по 15 целевым компаниям из конфигурации")
        print(" Все результаты отфильтрованы по списку TARGET_COMPANIES")
        print(" Анализ исключает вакансии от других компаний")
        print("=" * 80)

    def _check_connection(self) -> bool:
        """
        Проверяет подключение к БД

        Returns:
            bool: True если подключение успешно
        """
        print("\n1. Проверка подключения к базе данных...")

        if self.db_manager.check_connection():
            print(" Подключение к базе данных успешно установлено")
            return True
        else:
            print("Ошибка подключения к базе данных")
            print("Убедитесь, что PostgreSQL запущен и настроен корректно")
            return False

    def _show_target_companies(self) -> None:
        """Показывает информацию о целевых компаниях"""
        print("\n2. Целевые компании проекта (15 компаний):")
        print("-" * 60)

        from src.config.target_companies import TargetCompanies
        TARGET_COMPANIES = TargetCompanies.get_all_companies()

        print("Анализ будет проводиться по следующим целевым компаниям:")
        print()

        for i, company in enumerate(TARGET_COMPANIES, 1):
            print(f"{i:2d}. {company.name} (HH ID: {company.hh_id})")
            if company.sj_id:
                print(f"      SuperJob ID: {company.sj_id}")
            if company.description:
                print(f"      {company.description}")
            print()

        print(f"\nВсего целевых компаний: {len(TARGET_COMPANIES)}")

    def _demo_companies_and_vacancies_count(self) -> None:
        """Демонстрирует метод get_companies_and_vacancies_count() для целевых компаний"""
        print("\n3. get_companies_and_vacancies_count() - Анализ вакансий по целевым компаниям:")
        print("-" * 80)

        from src.config.target_companies import TargetCompanies
        TARGET_COMPANIES = TargetCompanies.get_all_companies()

        print("Анализ показывает только данные от целевых компаний из конфигурации проекта")
        print("Метод фильтрует результаты и показывает статистику по всем 15 целевым компаниям")
        print()

        # Получаем данные специально по целевым компаниям
        companies_data = self.db_manager.get_target_companies_analysis()

        if not companies_data:
            print("Нет данных о целевых компаниях")
            print("Выполните поиск вакансий через пункт меню 1 для получения данных")
            return

        print(f"{'№':<3} {'Целевая компания':<35} {'Количество вакансий':<20}")
        print("-" * 80)

        total_vacancies = 0
        companies_with_vacancies = 0

        # Показываем результаты в том порядке, как они возвращены методом
        # (метод уже фильтрует и сопоставляет целевые компании)
        for i, (company_name, vacancy_count) in enumerate(companies_data, 1):
            status = "[+]" if vacancy_count > 0 else "[-]"
            print(f"{i:<3} {status} {company_name:<32} {vacancy_count:<20}")

            total_vacancies += vacancy_count
            if vacancy_count > 0:
                companies_with_vacancies += 1

        print("-" * 80)
        print(f"АНАЛИЗ ПО ЦЕЛЕВЫМ КОМПАНИЯМ:")
        print(f"   • Целевых компаний с вакансиями: {companies_with_vacancies} из {len(TARGET_COMPANIES)}")
        print(f"   • Всего вакансий от целевых компаний: {total_vacancies}")
        print(f"   • Покрытие целевых компаний: {(companies_with_vacancies/len(TARGET_COMPANIES)*100):.1f}%")

        if total_vacancies == 0:
            print("СОВЕТ: Для получения данных выполните поиск вакансий через пункт меню 1")
            print("   Выберите источник API и введите запрос для поиска")
        else:
            print(f"\nРЕЗУЛЬТАТ: Найдены вакансии от {companies_with_vacancies} целевых компаний")
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
            numbers = re.findall(r'\d+', salary_info)
            if numbers:
                # Берем максимальное значение (если есть диапазон)
                return max(int(num) for num in numbers)
            return 0

        sorted_vacancies = sorted(all_vacancies,
                                key=lambda x: (-get_salary_value(x), x.get('title', '')))

        print(f"{'№':<3} {'Название':<50} {'Зарплата':<25}")
        print("-" * 80)

        # Показываем первые 25 вакансий
        for i, vacancy in enumerate(sorted_vacancies[:25], 1):
            title = vacancy['title'][:49] if len(vacancy['title']) > 49 else vacancy['title']
            salary = vacancy['salary_info'][:24] if len(vacancy['salary_info']) > 24 else vacancy['salary_info']

            print(f"{i:<3} {title:<50} {salary:<25}")

        if len(sorted_vacancies) > 25:
            print(f"... и еще {len(sorted_vacancies) - 25} вакансий")

        print(f"\nВсего вакансий: {len(sorted_vacancies)}")

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
                print("Возможные причины:")
                print("• Недостаточно вакансий с указанной зарплатой")
                print("• Все вакансии имеют зарплату ниже или равную средней")
                return

            print(f"{'№':<3} {'Название':<35} {'Компания':<25} {'Зарплата':<20}")
            print("-" * 90)

            # Показываем первые 15 вакансий с высокой зарплатой
            for i, vacancy in enumerate(high_salary_vacancies[:15], 1):
                # RealDictCursor возвращает словари
                title = str(vacancy.get('title', ''))[:34]
                company = str(vacancy.get('company_name', ''))[:24]
                salary = str(vacancy.get('salary_info', ''))[:19]

                print(f"{i:<3} {title:<35} {company:<25} {salary:<20}")

            if len(high_salary_vacancies) > 15:
                print(f"... и еще {len(high_salary_vacancies) - 15} вакансий")

            print(f"Всего вакансий с зарплатой выше средней: {len(high_salary_vacancies)}")

        except Exception as e:
            logger.error(f"Ошибка при демонстрации вакансий с высокой зарплатой: {e}")
            print(f"Ошибка при получении вакансий с высокой зарплатой: {e}")
            print(f"Тип данных результата: {type(high_salary_vacancies) if 'high_salary_vacancies' in locals() else 'не определен'}")
            if 'high_salary_vacancies' in locals() and high_salary_vacancies and len(high_salary_vacancies) > 0:
                print(f"Первый элемент: {high_salary_vacancies[0]}")
                print(f"Тип первого элемента: {type(high_salary_vacancies[0])}")
                if hasattr(high_salary_vacancies[0], 'keys'):
                    print(f"Ключи: {list(high_salary_vacancies[0].keys())}")
            print("\nВозможные причины:")
            print("• Нет подключения к базе данных")
            print("• Ошибка в SQL-запросах")
            print("• Проблемы с форматированием данных")

    def _demo_vacancies_with_keyword(self) -> None:
        """Демонстрирует метод get_vacancies_with_keyword()"""
        print("\n7. get_vacancies_with_keyword() - Поиск вакансий по ключевому слову:")
        print("-" * 80)

        keywords = ["python", "java", "разработчик", "менеджер", "аналитик"]

        for keyword in keywords:
            print(f"\nПоиск по ключевому слову '{keyword}':")

            try:
                vacancies = self.db_manager.get_vacancies_with_keyword(keyword)

                if not vacancies:
                    print(f" Вакансии по ключевому слову '{keyword}' не найдены.")
                    continue

                print(f" Найдено {len(vacancies)} вакансий:")
                print(f"{'№':<3} {'Название':<50} {'Зарплата':<25}")
                print("-" * 80)

                # Показываем первые 15 вакансий
                for i, vacancy in enumerate(vacancies[:15], 1):
                    # RealDictCursor возвращает словари
                    title = str(vacancy.get('title', ''))[:49]
                    salary = str(vacancy.get('salary_info', ''))[:24]

                    print(f"{i:<3} {title:<50} {salary:<25}")

                if len(vacancies) > 15:
                    print(f"... и еще {len(vacancies) - 15} вакансий")

            except Exception as e:
                logger.error(f"Ошибка при поиске по ключевому слову '{keyword}': {e}")
                print(f" Ошибка при поиске по ключевому слову '{keyword}': {e}")
                print("   Возможные причины: проблемы с SQL-запросом или данными")
                print(f"   Тип результата: {type(vacancies) if 'vacancies' in locals() else 'не определен'}")
                if 'vacancies' in locals() and vacancies and len(vacancies) > 0:
                    print(f"   Первый элемент: {vacancies[0]}")
                    print(f"   Тип первого элемента: {type(vacancies[0])}")
                    if hasattr(vacancies[0], 'keys'):
                        print(f"   Ключи: {list(vacancies[0].keys())}")

    def _demo_database_stats(self) -> None:
        """Демонстрирует получение статистики БД"""
        print("\n8. Статистика базы данных:")
        print("----------------------------------------")

        # Примеры дат убраны для чистоты вывода
        try:
            with self.db_manager._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT published_at, created_at
                        FROM vacancies
                        WHERE published_at IS NOT NULL
                        LIMIT 3
                    """)
                    date_samples = cursor.fetchall()

                    if date_samples:
                        print(" Примеры дат в БД:")
                        for i, (pub_date, create_date) in enumerate(date_samples, 1):
                            # Форматируем даты в российском формате
                            if isinstance(pub_date, datetime):
                                pub_date_str = pub_date.strftime('%d.%m.%Y %H:%M:%S')
                            else:
                                pub_date_str = str(pub_date)

                            if isinstance(create_date, datetime):
                                create_date_str = create_date.strftime('%d.%m.%Y %H:%M:%S')
                            else:
                                create_date_str = str(create_date)

                            print(f"   {i}. published_at: {pub_date_str} (тип: {type(pub_date)})")
                            print(f"      created_at: {create_date_str} (тип: {type(create_date)})")
                        print()
        except Exception as e:
            print(f"Ошибка при получении примеров дат: {e}")


        stats = self.db_manager.get_database_stats()
        if stats:
            print(f"Общее количество вакансий: {stats.get('total_vacancies', 0)}")
            print(f"Общее количество компаний: {stats.get('total_companies', 0)}")
            print(f"Вакансий с указанной зарплатой: {stats.get('vacancies_with_salary', 0)}")

            # Обрабатываем даты
            latest_date = stats.get('latest_vacancy_date')
            earliest_date = stats.get('earliest_vacancy_date')

            if latest_date:
                if hasattr(latest_date, 'strftime'):
                    latest_str = latest_date.strftime('%d.%m.%Y %H:%M:%S')
                else:
                    latest_str = str(latest_date)
                print(f"Дата последней вакансии: {latest_str}")
            else:
                print("Дата последней вакансии: Не указана")

            if earliest_date:
                if hasattr(earliest_date, 'strftime'):
                    earliest_str = earliest_date.strftime('%d.%m.%Y %H:%M:%S')
                else:
                    earliest_str = str(earliest_date)
                print(f"Дата первой вакансии: {earliest_str}")
            else:
                print("Дата первой вакансии: Не указана")

            # Дополнительная статистика если есть
            if stats.get('vacancies_last_week'):
                print(f"Вакансий за последнюю неделю: {stats.get('vacancies_last_week', 0)}")
            if stats.get('vacancies_last_month'):
                print(f"Вакансий за последний месяц: {stats.get('vacancies_last_month', 0)}")

            # Статистика заполненности полей
            total = stats.get('total_vacancies', 0)
            if total > 0:
                print("\n📊 Заполненность полей:")
                desc_pct = (stats.get('vacancies_with_description', 0) / total * 100) if total else 0
                req_pct = (stats.get('vacancies_with_requirements', 0) / total * 100) if total else 0
                area_pct = (stats.get('vacancies_with_area', 0) / total * 100) if total else 0
                date_pct = (stats.get('vacancies_with_published_date', 0) / total * 100) if total else 0

                print(f"Описание: {stats.get('vacancies_with_description', 0)}/{total} ({desc_pct:.1f}%)")
                print(f"Требования: {stats.get('vacancies_with_requirements', 0)}/{total} ({req_pct:.1f}%)")
                print(f"Регион: {stats.get('vacancies_with_area', 0)}/{total} ({area_pct:.1f}%)")
                print(f"Дата публикации: {stats.get('vacancies_with_published_date', 0)}/{total} ({date_pct:.1f}%)")
        else:
            print(" Ошибка при получении статистики базы данных")


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