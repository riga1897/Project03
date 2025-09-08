import logging
from typing import List, Optional

from src.utils.vacancy_formatter import vacancy_formatter
from src.utils.vacancy_operations import VacancyOperations
from src.vacancies.models import Vacancy

logger = logging.getLogger(__name__)


def get_user_input(prompt: str, required: bool = True) -> Optional[str]:
    """
    Получение ввода от пользователя с валидацией

    Args:
        prompt: Текст приглашения для ввода
        required: Обязательно ли поле для заполнения

    Returns:
        Введенная строка или None если поле не обязательное и пустое
    """
    while True:
        user_input = input(prompt).strip()

        if user_input or not required:
            return user_input if user_input else None

        print("Поле не может быть пустым!")


def get_positive_integer(prompt: str, default: Optional[int] = None) -> Optional[int]:
    """
    Получение положительного целого числа от пользователя

    Args:
        prompt: Текст приглашения для ввода
        default: Значение по умолчанию при пустом вводе

    Returns:
        Положительное целое число или None при ошибке
    """
    try:
        user_input = input(prompt).strip()

        # Если ввод пустой и есть значение по умолчанию
        if not user_input and default is not None:
            return default

        # Если ввод пустой и нет значения по умолчанию
        if not user_input:
            print("Введите корректное число!")
            return None

        value = int(user_input)
        if value <= 0:
            print("Число должно быть положительным!")
            return None
        return value
    except ValueError:
        print("Введите корректное число!")
        return None


def parse_salary_range(salary_range: str) -> Optional[tuple[int, int]]:
    """
    Парсинг диапазона зарплат из строки

    Args:
        salary_range: Строка с диапазоном зарплат (например: "100000 - 150000")

    Returns:
        Кортеж (min_salary, max_salary) или None при ошибке
    """
    try:
        # Парсим диапазон
        if " - " in salary_range:
            min_sal, max_sal = salary_range.split(" - ")
        elif "-" in salary_range:
            min_sal, max_sal = salary_range.split("-")
        else:
            print("Неверный формат диапазона. Используйте формат: 100000 - 150000")
            return None

        min_salary = int(min_sal.strip())
        max_salary = int(max_sal.strip())

        if min_salary > max_salary:
            min_salary, max_salary = max_salary, min_salary

        return min_salary, max_salary

    except ValueError:
        print("Введите корректные числа!")
        return None


def confirm_action(prompt: str) -> bool:
    """
    Получение подтверждения действия от пользователя

    Args:
        prompt: Текст приглашения для подтверждения

    Returns:
        True если пользователь подтвердил, False иначе
    """
    while True:
        answer = input(f"{prompt} (y/n): ").strip().lower()
        if answer in ["y", "yes", "д", "да"]:
            return True
        elif answer in ["n", "no", "н", "нет"]:
            return False
        else:
            print("Введите 'y' для да или 'n' для нет.")


def filter_vacancies_by_keyword(vacancies: List[Vacancy], keyword: str) -> List[Vacancy]:
    """
    Фильтрует вакансии по ключевому слову в названии или описании.
    Поддерживает логические операторы AND и OR.

    Args:
        vacancies: Список вакансий для фильтрации
        keyword: Ключевое слово или запрос для поиска (поддерживает "python AND call", "java OR kotlin")

    Returns:
        List[Vacancy]: Отфильтрованный список вакансий
    """
    if not keyword or not vacancies:
        return []

    # Парсим поисковый запрос на ключевые слова и оператор
    parsed_query = _parse_search_query(keyword)
    if not parsed_query:
        return []

    keywords = parsed_query["keywords"]
    operator = parsed_query["operator"]

    filtered_vacancies = []

    for vacancy in vacancies:
        # Формируем строку поиска из всех текстовых полей
        full_text = _build_searchable_text(vacancy)

        # Применяем логику поиска в зависимости от оператора
        if operator == "AND":
            # Все ключевые слова должны присутствовать
            if all(kw.lower() in full_text for kw in keywords):
                filtered_vacancies.append(vacancy)
        else:  # OR или одно слово
            # Достаточно любого ключевого слова
            if any(kw.lower() in full_text for kw in keywords):
                filtered_vacancies.append(vacancy)

    return filtered_vacancies


