"""Утилиты для поиска и фильтрации вакансий.

Этот модуль предоставляет набор функций для обработки поисковых запросов,
фильтрации вакансий по различным критериям и нормализации данных для поиска.

Functions:
    normalize_query: Нормализация поискового запроса
    extract_keywords: Извлечение ключевых слов из запроса  
    build_search_params: Построение параметров для API поиска
    filter_vacancies_by_keywords: Фильтрация вакансий по ключевым словам
    filter_vacancies_by_salary: Фильтрация по зарплате
    filter_vacancies_by_company: Фильтрация по компании
    search_vacancies_in_database: Поиск в базе данных
"""

import logging
import re
from typing import Any, Dict, List, Optional

from src.vacancies.models import Vacancy

logger = logging.getLogger(__name__)


def normalize_query(query: str) -> str:
    """Нормализует поисковый запрос для унифицированного поиска.

    Приводит запрос к нижнему регистру, убирает лишние пробелы,
    ограничивает длину и подготавливает для дальнейшей обработки.

    Args:
        query: Исходный поисковый запрос.

    Returns:
        Нормализованный запрос в нижнем регистре.
    """
    if not query:
        return ""

    # Приводим к нижнему регистру и убираем лишние пробелы
    normalized = str(query).lower().strip()

    # Убираем множественные пробелы
    normalized = re.sub(r"\s+", " ", normalized)

    # Ограничиваем длину запроса
    if len(normalized) > 500:
        normalized = normalized[:500]

    return normalized


def extract_keywords(query: str) -> List[str]:
    """
    Извлечение ключевых слов из поискового запроса

    Args:
        query: Поисковый запрос

    Returns:
        Список ключевых слов
    """
    if not query:
        return []

    # Нормализуем запрос
    normalized = normalize_query(query)

    # Удаляем операторы AND, OR и знаки препинания
    cleaned = re.sub(r"\b(and|or)\b", " ", normalized)
    cleaned = re.sub(r"[^\w\s\.\+\#]", " ", cleaned)

    # Разбиваем на слова
    words = cleaned.split()

    # Фильтруем короткие слова и стоп-слова
    stop_words = {"и", "в", "на", "с", "по", "для", "от", "до", "работа", "вакансия"}
    keywords = [word for word in words if len(word) > 1 and word not in stop_words]

    return keywords


def build_search_params(query: str, per_page: int = 50, page: int = 0, **kwargs) -> Dict[str, Any]:
    """
    Построение параметров поиска

    Args:
        query: Поисковый запрос
        per_page: Количество вакансий на странице
        page: Номер страницы
        **kwargs: Дополнительные параметры

    Returns:
        Словарь параметров поиска
    """
    # Ограничиваем per_page
    if per_page > 100:
        per_page = 100

    params = {"text": query, "per_page": per_page, "page": page}

    # Добавляем дополнительные параметры
    if "salary_from" in kwargs:
        params["salary"] = kwargs["salary_from"]

    if "salary_to" in kwargs:
        params["salary_to"] = kwargs["salary_to"]

    if "area" in kwargs:
        params["area"] = kwargs["area"]

    if "experience" in kwargs:
        params["experience"] = kwargs["experience"]

    if "schedule" in kwargs:
        params["schedule"] = kwargs["schedule"]

    return params


def validate_search_query(query: str) -> bool:
    """
    Валидация поискового запроса

    Args:
        query: Поисковый запрос для проверки

    Returns:
        True если запрос валиден, False иначе
    """
    if not query:
        return False

    if not isinstance(query, str):
        return False

    # Проверяем что после очистки остался хотя бы один символ
    cleaned = query.strip()
    return len(cleaned) > 0


