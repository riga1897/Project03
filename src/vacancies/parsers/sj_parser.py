import logging
from typing import Any, Dict, List

from ..models import Vacancy

logger = logging.getLogger(__name__)


class SuperJobParser:
    """Парсер для обработки данных вакансий SuperJob"""

    @staticmethod
    def parse_vacancies(vacancies_data: List[Dict[str, Any]]) -> List[Vacancy]:
        """
        Парсинг списка вакансий SuperJob

        Args:
            vacancies_data: Данные вакансий от API SuperJob

        Returns:
            List[SuperJobVacancy]: Список объектов вакансий
        """
        parsed_vacancies = []

        for vacancy_data in vacancies_data:
            try:
                # Устанавливаем источник если не установлен
                if "source" not in vacancy_data or not vacancy_data["source"]:
                    vacancy_data["source"] = "superjob.ru"
                
                vacancy = Vacancy.from_dict(vacancy_data)
                parsed_vacancies.append(vacancy)
            except ValueError as e:
                logger.warning(f"Пропуск вакансии SuperJob из-за ошибки валидации: {e}")
                continue
            except Exception as e:
                logger.error(f"Неожиданная ошибка при парсинге вакансии SuperJob: {e}")
                continue

        logger.info(f"Успешно распарсено {len(parsed_vacancies)} вакансий SuperJob из {len(vacancies_data)}")
        return parsed_vacancies

    @staticmethod
    def convert_to_unified_format(sj_vacancy: Vacancy) -> Dict[str, Any]:
        """
        Конвертация SuperJob вакансии в унифицированный формат

        Args:
            sj_vacancy: Объект вакансии SuperJob

        Returns:
            Dict[str, Any]: Унифицированный словарь вакансии
        """
        # Обрабатываем зарплату для корректного отображения
        salary_dict = None
        if sj_vacancy.salary:
            salary_dict = sj_vacancy.salary.to_dict()
            # Исправляем период для SuperJob
            if salary_dict and "period" in salary_dict:
                if salary_dict["period"] in ["месяц", "month"]:
                    salary_dict["period"] = "месяц"

        return {
            "id": sj_vacancy.vacancy_id,
            "name": sj_vacancy.title,
            "title": sj_vacancy.title,
            "url": sj_vacancy.url,
            "alternate_url": sj_vacancy.url,
            "salary": salary_dict,
            "description": sj_vacancy.description,
            # Для SJ: обязанности = vacancyRichText (description), требования = candidat (requirements)
            "requirements": sj_vacancy.requirements,  # candidat
            "responsibilities": sj_vacancy.description,  # vacancyRichText
            "employer": sj_vacancy.employer,
            "experience": sj_vacancy.experience,
            "employment": sj_vacancy.employment,
            "schedule": sj_vacancy.schedule,
            "published_at": sj_vacancy.published_at.isoformat() if sj_vacancy.published_at else None,
            "skills": [],
            "keywords": [],
            "detailed_description": sj_vacancy.detailed_description,
            "benefits": sj_vacancy.benefits,
            "source": sj_vacancy.source or "superjob.ru",
        }

    @staticmethod
    def parse_vacancy(vacancy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Парсинг одной вакансии SJ в словарь

        Args:
            vacancy_data: Данные вакансии от API SJ

        Returns:
            Dict[str, Any]: Словарь с данными вакансии
        """
        try:
            town_info = vacancy_data.get('town', {})
            experience_info = vacancy_data.get('experience', {})
            type_of_work_info = vacancy_data.get('type_of_work', {})
            place_of_work_info = vacancy_data.get('place_of_work', {})

            return {
                'vacancy_id': str(vacancy_data.get('id', '')),
                'title': vacancy_data.get('profession', ''),
                'url': vacancy_data.get('link', ''),
                'salary_from': vacancy_data.get('payment_from'),
                'salary_to': vacancy_data.get('payment_to'),
                'salary_currency': vacancy_data.get('currency'),
                'requirements': vacancy_data.get('candidat', ''),
                'responsibilities': vacancy_data.get('work', ''),
                'employer': vacancy_data.get('firm_name', ''),
                'area': town_info.get('title', '') if town_info else '',
                'experience': experience_info.get('title', '') if experience_info else '',
                'employment': type_of_work_info.get('title', '') if type_of_work_info else '',
                'schedule': place_of_work_info.get('title', '') if place_of_work_info else '',
                'published_at': vacancy_data.get('date_pub_timestamp', ''),
            }
        except Exception as e:
            logger.error(f"Ошибка при парсинге вакансии SJ: {e}")
            return {
                'vacancy_id': str(vacancy_data.get('id', '')),
                'title': vacancy_data.get('profession', ''),
                'url': '',
                'salary_from': None,
                'salary_to': None,
                'salary_currency': None,
                'requirements': '',
                'responsibilities': '',
                'employer': '',
                'area': '',
                'experience': '',
                'employment': '',
                'schedule': '',
                'published_at': '',
            }

    @staticmethod
    def parse_companies(companies_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Парсинг списка компаний SJ

        Args:
            companies_data: Данные компаний от API SJ

        Returns:
            List[Dict[str, Any]]: Список словарей с данными компаний
        """
        try:
            companies = []
            objects = companies_data.get('objects', [])
            
            for company_data in objects:
                company = {
                    'company_id': str(company_data.get('id', '')),
                    'name': company_data.get('title', ''),
                    'description': company_data.get('description', ''),
                    'url': company_data.get('link', ''),
                }
                companies.append(company)
                
            logger.info(f"Успешно распарсено {len(companies)} компаний SJ")
            return companies
        except Exception as e:
            logger.error(f"Ошибка при парсинге списка компаний SJ: {e}")
            return []
