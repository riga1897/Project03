"""
Модуль совместимости для psycopg2/psycopg2-binary

Обеспечивает единый интерфейс для работы с PostgreSQL независимо от
установленного пакета: psycopg2-binary или psycopg2
"""

from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

# Попытка импорта psycopg2
psycopg2: Optional[Any] = None
PsycopgError: Optional[Any] = None
RealDictCursor: Optional[Any] = None

def _try_import_psycopg2() -> bool:
    """
    Попытка импорта psycopg2 или psycopg2-binary
    
    Returns:
        bool: True если импорт успешен, False иначе
    """
    global psycopg2, PsycopgError, RealDictCursor
    
    # Сначала пробуем psycopg2-binary (рекомендуется)
    try:
        import psycopg2 as _psycopg2
        from psycopg2 import Error as _PsycopgError
        from psycopg2.extras import RealDictCursor as _RealDictCursor
        
        psycopg2 = _psycopg2
        PsycopgError = _PsycopgError
        RealDictCursor = _RealDictCursor
        
        logger.debug("Успешно импортирован psycopg2 (или psycopg2-binary)")
        return True
        
    except ImportError as e:
        logger.error(f"Не удалось импортировать psycopg2: {e}")
        logger.error("Убедитесь что установлен psycopg2-binary или psycopg2:")
        logger.error("  pip install psycopg2-binary  # (рекомендуется)")
        logger.error("  или")  
        logger.error("  pip install psycopg2  # (требует PostgreSQL dev пакеты)")
        return False

# Выполняем импорт при загрузке модуля
_import_success = _try_import_psycopg2()

def get_psycopg2():
    """
    Возвращает модуль psycopg2
    
    Returns:
        psycopg2 модуль
        
    Raises:
        ImportError: Если psycopg2 не доступен
    """
    if not _import_success or psycopg2 is None:
        raise ImportError(
            "psycopg2 недоступен. Установите psycopg2-binary или psycopg2:\n"
            "  pip install psycopg2-binary  # (рекомендуется)\n"
            "  или\n" 
            "  pip install psycopg2  # (требует PostgreSQL dev пакеты)"
        )
    return psycopg2

def get_psycopg_error():
    """
    Возвращает класс ошибок psycopg2
    
    Returns:
        PsycopgError класс
        
    Raises:
        ImportError: Если psycopg2 не доступен
    """
    if not _import_success or PsycopgError is None:
        raise ImportError("psycopg2 недоступен")
    return PsycopgError

def get_real_dict_cursor():
    """
    Возвращает RealDictCursor класс
    
    Returns:
        RealDictCursor класс
        
    Raises:
        ImportError: Если psycopg2 не доступен
    """
    if not _import_success or RealDictCursor is None:
        raise ImportError("psycopg2 недоступен")
    return RealDictCursor

def is_available() -> bool:
    """
    Проверяет доступность psycopg2
    
    Returns:
        bool: True если psycopg2 доступен
    """
    return _import_success and psycopg2 is not None