"""
Парсер для извлечения структурированных данных из поля description.
Извлекает требования и обязанности из HTML и текстового контента.
"""

import logging
import re
from html import unescape
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class DescriptionParser:
    """Парсер для извлечения требований и обязанностей из описаний вакансий"""

    # Паттерны для поиска разделов
    REQUIREMENTS_PATTERNS = [
        r"<p[^>]*><strong[^>]*>Требования[^<]*</strong[^>]*></p[^>]*>(.+?)(?=<p[^>]*><strong[^>]*>|$)",
        r"<p[^>]*><b[^>]*>Требования[^<]*</b[^>]*></p[^>]*>(.+?)(?=<p[^>]*><b[^>]*>|$)",
        r"<strong[^>]*>Требования[^<]*</strong[^>]*>(.+?)(?=<strong[^>]*>|$)",
        r"<b[^>]*>Требования[^<]*</b[^>]*>(.+?)(?=<b[^>]*>|$)",
        r"Требования:(.+?)(?=\n[А-ЯA-Z][а-яa-z]+:|$)",
        r"ТРЕБОВАНИЯ:(.+?)(?=\n[А-ЯA-Z][а-яa-z]+:|$)",
    ]

    RESPONSIBILITIES_PATTERNS = [
        r"<p[^>]*><strong[^>]*>Обязанности[^<]*</strong[^>]*></p[^>]*>(.+?)(?=<p[^>]*><strong[^>]*>|$)",
        r"<p[^>]*><b[^>]*>Обязанности[^<]*</b[^>]*></p[^>]*>(.+?)(?=<p[^>]*><b[^>]*>|$)",
        r"<strong[^>]*>Обязанности[^<]*</strong[^>]*>(.+?)(?=<strong[^>]*>|$)",
        r"<b[^>]*>Обязанности[^<]*</b[^>]*>(.+?)(?=<b[^>]*>|$)",
        r"Обязанности:(.+?)(?=\n[А-ЯA-Z][а-яa-z]+:|$)",
        r"ОБЯЗАННОСТИ:(.+?)(?=\n[А-ЯA-Z][а-яa-z]+:|$)",
        r"Задачи:(.+?)(?=\n[А-ЯA-Z][а-яa-z]+:|$)",
        r"ЗАДАЧИ:(.+?)(?=\n[А-ЯA-Z][а-яa-z]+:|$)",
    ]

    @staticmethod
    def clean_html(html_text: str) -> str:
        """Очистка HTML тегов и декодирование сущностей"""
        if not html_text:
            return ""

        # Декодирование HTML сущностей
        text = unescape(html_text)

        # Замена списков на простые элементы
        text = re.sub(r"<li[^>]*>", "• ", text)
        text = re.sub(r"</li>", "\n", text)
        text = re.sub(r"<ul[^>]*>|</ul>", "", text)
        text = re.sub(r"<ol[^>]*>|</ol>", "", text)

        # Замена параграфов на переносы строк
        text = re.sub(r"<p[^>]*>", "", text)
        text = re.sub(r"</p>", "\n", text)

        # Удаление всех остальных HTML тегов
        text = re.sub(r"<[^>]+>", "", text)

        # Очистка множественных пробелов и переносов
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\n+", "\n", text)

        return text.strip()

    @classmethod
    def extract_requirements_and_responsibilities(cls, description: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Извлекает требования и обязанности из описания вакансии

        Args:
            description: Полное описание вакансии (может содержать HTML)

        Returns:
            Tuple[Optional[str], Optional[str]]: (requirements, responsibilities)
        """
        if not description:
            return None, None

        requirements = None
        responsibilities = None

        try:
            # Поиск требований
            for pattern in cls.REQUIREMENTS_PATTERNS:
                match = re.search(pattern, description, re.IGNORECASE | re.DOTALL)
                if match:
                    requirements = cls.clean_html(match.group(1)).strip()
                    if requirements and len(requirements) > 10:  # Минимальная длина
                        break

            # Поиск обязанностей
            for pattern in cls.RESPONSIBILITIES_PATTERNS:
                match = re.search(pattern, description, re.IGNORECASE | re.DOTALL)
                if match:
                    responsibilities = cls.clean_html(match.group(1)).strip()
                    if responsibilities and len(responsibilities) > 10:  # Минимальная длина
                        break

        except Exception as e:
            logger.warning(f"Ошибка парсинга описания: {e}")

        return requirements, responsibilities

    @classmethod
    def parse_vacancy_description(cls, vacancy_data: dict) -> dict:
        """
        Обрабатывает данные вакансии и извлекает структурированную информацию

        Args:
            vacancy_data: Словарь с данными вакансии

        Returns:
            dict: Обновленные данные с заполненными requirements и responsibilities
        """
        description = vacancy_data.get("description", "")

        # Если поля уже заполнены и не пустые, не перезаписываем
        has_requirements = vacancy_data.get("requirements", "").strip()
        has_responsibilities = vacancy_data.get("responsibilities", "").strip()

        if has_requirements and has_responsibilities:
            return vacancy_data

        # Извлекаем из description если поля пустые
        extracted_req, extracted_resp = cls.extract_requirements_and_responsibilities(description)

        # Заполняем только пустые поля
        if not has_requirements and extracted_req:
            vacancy_data["requirements"] = extracted_req

        if not has_responsibilities and extracted_resp:
            vacancy_data["responsibilities"] = extracted_resp

        return vacancy_data


# Примеры тестирования парсера
if __name__ == "__main__":
    # Тестовые данные в формате HH.ru
    test_description_hh = """
    <p><strong>Обязанности:</strong></p>
    <ul>
    <li>Разработка и поддержка веб-приложений на Python/Django</li>
    <li>Участие в проектировании архитектуры системы</li>
    <li>Код-ревью и менторинг младших разработчиков</li>
    </ul>
    <p><strong>Требования:</strong></p>
    <ul>
    <li>Python 3.8+, Django 3.2+</li>
    <li>Опыт работы с PostgreSQL, Redis</li>
    <li>Знание Git, Docker</li>
    </ul>
    """

    # Тестовые данные в текстовом формате
    test_description_text = """
    Обязанности:
    - Разработка микросервисов на FastAPI
    - Интеграция с внешними API
    
    Требования:
    - Python, FastAPI, SQLAlchemy
    - Опыт работы от 3 лет
    """

    parser = DescriptionParser()

    print("=== ТЕСТ HH.ru HTML формата ===")
    req1, resp1 = parser.extract_requirements_and_responsibilities(test_description_hh)
    print("Требования:", req1)
    print("Обязанности:", resp1)

    print("\n=== ТЕСТ текстового формата ===")
    req2, resp2 = parser.extract_requirements_and_responsibilities(test_description_text)
    print("Требования:", req2)
    print("Обязанности:", resp2)