def _parse_search_query(query: str) -> dict:
    """
    Парсит поисковый запрос на ключевые слова и логический оператор

    Args:
        query: Поисковый запрос

    Returns:
        dict: {"keywords": [список_слов], "operator": "AND"/"OR"}
    """
    if not query or not query.strip():
        return None

    query = query.strip()

    # Проверяем наличие операторов (регистронезависимо)
    if " AND " in query.upper():
        keywords = [kw.strip() for kw in query.split(" AND ") if kw.strip()]
        return {"keywords": keywords, "operator": "AND"}
    elif " OR " in query.upper():
        keywords = [kw.strip() for kw in query.split(" OR ") if kw.strip()]
        return {"keywords": keywords, "operator": "OR"}
    elif "," in query:
        keywords = [kw.strip() for kw in query.split(",") if kw.strip()]
        return {"keywords": keywords, "operator": "OR"}
    else:
        # Одно слово или фраза
        return {"keywords": [query], "operator": "OR"}


def _build_searchable_text(vacancy: Vacancy) -> str:
    """
    Формирует единую строку поиска из всех текстовых полей вакансии

    Args:
        vacancy: Объект вакансии

    Returns:
        str: Объединенный текст для поиска в нижнем регистре
    """
    searchable_text = []

    # Проверяем названия
    if vacancy.title:
        searchable_text.append(str(vacancy.title))

    # Проверяем описание
    if vacancy.description:
        searchable_text.append(str(vacancy.description))

    # Проверяем требования
    if vacancy.requirements:
        searchable_text.append(str(vacancy.requirements))

    # Проверяем обязанности
    if vacancy.responsibilities:
        searchable_text.append(str(vacancy.responsibilities))

    # Удалена проверка detailed_description - поле не существует в новой модели

    # Проверяем тип занятости - безопасно преобразуем в строку
    if vacancy.employment:
        if hasattr(vacancy.employment, "__str__"):
            searchable_text.append(str(vacancy.employment))
        elif hasattr(vacancy.employment, "name"):
            searchable_text.append(str(vacancy.employment.name))

    # Проверяем навыки (если поле существует)
    if hasattr(vacancy, "skills") and vacancy.skills:
        for skill in vacancy.skills:
            if isinstance(skill, dict) and "name" in skill:
                searchable_text.append(str(skill["name"]))
            elif isinstance(skill, str):
                searchable_text.append(skill)
            else:
                searchable_text.append(str(skill))

    # Проверяем компанию
    if vacancy.employer:
        if hasattr(vacancy.employer, "name") and vacancy.employer.name:
            searchable_text.append(str(vacancy.employer.name))
        elif isinstance(vacancy.employer, dict) and "name" in vacancy.employer:
            searchable_text.append(str(vacancy.employer["name"]))
        else:
            searchable_text.append(str(vacancy.employer))

    # Объединяем весь текст и возвращаем в нижнем регистре
    return " ".join(searchable_text).lower()


# Эти функции перенесены в src/utils/vacancy_operations.py


def filter_vacancies_by_min_salary(vacancies: List[Vacancy], min_salary: int) -> List[Vacancy]:
    """Устаревшая функция - используйте VacancyOperations.filter_vacancies_by_min_salary"""
    return VacancyOperations.filter_vacancies_by_min_salary(vacancies, min_salary)


def filter_vacancies_by_max_salary(vacancies: List[Vacancy], max_salary: int) -> List[Vacancy]:
    """Устаревшая функция - используйте VacancyOperations.filter_vacancies_by_max_salary"""
    return VacancyOperations.filter_vacancies_by_max_salary(vacancies, max_salary)


def filter_vacancies_by_salary_range(vacancies: List[Vacancy], min_salary: int, max_salary: int) -> List[Vacancy]:
    """Устаревшая функция - используйте VacancyOperations.filter_vacancies_by_salary_range"""
    return VacancyOperations.filter_vacancies_by_salary_range(vacancies, min_salary, max_salary)


def get_vacancies_with_salary(vacancies: List[Vacancy]) -> List[Vacancy]:
    """Устаревшая функция - используйте VacancyOperations.get_vacancies_with_salary"""
    return VacancyOperations.get_vacancies_with_salary(vacancies)


