import logging
from typing import List

from src.utils.search_utils import filter_vacancies_by_keyword, vacancy_contains_keyword
from src.vacancies.models import Vacancy

logger = logging.getLogger(__name__)


class VacancyOperations:
    """Класс для операций с вакансиями"""

    @staticmethod
    def get_vacancies_with_salary(vacancies: List[Vacancy]) -> List[Vacancy]:
        """
        Фильтрация вакансий, у которых указана зарплата

        Args:
            vacancies: Список вакансий для фильтрации

        Returns:
            List[Vacancy]: Список вакансий с указанной зарплатой
        """
        return [
            v
            for v in vacancies
            if v.salary
            and (
                (isinstance(v.salary, dict) and (v.salary.get("from") or v.salary.get("to")))
                or (
                    not isinstance(v.salary, dict)
                    and (getattr(v.salary, "salary_from", None) or getattr(v.salary, "salary_to", None) or 
                         getattr(v.salary, "amount_from", None) or getattr(v.salary, "amount_to", None))
                )
            )
        ]

    @staticmethod
    def sort_vacancies_by_salary(vacancies: List[Vacancy], reverse: bool = True) -> List[Vacancy]:
        """
        Сортировка вакансий по зарплате

        Args:
            vacancies: Список вакансий для сортировки
            reverse: Сортировка по убыванию (True) или возрастанию (False)

        Returns:
            List[Vacancy]: Отсортированный список вакансий
        """

        def get_sort_key(vacancy: Vacancy) -> int:
            """Локальная функция для получения ключа сортировки по зарплате."""
            if vacancy.salary:
                # Обработка нового формата (словарь)
                if isinstance(vacancy.salary, dict):
                    salary_from = vacancy.salary.get("from", 0) or 0
                    salary_to = vacancy.salary.get("to", 0) or 0
                    # Возвращаем максимальное из from/to или среднее
                    if salary_from and salary_to:
                        return max(salary_from, salary_to)
                    return salary_from or salary_to
                # Обработка старого формата (объект Salary)
                elif hasattr(vacancy.salary, "get_max_salary"):
                    max_sal = vacancy.salary.get_max_salary()
                    return max_sal if max_sal is not None else 0
            return 0

        return sorted(vacancies, key=get_sort_key, reverse=reverse)

    @staticmethod
    def filter_vacancies_by_min_salary(vacancies: List[Vacancy], min_salary: int) -> List[Vacancy]:
        """
        Фильтрация вакансий по минимальной зарплате

        Args:
            vacancies: Список вакансий для фильтрации
            min_salary: Минимальная зарплата

        Returns:
            List[Vacancy]: Список отфильтрованных вакансий
        """
        filtered_vacancies = []

        for vacancy in vacancies:
            # Пропускаем вакансии без зарплаты
            if not vacancy.salary:
                continue

            # Получаем значения зарплаты (поддержка нового и старого формата)
            if isinstance(vacancy.salary, dict):
                salary_from = vacancy.salary.get("from")
                salary_to = vacancy.salary.get("to")
            else:
                # Поддержка разных названий атрибутов в объектах зарплаты
                salary_from = (getattr(vacancy.salary, "salary_from", None) or 
                             getattr(vacancy.salary, "amount_from", None))
                salary_to = (getattr(vacancy.salary, "salary_to", None) or 
                           getattr(vacancy.salary, "amount_to", None))

            # Если нет ни одного значения зарплаты, пропускаем
            if not salary_from and not salary_to:
                continue

            # Правильная логика для минимальной зарплаты:
            # Вакансия подходит если её максимальная зарплата >= min_salary
            vacancy_max = salary_to or salary_from  # Берем максимум из диапазона или единственное значение
            
            if vacancy_max >= min_salary:
                filtered_vacancies.append(vacancy)

        logger.info(
            f"Отфильтровано {len(filtered_vacancies)} вакансий из {len(vacancies)} с минимальной зарплатой {min_salary}"
        )
        return filtered_vacancies

    @staticmethod
    def filter_vacancies_by_max_salary(vacancies: List[Vacancy], max_salary: int) -> List[Vacancy]:
        """
        Фильтрация вакансий по максимальной зарплате

        Args:
            vacancies: Список вакансий для фильтрации
            max_salary: Максимальная зарплата

        Returns:
            List[Vacancy]: Список отфильтрованных вакансий
        """
        filtered_vacancies = []

        for vacancy in vacancies:
            # Пропускаем вакансии без зарплаты
            if not vacancy.salary:
                continue

            # Получаем значения зарплаты (поддержка нового и старого формата)
            if isinstance(vacancy.salary, dict):
                salary_from = vacancy.salary.get("from")
                salary_to = vacancy.salary.get("to")
            else:
                # Поддержка разных названий атрибутов в объектах зарплаты
                salary_from = (getattr(vacancy.salary, "salary_from", None) or 
                             getattr(vacancy.salary, "amount_from", None))
                salary_to = (getattr(vacancy.salary, "salary_to", None) or 
                           getattr(vacancy.salary, "amount_to", None))

            # Если нет ни одного значения зарплаты, пропускаем
            if not salary_from and not salary_to:
                continue

            # Правильная логика для максимальной зарплаты:
            # Вакансия подходит если её минимальная зарплата <= max_salary
            vacancy_min = salary_from or salary_to  # Берем минимум из диапазона или единственное значение
            
            if vacancy_min <= max_salary:
                filtered_vacancies.append(vacancy)

        logger.info(
            f"Отфильтровано {len(filtered_vacancies)} вакансий из {len(vacancies)} с максимальной зарплатой {max_salary}"
        )
        return filtered_vacancies

    @staticmethod
    def filter_vacancies_by_salary_range(vacancies: List[Vacancy], min_salary: int, max_salary: int) -> List[Vacancy]:
        """
        Фильтрация вакансий по диапазону зарплат

        Args:
            vacancies: Список вакансий для фильтрации
            min_salary: Минимальная зарплата диапазона
            max_salary: Максимальная зарплата диапазона

        Returns:
            List[Vacancy]: Список отфильтрованных вакансий
        """
        filtered_vacancies = []

        for vacancy in vacancies:
            # Пропускаем вакансии без зарплаты
            if not vacancy.salary:
                continue

            # Получаем значения зарплаты (поддержка нового и старого формата)
            if isinstance(vacancy.salary, dict):
                salary_from = vacancy.salary.get("from")
                salary_to = vacancy.salary.get("to")
            else:
                # Поддержка разных названий атрибутов в объектах зарплаты
                salary_from = (getattr(vacancy.salary, "salary_from", None) or 
                             getattr(vacancy.salary, "amount_from", None))
                salary_to = (getattr(vacancy.salary, "salary_to", None) or 
                           getattr(vacancy.salary, "amount_to", None))

            # Если нет ни одного значения зарплаты, пропускаем
            if not salary_from and not salary_to:
                continue

            # Правильная логика для диапазона зарплат:
            # Вакансия подходит если её максимальная >= min_salary И минимальная <= max_salary
            vacancy_min = salary_from or salary_to
            vacancy_max = salary_to or salary_from
            
            # Проверяем, попадает ли вакансия в диапазон
            if vacancy_max >= min_salary and vacancy_min <= max_salary:
                filtered_vacancies.append(vacancy)

        logger.info(
            f"Отфильтровано {len(filtered_vacancies)} вакансий из {len(vacancies)} по диапазону {min_salary}-{max_salary}"
        )
        return filtered_vacancies

    @staticmethod
    def filter_vacancies_by_multiple_keywords(vacancies: List[Vacancy], keywords: List[str]) -> List[Vacancy]:
        """
        Фильтрация вакансий по нескольким ключевым словам

        Args:
            vacancies: Список вакансий для фильтрации
            keywords: Список ключевых слов для поиска

        Returns:
            List[Vacancy]: Список отфильтрованных вакансий
        """
        # ЗАГЛУШКА: Поиск теперь выполняется только в PostgresSaver.search_vacancies_batch
        logger.warning("Метод search_by_keywords устарел. Используйте SQLFilterService")
        return vacancies  # Возвращаем без изменений для обратной совместимости

    @staticmethod
    def search_vacancies_advanced(vacancies: List[Vacancy], query: str) -> List[Vacancy]:
        """
        Продвинутый поиск по вакансиям с поддержкой операторов

        Args:
            vacancies: Список вакансий для поиска
            query: Поисковый запрос (может содержать операторы AND, OR)

        Returns:
            List[Vacancy]: Список найденных вакансий
        """
        # Простая обработка AND/OR операторов
        if " AND " in query.upper():
            # Разбираем более аккуратно, сохраняя регистр
            parts = query.split()
            keywords = []
            current_keyword: List[str] = []
            for part in parts:
                if part.upper() == "AND":
                    if current_keyword:
                        keywords.append(" ".join(current_keyword))
                        current_keyword = []
                else:
                    current_keyword.append(part)
            if current_keyword:
                keywords.append(" ".join(current_keyword))

            # Для AND ищем вакансии, которые содержат ВСЕ ключевые слова
            result = []
            for vacancy in vacancies:
                found_all = True
                for keyword in keywords:
                    # Проверяем наличие каждого ключевого слова в вакансии
                    if not vacancy_contains_keyword(vacancy, keyword.strip()):
                        found_all = False
                        break
                if found_all:
                    result.append(vacancy)
            return result

        elif " OR " in query.upper():
            # Аналогично для OR
            parts = query.split()
            keywords = []
            current_keyword = []
            for part in parts:
                if part.upper() == "OR":
                    if current_keyword:
                        keywords.append(" ".join(current_keyword))
                        current_keyword = []
                else:
                    current_keyword.append(part)
            if current_keyword:
                keywords.append(" ".join(current_keyword))

            return VacancyOperations.filter_vacancies_by_multiple_keywords(vacancies, [kw.strip() for kw in keywords])
        elif "," in query:
            # Поиск с запятой как разделителем (OR)
            keywords = [kw.strip() for kw in query.split(",") if kw.strip()]
            return VacancyOperations.filter_vacancies_by_multiple_keywords(vacancies, keywords)
        elif " " in query.strip() and not any(op in query.upper() for op in [" AND ", " OR "]):
            # Поиск с пробелами как разделителем (OR по умолчанию)
            keywords = [kw.strip() for kw in query.split() if kw.strip()]
            return VacancyOperations.filter_vacancies_by_multiple_keywords(vacancies, keywords)
        else:
            # Простой поиск по одному ключевому слову
            return filter_vacancies_by_keyword(vacancies, query)

    @staticmethod
    def search_vacancies_by_keyword(vacancies: List[Vacancy], keyword: str, use_sql: bool = True) -> List[Vacancy]:
        """
        Поиск вакансий по ключевому слову в названии или описании
        Поддерживает как SQL-поиск (быстрый), так и Python-поиск (для данных из API)

        Args:
            vacancies: Список вакансий для поиска
            keyword: Ключевое слово для поиска
            use_sql: Использовать SQL-поиск через БД (по умолчанию True)

        Returns:
            List[Vacancy]: Список найденных вакансий
        """
        if not keyword or not keyword.strip():
            return []

        # Если можем использовать SQL и у нас есть PostgresSaver
        if use_sql:
            try:
                from src.storage.postgres_saver import PostgresSaver

                postgres_saver = PostgresSaver()

                # SQL-поиск по ключевому слову в БД
                sql_results = postgres_saver.search_vacancies_batch([keyword], limit=1000)
                if sql_results:
                    return sql_results
            except Exception as e:
                logger.error(f"SQL-поиск не удался: {e}")
                logger.info("Поиск должен выполняться только через PostgresSaver.search_vacancies_batch")
                return []  # Возвращаем пустой результат

        # Если SQL не сработал, возвращаем пустой результат
        return []

    @staticmethod
    def debug_vacancy_search(vacancy: Vacancy, keyword: str) -> None:
        """
        Отладочная функция для проверки содержимого вакансии при поиске

        Выводит подробную информацию о вакансии и показывает, в каких полях
        найдено ключевое слово.
        """
        print(f"\n=== ОТЛАДКА ПОИСКА: '{keyword}' ===")
        print(f"Вакансия: {vacancy.title}")
        print(f"Компания: {vacancy.employer}")
        # print(f"Ключевые слова: {vacancy.keywords}")
        print(f"URL: {vacancy.url}")

        # Проверяем каждое поле
        fields_to_check = [
            ("Название", vacancy.title),
            ("Описание", vacancy.description),
            ("Требования", vacancy.requirements),
            ("Обязанности", vacancy.responsibilities),
            ("Компания", vacancy.employer),
        ]

        for field_name, field_value in fields_to_check:
            if field_value and keyword.lower() in str(field_value).lower():
                logger.debug(f"Найдено в поле '{field_name}': ...{str(field_value)[:100]}...")

        print("=" * 50)

    @staticmethod
    def debug_vacancy_keywords(vacancy: Vacancy) -> None:
        """
        Отладочная функция для проверки извлечения ключевых слов
        """
        print("\n=== ОТЛАДКА КЛЮЧЕВЫХ СЛОВ ===")
        print(f"Вакансия: {vacancy.title}")
        print(f"URL: {vacancy.url}")
        # print(f"Автоматически извлеченные ключевые слова: {vacancy.keywords}")

        # Показываем текст, из которого извлекались ключевые слова
        full_text = " ".join(
            [vacancy.description or "", vacancy.requirements or "", vacancy.responsibilities or ""]
        ).lower()

        print(f"Полный текст для анализа (первые 200 символов): {full_text[:200]}...")

        # Проверяем конкретные ключевые слова
        test_keywords = ["excel", "1c", "1с", "r"]
        for keyword in test_keywords:
            import re

            pattern = r"\b" + re.escape(keyword) + r"\b"
            matches = re.findall(pattern, full_text)
            if matches:
                logger.debug(f"Найдено '{keyword}': {matches}")
            else:
                logger.debug(f"НЕ найдено '{keyword}'")

        print("=" * 50)
