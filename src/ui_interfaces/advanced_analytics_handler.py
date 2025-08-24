
import logging
from typing import Optional, Dict, Any

from src.utils.ui_helpers import get_user_input, get_positive_integer, confirm_action
from src.utils.ui_navigation import quick_paginate
from src.utils.vacancy_formatter import VacancyFormatter

logger = logging.getLogger(__name__)


class AdvancedAnalyticsHandler:
    """Обработчик расширенной аналитики и SQL-оптимизированных запросов"""

    def __init__(self, storage):
        """
        Инициализация обработчика аналитики
        
        Args:
            storage: Хранилище вакансий (поддерживающее новые методы)
        """
        self.storage = storage

    def show_analytics_menu(self) -> None:
        """Показать меню аналитики"""
        while True:
            print("\n" + "="*50)
            print("РАСШИРЕННАЯ АНАЛИТИКА ВАКАНСИЙ")
            print("="*50)
            print("1. Статистика по зарплатам")
            print("2. Топ работодателей")
            print("3. Популярные ключевые слова")
            print("4. Расширенный поиск с фильтрами")
            print("5. Умная пагинация вакансий")
            print("0. Назад")
            print("-"*50)
            
            choice = get_user_input("Выберите опцию: ")
            
            if choice == "1":
                self._show_salary_statistics()
            elif choice == "2":
                self._show_top_employers()
            elif choice == "3":
                self._show_popular_keywords()
            elif choice == "4":
                self._advanced_search()
            elif choice == "5":
                self._smart_pagination()
            elif choice == "0":
                break
            else:
                print("Неверный выбор. Попробуйте снова.")

    def _show_salary_statistics(self) -> None:
        """Показать статистику по зарплатам"""
        print("\n📊 СТАТИСТИКА ПО ЗАРПЛАТАМ")
        
        # Можно добавить фильтры
        filters = self._get_basic_filters()
        
        try:
            stats = self.storage.get_salary_statistics(filters)
            
            if not stats:
                print("❌ Не удалось получить статистику")
                return
                
            print(f"\n📈 Общая статистика:")
            print(f"  Всего вакансий: {stats.get('total_vacancies', 0)}")
            print(f"  С указанием зарплаты: {stats.get('vacancies_with_salary', 0)}")
            print(f"  Покрытие зарплат: {stats.get('salary_coverage', 0)}%")
            print(f"\n💰 Зарплатная статистика:")
            print(f"  Минимальная: {stats.get('min_salary', 0):,} ₽")
            print(f"  Максимальная: {stats.get('max_salary', 0):,} ₽")
            print(f"  Средняя: {stats.get('avg_salary', 0):,} ₽")
            print(f"  Медиана: {stats.get('median_salary', 0):,} ₽")
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            print(f"❌ Ошибка: {e}")

    def _show_top_employers(self) -> None:
        """Показать топ работодателей"""
        print("\n🏢 ТОП РАБОТОДАТЕЛЕЙ")
        
        limit = get_positive_integer("Количество работодателей в топе (по умолчанию 10): ") or 10
        filters = self._get_basic_filters()
        
        try:
            employers = self.storage.get_top_employers(limit, filters)
            
            if not employers:
                print("❌ Работодатели не найдены")
                return
            
            print(f"\n🎯 Топ {len(employers)} работодателей:")
            print("-" * 80)
            
            for i, emp in enumerate(employers, 1):
                avg_salary_str = f"{emp['avg_salary']:,} ₽" if emp['avg_salary'] > 0 else "не указана"
                print(f"{i:2}. {emp['employer']}")
                print(f"    📝 Вакансий: {emp['vacancy_count']}")
                print(f"    💰 Средняя зарплата: {avg_salary_str}")
                print(f"    📊 Вакансий с зарплатой: {emp['vacancies_with_salary']}")
                print()
                
        except Exception as e:
            logger.error(f"Ошибка получения топа работодателей: {e}")
            print(f"❌ Ошибка: {e}")

    def _show_popular_keywords(self) -> None:
        """Показать популярные ключевые слова"""
        print("\n🔍 ПОПУЛЯРНЫЕ КЛЮЧЕВЫЕ СЛОВА")
        
        limit = get_positive_integer("Количество ключевых слов (по умолчанию 20): ") or 20
        filters = self._get_basic_filters()
        
        try:
            keywords = self.storage.get_popular_keywords(limit, filters)
            
            if not keywords:
                print("❌ Ключевые слова не найдены")
                return
            
            print(f"\n📋 Топ {len(keywords)} ключевых слов:")
            print("-" * 50)
            
            # Группируем по частоте для лучшего отображения
            max_freq = keywords[0]['frequency'] if keywords else 1
            
            for i, kw in enumerate(keywords, 1):
                frequency = kw['frequency']
                bar_length = min(20, int(frequency / max_freq * 20))
                bar = "█" * bar_length + "░" * (20 - bar_length)
                
                print(f"{i:2}. {kw['keyword']:<15} {bar} {frequency}")
                
        except Exception as e:
            logger.error(f"Ошибка анализа ключевых слов: {e}")
            print(f"❌ Ошибка: {e}")

    def _advanced_search(self) -> None:
        """Расширенный поиск с множественными фильтрами"""
        print("\n🔎 РАСШИРЕННЫЙ ПОИСК")
        
        # Сбор параметров поиска
        keywords_input = get_user_input("Ключевые слова (через запятую): ", required=False)
        keywords = [kw.strip() for kw in keywords_input.split(",")] if keywords_input else []
        
        # Диапазон зарплат
        salary_range = None
        if confirm_action("Задать диапазон зарплат?"):
            min_salary = get_positive_integer("Минимальная зарплата: ")
            max_salary = get_positive_integer("Максимальная зарплата: ")
            if min_salary and max_salary:
                salary_range = (min_salary, max_salary)
        
        # Уровни опыта
        experience_levels = None
        if confirm_action("Фильтровать по опыту?"):
            exp_input = get_user_input("Уровни опыта (junior, middle, senior через запятую): ", required=False)
            experience_levels = [exp.strip() for exp in exp_input.split(",")] if exp_input else None
        
        # Типы занятости
        employment_types = None
        if confirm_action("Фильтровать по типу занятости?"):
            emp_input = get_user_input("Типы занятости (полная, частичная и т.д. через запятую): ", required=False)
            employment_types = [emp.strip() for emp in emp_input.split(",")] if emp_input else None
        
        # Пагинация
        page_size = get_positive_integer("Количество результатов на странице (по умолчанию 10): ") or 10
        
        try:
            page = 1
            while True:
                vacancies, total_count = self.storage.search_vacancies_advanced(
                    keywords=keywords,
                    salary_range=salary_range,
                    experience_levels=experience_levels,
                    employment_types=employment_types,
                    page=page,
                    page_size=page_size
                )
                
                if not vacancies and page == 1:
                    print("❌ Вакансии не найдены по заданным критериям")
                    return
                
                print(f"\n🎯 Результаты поиска (страница {page}, найдено {total_count})")
                print("="*60)
                
                for i, vacancy in enumerate(vacancies, (page-1)*page_size + 1):
                    print(VacancyFormatter.format_vacancy_brief(vacancy, i))
                
                # Навигация
                if total_count > page * page_size:
                    if confirm_action(f"Показать следующие {page_size} результатов?"):
                        page += 1
                        continue
                
                break
                
        except Exception as e:
            logger.error(f"Ошибка расширенного поиска: {e}")
            print(f"❌ Ошибка: {e}")

    def _smart_pagination(self) -> None:
        """Умная пагинация с сортировкой"""
        print("\n📄 УМНАЯ ПАГИНАЦИЯ")
        
        # Параметры
        page_size = get_positive_integer("Размер страницы (по умолчанию 10): ") or 10
        
        print("\nВыберите сортировку:")
        print("1. По дате создания (новые сначала)")
        print("2. По дате создания (старые сначала)")
        print("3. По зарплате (по убыванию)")
        print("4. По зарплате (по возрастанию)")
        print("5. По названию (А-Я)")
        print("6. По названию (Я-А)")
        
        sort_choice = get_user_input("Выбор сортировки (по умолчанию 1): ") or "1"
        
        sort_options = {
            "1": ("created_at", True),
            "2": ("created_at", False),
            "3": ("salary", True),
            "4": ("salary", False),
            "5": ("title", False),
            "6": ("title", True)
        }
        
        sort_by, sort_desc = sort_options.get(sort_choice, ("created_at", True))
        filters = self._get_basic_filters()
        
        try:
            page = 1
            while True:
                vacancies, total_count = self.storage.get_vacancies_paginated(
                    page=page,
                    page_size=page_size,
                    filters=filters,
                    sort_by=sort_by,
                    sort_desc=sort_desc
                )
                
                if not vacancies and page == 1:
                    print("❌ Вакансии не найдены")
                    return
                
                total_pages = (total_count + page_size - 1) // page_size
                print(f"\n📋 Страница {page} из {total_pages} (всего {total_count} вакансий)")
                print("="*60)
                
                for i, vacancy in enumerate(vacancies, (page-1)*page_size + 1):
                    print(VacancyFormatter.format_vacancy_brief(vacancy, i))
                
                # Навигация
                print(f"\n📖 Навигация:")
                if page > 1:
                    print("  ← p - предыдущая страница")
                if page < total_pages:
                    print("  → n - следующая страница")
                print("  🔍 s - новый поиск")
                print("  ❌ q - выход")
                
                nav_choice = get_user_input("Ваш выбор: ").lower()
                
                if nav_choice == 'n' and page < total_pages:
                    page += 1
                elif nav_choice == 'p' and page > 1:
                    page -= 1
                elif nav_choice == 's':
                    return self._smart_pagination()
                elif nav_choice == 'q':
                    break
                else:
                    print("❓ Неверный выбор")
                
        except Exception as e:
            logger.error(f"Ошибка пагинации: {e}")
            print(f"❌ Ошибка: {e}")

    def _get_basic_filters(self) -> Optional[Dict[str, Any]]:
        """Получить базовые фильтры от пользователя"""
        if not confirm_action("Применить фильтры?"):
            return None
        
        filters = {}
        
        title_filter = get_user_input("Фильтр по названию (часть названия): ", required=False)
        if title_filter:
            filters['title'] = title_filter
        
        employer_filter = get_user_input("Фильтр по работодателю: ", required=False)
        if employer_filter:
            filters['employer'] = employer_filter
        
        return filters if filters else None