def sort_vacancies_by_salary(vacancies: List[Vacancy], reverse: bool = True) -> List[Vacancy]:
    """Устаревшая функция - используйте VacancyOperations.sort_vacancies_by_salary"""
    return VacancyOperations.sort_vacancies_by_salary(vacancies, reverse)


def filter_vacancies_by_multiple_keywords(vacancies: List[Vacancy], keywords: List[str]) -> List[Vacancy]:
    """Устаревшая функция - используйте VacancyOperations.filter_vacancies_by_multiple_keywords"""
    return VacancyOperations.filter_vacancies_by_multiple_keywords(vacancies, keywords)


def search_vacancies_advanced(vacancies: List[Vacancy], query: str) -> List[Vacancy]:
    """Устаревшая функция - используйте VacancyOperations.search_vacancies_advanced"""
    return VacancyOperations.search_vacancies_advanced(vacancies, query)


def debug_vacancy_search(vacancy: Vacancy, keyword: str) -> None:
    """
    Отладочная функция для проверки содержимого вакансии при поиске

    Выводит подробную информацию о вакансии и показывает, в каких полях
    найдено искомое ключевое слово. Используется для отладки алгоритма поиска.

    Args:
        vacancy: Вакансия для отладки
        keyword: Ключевое слово для поиска
    """
    print(f"\n=== Отладка вакансии: {vacancy.title} ===")
    print(f"ID: {vacancy.id}")
    print(f"Заголовок: {vacancy.title}")
    print(f"Описание: {vacancy.description[:200] if vacancy.description else 'Нет'}...")
    print(f"Требования: {vacancy.requirements[:200] if vacancy.requirements else 'Нет'}...")
    print(f"Обязанности: {vacancy.responsibilities[:200] if vacancy.responsibilities else 'Нет'}...")
    # print(f"Ключевые слова: {vacancy.keywords}")
    print(f"Навыки: {vacancy.skills}")
    print(f"Работодатель: {vacancy.employer}")
    print(f"Опыт: {vacancy.experience}")
    print(f"Занятость: {vacancy.employment}")
    print(f"График: {vacancy.schedule}")
    print(f"Бонусы: {vacancy.benefits}")

    # Проверяем наличие ключевого слова
    keyword_lower = keyword.lower()
    found_in = []

    if vacancy.title and keyword_lower in vacancy.title.lower():
        found_in.append("заголовок")
    if vacancy.description and keyword_lower in vacancy.description.lower():
        found_in.append("описание")
    if vacancy.requirements and keyword_lower in vacancy.requirements.lower():
        found_in.append("требования")
    if vacancy.responsibilities and keyword_lower in vacancy.responsibilities.lower():
        found_in.append("обязанности")
    # if vacancy.keywords and any(keyword_lower in kw.lower() for kw in vacancy.keywords):
    #     found_in.append("ключевые слова")

    print(f"Ключевое слово '{keyword}' найдено в: {', '.join(found_in) if found_in else 'НИГДЕ'}")
    print("=" * 50)


def debug_search_vacancies(vacancies: List[Vacancy], keyword: str) -> None:
    """
    Отладочная функция для анализа всех сохраненных вакансий

    Выводит сводную информацию о поиске по всем вакансиям и показывает
    первые 5 вакансий с подробным анализом. Используется для отладки
    алгоритма поиска на больших наборах данных.

    Args:
        vacancies: Список вакансий для анализа
        keyword: Ключевое слово для поиска
    """
    print(f"\n=== Отладка поиска по слову '{keyword}' ===")
    print(f"Всего вакансий: {len(vacancies)}")

    for i, vacancy in enumerate(vacancies[:5]):  # Показываем первые 5
        print(f"\nВакансия {i+1}:")
        debug_vacancy_search(vacancy, keyword)


def display_vacancy_info(vacancy: "Vacancy", number: Optional[int] = None) -> None:
    """
    Отображение информации о вакансии

    Args:
        vacancy: Объект вакансии
        number: Порядковый номер (опционально)
    """
    vacancy_formatter.display_vacancy_info(vacancy, number)