def format_search_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Форматирование результатов поиска

    Args:
        results: Список результатов поиска

    Returns:
        Отформатированный список результатов
    """
    if not results:
        return []

    formatted_results = []

    for result in results:
        if not isinstance(result, dict):
            continue

        formatted_result = {
            "id": result.get("id") or result.get("vacancy_id", ""),
            "title": result.get("name") or result.get("profession") or result.get("title", ""),
            "source": result.get("source", "unknown"),
            "url": result.get("alternate_url") or result.get("link") or result.get("url", ""),
        }

        formatted_results.append(formatted_result)

    return formatted_results


def filter_vacancies_by_keyword(vacancies: List[Vacancy], keyword: str) -> List[Vacancy]:
    """
    Расширенная фильтрация вакансий по ключевому слову

    Args:
        vacancies: Список вакансий для фильтрации
        keyword: Ключевое слово для поиска

    Returns:
        Список отфильтрованных вакансий с оценкой релевантности
    """
    filtered_vacancies = []
    keyword_lower = keyword.lower()

    for vacancy in vacancies:
        relevance_score = 0

        # Проверяем по ID вакансии (очень высокий приоритет)
        if vacancy.id and keyword_lower in vacancy.id.lower():
            relevance_score += 15

        # Проверяем в заголовке (высокий приоритет)
        if vacancy.title and keyword_lower in vacancy.title.lower():
            relevance_score += 10

        # Проверяем в требованиях (средний приоритет)
        if vacancy.requirements and keyword_lower in vacancy.requirements.lower():
            relevance_score += 5

        # Проверяем в обязанностях (средний приоритет)
        if vacancy.responsibilities and keyword_lower in vacancy.responsibilities.lower():
            relevance_score += 5

        # Проверяем в описании (низкий приоритет)
        if vacancy.description and keyword_lower in vacancy.description.lower():
            relevance_score += 3

        # Дополнительная проверка в описании (используем основное поле description)
        # Удалена проверка detailed_description - поле не существует в новой модели

        # Проверяем в навыках (если поле существует)
        if hasattr(vacancy, 'skills') and vacancy.skills:
            try:
                for skill in vacancy.skills:
                    if isinstance(skill, dict) and "name" in skill:
                        if keyword_lower in skill["name"].lower():
                            relevance_score += 6
                    elif isinstance(skill, str) and keyword_lower in skill.lower():
                        relevance_score += 6
            except (AttributeError, TypeError):
                pass  # Поле skills отсутствует или имеет неожиданный тип

        # Дополнительные проверки для улучшения поиска.
        # Проверяем в информации о работодателе.
        if vacancy.employer:
            if isinstance(vacancy.employer, dict):
                employer_name = vacancy.employer.get("name", "")
                if employer_name and keyword_lower in employer_name.lower():
                    relevance_score += 4
            elif hasattr(vacancy.employer, "name"):
                if keyword_lower in vacancy.employer.name.lower():
                    relevance_score += 4

        # Проверяем в типе занятости (объект Pydantic)
        if vacancy.employment:
            if hasattr(vacancy.employment, "name") and keyword_lower in vacancy.employment.name.lower():
                relevance_score += 3
            elif isinstance(vacancy.employment, str) and keyword_lower in vacancy.employment.lower():
                relevance_score += 3

        # Проверяем в графике работы (объект Pydantic)
        if vacancy.schedule:
            if hasattr(vacancy.schedule, "name") and keyword_lower in vacancy.schedule.name.lower():
                relevance_score += 3
            elif isinstance(vacancy.schedule, str) and keyword_lower in vacancy.schedule.lower():
                relevance_score += 3

        # Проверяем в опыте работы (объект Pydantic)
        if vacancy.experience:
            if hasattr(vacancy.experience, "name") and keyword_lower in vacancy.experience.name.lower():
                relevance_score += 3
            elif isinstance(vacancy.experience, str) and keyword_lower in vacancy.experience.lower():
                relevance_score += 3

        # Проверяем в бонусах/льготах (если поле существует)
        if hasattr(vacancy, 'benefits') and vacancy.benefits:
            try:
                if keyword_lower in str(vacancy.benefits).lower():
                    relevance_score += 2
            except (AttributeError, TypeError):
                pass  # Поле benefits отсутствует или имеет неожиданный тип

        if relevance_score > 0:
            # Добавляем временный атрибут для сортировки (безопасно)
            try:
                vacancy._relevance_score = relevance_score  # type: ignore
            except AttributeError:
                # Если не можем установить атрибут, используем другой способ
                pass
            filtered_vacancies.append(vacancy)

    # Сортируем по релевантности
    filtered_vacancies.sort(key=lambda x: getattr(x, "_relevance_score", 0), reverse=True)

    return filtered_vacancies


def vacancy_contains_keyword(vacancy: Vacancy, keyword: str) -> bool:
    """
    Проверяет, содержит ли вакансия указанное ключевое слово

    Args:
        vacancy: Вакансия для проверки
        keyword: Ключевое слово для поиска

    Returns:
        bool: True, если ключевое слово найдено
    """
    keyword_lower = keyword.lower()

    # Проверяем в заголовке
    if vacancy.title and keyword_lower in vacancy.title.lower():
        return True

    # Проверяем в требованиях
    if vacancy.requirements and keyword_lower in vacancy.requirements.lower():
        return True

    # Проверяем в обязанностях
    if vacancy.responsibilities and keyword_lower in vacancy.responsibilities.lower():
        return True

    # Проверяем в описании
    if vacancy.description and keyword_lower in vacancy.description.lower():
        return True

    # Удалена проверка detailed_description - поле не существует в новой модели

    # Дополнительная проверка для SuperJob - проверяем все текстовые поля
    if hasattr(vacancy, "profession") and vacancy.profession:
        try:
            if keyword_lower in str(vacancy.profession).lower():
                return True
        except (AttributeError, TypeError):
            pass  # Поле profession отсутствует или имеет неожиданный тип

    # Проверяем в навыках (если поле существует)
    if hasattr(vacancy, 'skills') and vacancy.skills:
        try:
            for skill in vacancy.skills:
                if isinstance(skill, dict) and "name" in skill:
                    if keyword_lower in skill["name"].lower():
                        return True
                elif isinstance(skill, str) and keyword_lower in skill.lower():
                    return True
        except (AttributeError, TypeError):
            pass  # Поле skills отсутствует или имеет неожиданный тип

    return False


class SearchQueryParser:
    """Класс для парсинга сложных поисковых запросов.
    
    Обрабатывает поисковые запросы с операторами AND, OR, кавычками
    и другими специальными конструкциями для улучшения точности поиска.
    """

    def __init__(self) -> None:
        """Инициализация парсера запросов."""
        pass

    def parse(self, query: str) -> Dict[str, Any]:
        """Парсинг поискового запроса"""
        if not query or not query.strip():
            return None

        query = query.strip()

        if " AND " in query.upper():
            keywords = [kw.strip() for kw in query.upper().split(" AND ")]
            return {"keywords": keywords, "operator": "AND"}
        elif " OR " in query.upper():
            keywords = [kw.strip() for kw in query.upper().split(" OR ")]
            return {"keywords": keywords, "operator": "OR"}
        elif "," in query:
            keywords = [kw.strip() for kw in query.split(",")]
            return {"keywords": keywords, "operator": "OR"}
        else:
            return {"keywords": [query], "operator": "OR"}


class AdvancedSearch:
    """Класс для продвинутого поиска"""

    def __init__(self):
        """Инициализация продвинутого поиска"""
        pass

    def search_with_and(self, vacancies, keywords):
        """Поиск с оператором AND - ищет во всех текстовых полях включая search_query"""
        result = []
        for vacancy in vacancies:
            # Включаем search_query в поиск если это объект из базы данных
            search_query = ""
            if hasattr(vacancy, "search_query") and vacancy.search_query:
                search_query = vacancy.search_query

            search_text = f"{vacancy.title} {vacancy.description or ''} {search_query}".lower()
            if all(keyword.lower() in search_text for keyword in keywords):
                result.append(vacancy)
        return result

    def search_with_or(self, vacancies, keywords):
        """Поиск с оператором OR - ищет во всех текстовых полях включая search_query"""
        result = []
        for vacancy in vacancies:
            # Включаем search_query в поиск если это объект из базы данных
            search_query = ""
            if hasattr(vacancy, "search_query") and vacancy.search_query:
                search_query = vacancy.search_query

            search_text = f"{vacancy.title} {vacancy.description or ''} {search_query}".lower()
            if any(keyword.lower() in search_text for keyword in keywords):
                result.append(vacancy)
        return result
