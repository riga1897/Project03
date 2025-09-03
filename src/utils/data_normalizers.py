"""
Утилиты для унификации смешанных типов данных.
Устраняют проблемы с использованием словарей vs строк vs объектов.
"""
from typing import Any, Optional, Union, Dict


def normalize_area_data(area_data: Union[str, Dict[str, Any], None]) -> Optional[str]:
    """
    Унифицированная обработка данных области/местоположения.
    
    Args:
        area_data: Данные области - может быть строкой, словарем или None
        
    Returns:
        Optional[str]: Нормализованное название области или None
    """
    if not area_data:
        return None
        
    if isinstance(area_data, str):
        return area_data.strip() if area_data.strip() else None
        
    if isinstance(area_data, dict):
        # Приоритет: name > title > id > str(dict)
        name = area_data.get("name")
        if name:
            return str(name).strip()
            
        title = area_data.get("title")  
        if title:
            return str(title).strip()
            
        area_id = area_data.get("id")
        if area_id:
            return str(area_id).strip()
            
        # Если есть другие ключи, возвращаем строковое представление
        return str(area_data).strip() if str(area_data).strip() != '{}' else None
    
    # Для всех остальных типов
    return str(area_data).strip() if str(area_data).strip() else None


def normalize_experience_data(experience_data: Union[str, Dict[str, Any], None]) -> Optional[str]:
    """
    Унифицированная обработка данных опыта работы.
    
    Args:
        experience_data: Данные опыта - может быть строкой, словарем или None
        
    Returns:
        Optional[str]: Нормализованное описание опыта или None
    """
    if not experience_data:
        return None
        
    if isinstance(experience_data, str):
        return experience_data.strip() if experience_data.strip() else None
        
    if isinstance(experience_data, dict):
        # Приоритет: name > title > id > str(dict)
        name = experience_data.get("name")
        if name:
            return str(name).strip()
            
        title = experience_data.get("title")
        if title:
            return str(title).strip()
            
        exp_id = experience_data.get("id") 
        if exp_id:
            return str(exp_id).strip()
            
        # Если есть другие ключи, возвращаем строковое представление
        return str(experience_data).strip() if str(experience_data).strip() != '{}' else None
    
    # Для всех остальных типов
    return str(experience_data).strip() if str(experience_data).strip() else None


def normalize_employment_data(employment_data: Union[str, Dict[str, Any], None]) -> Optional[str]:
    """
    Унифицированная обработка данных типа занятости.
    
    Args:
        employment_data: Данные занятости - может быть строкой, словарем или None
        
    Returns:
        Optional[str]: Нормализованный тип занятости или None
    """
    if not employment_data:
        return None
        
    if isinstance(employment_data, str):
        return employment_data.strip() if employment_data.strip() else None
        
    if isinstance(employment_data, dict):
        # Приоритет: name > title > type > id > str(dict)
        name = employment_data.get("name")
        if name:
            return str(name).strip()
            
        title = employment_data.get("title")
        if title:
            return str(title).strip()
            
        emp_type = employment_data.get("type")
        if emp_type:
            return str(emp_type).strip()
            
        emp_id = employment_data.get("id")
        if emp_id:
            return str(emp_id).strip()
            
        # Если есть другие ключи, возвращаем строковое представление
        return str(employment_data).strip() if str(employment_data).strip() != '{}' else None
    
    # Для всех остальных типов  
    return str(employment_data).strip() if str(employment_data).strip() else None


def normalize_employer_data(employer_data: Union[str, Dict[str, Any], None]) -> Optional[str]:
    """
    Унифицированная обработка данных работодателя для строкового представления.
    
    Args:
        employer_data: Данные работодателя - может быть строкой, словарем или None
        
    Returns:
        Optional[str]: Нормализованное название работодателя или None
    """
    if not employer_data:
        return None
        
    if isinstance(employer_data, str):
        return employer_data.strip() if employer_data.strip() else None
        
    if isinstance(employer_data, dict):
        # Приоритет: name > title > firm_name > id > str(dict)
        name = employer_data.get("name")
        if name:
            return str(name).strip()
            
        title = employer_data.get("title")
        if title:
            return str(title).strip()
            
        firm_name = employer_data.get("firm_name")  # Для SuperJob
        if firm_name:
            return str(firm_name).strip()
            
        emp_id = employer_data.get("id")
        if emp_id:
            return str(emp_id).strip()
            
        # Если есть другие ключи, возвращаем строковое представление
        return str(employer_data).strip() if str(employer_data).strip() != '{}' else None
    
    # Для всех остальных типов
    return str(employer_data).strip() if str(employer_data).strip() else None