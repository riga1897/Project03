
"""
Модуль для сбора и отображения статистики по вакансиям
"""

import logging
from typing import List, Dict, Any
from collections import defaultdict

# Настраиваем логирование на DEBUG уровень для этого модуля
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class VacancyStats:
    """Класс для сбора и отображения статистики по вакансиям"""

    @staticmethod
    def get_company_distribution(vacancies: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Получить распределение вакансий по компаниям
        
        Args:
            vacancies: Список вакансий
            
        Returns:
            Dict[str, int]: Словарь с компаниями и количеством вакансий
        """
        company_stats = defaultdict(int)
        
        for i, vacancy in enumerate(vacancies):
            # Получаем название компании из разных источников
            company_name = VacancyStats._extract_company_name(vacancy)
            
            # Отладочная информация для первых нескольких вакансий
            if i < 5:
                logger.debug(f"Vacancy {i}: type={type(vacancy)}")
                if isinstance(vacancy, dict):
                    logger.debug(f"  Keys: {list(vacancy.keys())}")
                    if "employer" in vacancy:
                        logger.debug(f"  Employer: {vacancy['employer']}")
                    if "raw_data" in vacancy:
                        logger.debug(f"  Raw data keys: {list(vacancy['raw_data'].keys()) if isinstance(vacancy['raw_data'], dict) else 'not dict'}")
                        if isinstance(vacancy['raw_data'], dict) and "employer" in vacancy['raw_data']:
                            logger.debug(f"  Raw data employer: {vacancy['raw_data']['employer']}")
                else:
                    logger.debug(f"  Has employer attr: {hasattr(vacancy, 'employer')}")
                    if hasattr(vacancy, 'employer'):
                        logger.debug(f"  Employer: {vacancy.employer}")
                    logger.debug(f"  Has raw_data attr: {hasattr(vacancy, 'raw_data')}")
                    if hasattr(vacancy, 'raw_data'):
                        logger.debug(f"  Raw data: {vacancy.raw_data}")
                logger.debug(f"  Extracted company: {company_name}")
            
            if company_name:
                company_stats[company_name] += 1
                
        return dict(company_stats)
    
    @staticmethod
    def _extract_company_name(vacancy: Dict[str, Any]) -> str:
        """
        Извлечь название компании из данных вакансии
        
        Args:
            vacancy: Данные вакансии
            
        Returns:
            str: Название компании или "Неизвестная компания"
        """
        # ПРИОРИТЕТ 1: Проверяем raw_data.employer (основной источник для HH)
        if hasattr(vacancy, 'raw_data') and vacancy.raw_data:
            raw_data = vacancy.raw_data
            if isinstance(raw_data, dict) and "employer" in raw_data:
                employer = raw_data["employer"]
                if isinstance(employer, dict) and "name" in employer:
                    return employer["name"]
                elif isinstance(employer, str):
                    return employer
        
        # ПРИОРИТЕТ 2: Проверяем объект Vacancy.employer
        if hasattr(vacancy, 'employer'):
            employer = vacancy.employer
            if isinstance(employer, dict):
                return employer.get("name", "Неизвестная компания")
            elif isinstance(employer, str):
                return employer
            elif employer:
                return str(employer)
        
        # ПРИОРИТЕТ 3: Для словарей - HeadHunter прямой доступ
        if isinstance(vacancy, dict) and "employer" in vacancy:
            employer = vacancy["employer"]
            if isinstance(employer, dict) and "name" in employer:
                return employer["name"]
            elif isinstance(employer, str):
                return employer
        
        # ПРИОРИТЕТ 4: Дополнительная проверка для raw_data как словарь
        if isinstance(vacancy, dict) and "raw_data" in vacancy:
            raw_data = vacancy["raw_data"]
            if isinstance(raw_data, dict) and "employer" in raw_data:
                employer = raw_data["employer"]
                if isinstance(employer, dict) and "name" in employer:
                    return employer["name"]
                elif isinstance(employer, str):
                    return employer
        
        # ПРИОРИТЕТ 5: Проверяем атрибут _employer_name (стандартизированное название из БД)
        if hasattr(vacancy, '_employer_name') and vacancy._employer_name:
            return vacancy._employer_name
            
        # ПРИОРИТЕТ 6: Для словарей - SuperJob
        if isinstance(vacancy, dict) and "firm_name" in vacancy:
            return vacancy.get("firm_name", "Неизвестная компания")
        
        # ПРИОРИТЕТ 7: Проверяем прямые поля HH в случае если это сырые данные
        if isinstance(vacancy, dict):
            # Проверяем возможные варианты полей компании в HH
            for field in ["company_name", "company", "employer_name"]:
                if field in vacancy and vacancy[field]:
                    company = vacancy[field]
                    if isinstance(company, dict):
                        return company.get("name", str(company))
                    return str(company)
                
        return "Неизвестная компания"
    
    @staticmethod
    def display_company_stats(vacancies: List[Dict[str, Any]], source_name: str = ""):
        """
        Отобразить статистику по компаниям
        
        Args:
            vacancies: Список вакансий
            source_name: Название источника для заголовка
        """
        if not vacancies:
            print("Нет вакансий для отображения статистики")
            return
            
        company_stats = VacancyStats.get_company_distribution(vacancies)
        
        if not company_stats:
            print("Не удалось извлечь информацию о компаниях")
            return
            
        VacancyStats._display_company_distribution(company_stats, len(vacancies), source_name)
    
    @staticmethod
    def _display_company_distribution(company_stats: Dict[str, int], total_vacancies: int, source_name: str = ""):
        """
        Отобразить распределение компаний
        
        Args:
            company_stats: Словарь с распределением компаний
            total_vacancies: Общее количество вакансий
            source_name: Название источника для заголовка
        """
        print(f"\n📊 Распределение вакансий по компаниям{' (' + source_name + ')' if source_name else ''}:")
        print(f"Всего найдено {total_vacancies} вакансий от {len(company_stats)} компаний")
        print("-" * 60)
        
        # Сортируем по количеству вакансий (убывание)
        sorted_companies = sorted(company_stats.items(), key=lambda x: x[1], reverse=True)
        
        for company, count in sorted_companies:
            percentage = (count / total_vacancies) * 100
            print(f"  {company}: {count} вакансий ({percentage:.1f}%)")
        
        print("-" * 60)
    
    @staticmethod
    def display_source_stats(hh_vacancies: List[Dict[str, Any]], sj_vacancies: List[Dict[str, Any]]):
        """
        Отобразить статистику по каждому источнику отдельно
        
        Args:
            hh_vacancies: Вакансии с HH.ru
            sj_vacancies: Вакансии с SuperJob
        """
        total_hh = len(hh_vacancies)
        total_sj = len(sj_vacancies)
        total_all = total_hh + total_sj
        
        if total_all == 0:
            print("Нет вакансий для отображения статистики")
            return
        
        print(f"\n📊 Итого найдено: {total_all} вакансий")
        print(f"HH.ru: {total_hh} вакансий")
        print(f"SuperJob: {total_sj} вакансий")
        
        # Показываем статистику по каждому источнику отдельно
        if hh_vacancies:
            VacancyStats.display_company_stats(hh_vacancies, "HH.ru")
            
        if sj_vacancies:
            VacancyStats.display_company_stats(sj_vacancies, "SuperJob")
