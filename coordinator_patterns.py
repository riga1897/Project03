"""
Паттерны организации центрального координатора в Python

Центральный координатор (Coordinator/Mediator) - это паттерн проектирования,
который инкапсулирует логику взаимодействия между множественными компонентами,
обеспечивая слабую связанность и централизованное управление потоками данных.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol, Type, TypeVar
from dataclasses import dataclass
from enum import Enum
import logging
import asyncio
from contextlib import asynccontextmanager

# ================================
# 1. БАЗОВЫЕ ИНТЕРФЕЙСЫ
# ================================

class CoordinatorEvent(Enum):
    """Типы событий для координатора"""
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class CoordinationResult:
    """Результат координации операций"""
    success: bool
    data: Any = None
    errors: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.metadata is None:
            self.metadata = {}

class CoordinatorProtocol(Protocol):
    """Протокол для всех координаторов"""
    
    async def coordinate(self, *args, **kwargs) -> CoordinationResult:
        """Основной метод координации"""
        ...
    
    def register_handler(self, event: CoordinatorEvent, handler: callable) -> None:
        """Регистрация обработчика событий"""
        ...

# ================================
# 2. БАЗОВЫЙ КООРДИНАТОР
# ================================

class BaseCoordinator(ABC):
    """Базовый абстрактный координатор"""
    
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._event_handlers: Dict[CoordinatorEvent, List[callable]] = {
            event: [] for event in CoordinatorEvent
        }
        self._middlewares: List[callable] = []
        self._context: Dict[str, Any] = {}
    
    def register_handler(self, event: CoordinatorEvent, handler: callable) -> None:
        """Регистрирует обработчик для конкретного события"""
        self._event_handlers[event].append(handler)
    
    def add_middleware(self, middleware: callable) -> None:
        """Добавляет middleware для обработки запросов"""
        self._middlewares.append(middleware)
    
    async def _emit_event(self, event: CoordinatorEvent, data: Any = None) -> None:
        """Вызывает все обработчики для конкретного события"""
        for handler in self._event_handlers[event]:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event, data)
                else:
                    handler(event, data)
            except Exception as e:
                self._logger.error(f"Error in event handler: {e}")
    
    async def _apply_middlewares(self, request: Any) -> Any:
        """Применяет middleware к запросу"""
        result = request
        for middleware in self._middlewares:
            if asyncio.iscoroutinefunction(middleware):
                result = await middleware(result)
            else:
                result = middleware(result)
        return result
    
    @abstractmethod
    async def coordinate(self, *args, **kwargs) -> CoordinationResult:
        """Основной метод координации - должен быть реализован в наследниках"""
        pass
    
    def set_context(self, key: str, value: Any) -> None:
        """Устанавливает контекстное значение"""
        self._context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Получает контекстное значение"""
        return self._context.get(key, default)

# ================================
# 3. КОНКРЕТНАЯ РЕАЛИЗАЦИЯ
# ================================

class ServiceCoordinator(BaseCoordinator):
    """Координатор для работы с множественными сервисами"""
    
    def __init__(self):
        super().__init__()
        self._services: Dict[str, Any] = {}
        self._service_dependencies: Dict[str, List[str]] = {}
    
    def register_service(self, name: str, service: Any, dependencies: List[str] = None) -> None:
        """Регистрирует сервис с его зависимостями"""
        self._services[name] = service
        self._service_dependencies[name] = dependencies or []
        self._logger.info(f"Registered service: {name}")
    
    def _resolve_execution_order(self) -> List[str]:
        """Определяет порядок выполнения сервисов на основе зависимостей"""
        resolved = []
        remaining = set(self._services.keys())
        
        while remaining:
            # Находим сервисы без нерешенных зависимостей
            ready = [
                service for service in remaining
                if all(dep in resolved for dep in self._service_dependencies[service])
            ]
            
            if not ready:
                raise ValueError(f"Circular dependency detected in services: {remaining}")
            
            resolved.extend(ready)
            remaining -= set(ready)
        
        return resolved
    
    async def coordinate(self, operation: str, *args, **kwargs) -> CoordinationResult:
        """Координирует выполнение операции across всех сервисов"""
        
        await self._emit_event(CoordinatorEvent.STARTED, operation)
        
        try:
            # Применяем middleware
            processed_args = await self._apply_middlewares((args, kwargs))
            args, kwargs = processed_args if isinstance(processed_args, tuple) else (args, kwargs)
            
            # Определяем порядок выполнения
            execution_order = self._resolve_execution_order()
            
            results = {}
            errors = []
            
            # Выполняем операцию для каждого сервиса
            for service_name in execution_order:
                service = self._services[service_name]
                
                try:
                    self._logger.debug(f"Executing {operation} on {service_name}")
                    
                    # Проверяем, есть ли у сервиса нужный метод
                    if hasattr(service, operation):
                        method = getattr(service, operation)
                        
                        # Выполняем асинхронно или синхронно
                        if asyncio.iscoroutinefunction(method):
                            result = await method(*args, **kwargs)
                        else:
                            result = method(*args, **kwargs)
                        
                        results[service_name] = result
                    else:
                        self._logger.warning(f"Service {service_name} doesn't have method {operation}")
                        
                except Exception as e:
                    error_msg = f"Error in service {service_name}: {str(e)}"
                    errors.append(error_msg)
                    self._logger.error(error_msg, exc_info=True)
            
            # Формируем результат
            success = len(errors) == 0
            result = CoordinationResult(
                success=success,
                data=results,
                errors=errors,
                metadata={"operation": operation, "services_count": len(execution_order)}
            )
            
            await self._emit_event(
                CoordinatorEvent.COMPLETED if success else CoordinatorEvent.FAILED,
                result
            )
            
            return result
            
        except Exception as e:
            error_result = CoordinationResult(
                success=False,
                errors=[str(e)],
                metadata={"operation": operation}
            )
            await self._emit_event(CoordinatorEvent.FAILED, error_result)
            return error_result

# ================================
# 4. СПЕЦИАЛИЗИРОВАННЫЕ КООРДИНАТОРЫ
# ================================

class TransactionalCoordinator(ServiceCoordinator):
    """Координатор с поддержкой транзакций"""
    
    def __init__(self):
        super().__init__()
        self._transaction_managers: List[Any] = []
    
    def add_transaction_manager(self, manager: Any) -> None:
        """Добавляет менеджер транзакций"""
        self._transaction_managers.append(manager)
    
    @asynccontextmanager
    async def transaction_context(self):
        """Контекстный менеджер для управления транзакциями"""
        transactions = []
        
        try:
            # Начинаем все транзакции
            for manager in self._transaction_managers:
                if hasattr(manager, 'begin_transaction'):
                    tx = await manager.begin_transaction()
                    transactions.append(tx)
            
            yield transactions
            
            # Коммитим все транзакции
            for tx in transactions:
                if hasattr(tx, 'commit'):
                    await tx.commit()
                    
        except Exception as e:
            # Откатываем все транзакции при ошибке
            for tx in transactions:
                if hasattr(tx, 'rollback'):
                    try:
                        await tx.rollback()
                    except Exception as rollback_error:
                        self._logger.error(f"Rollback error: {rollback_error}")
            raise e
    
    async def coordinate_transactional(self, operation: str, *args, **kwargs) -> CoordinationResult:
        """Координирует выполнение операции в рамках транзакции"""
        
        async with self.transaction_context():
            return await self.coordinate(operation, *args, **kwargs)

class PipelineCoordinator(BaseCoordinator):
    """Координатор для последовательного выполнения pipeline операций"""
    
    def __init__(self):
        super().__init__()
        self._pipeline_steps: List[callable] = []
    
    def add_step(self, step: callable) -> None:
        """Добавляет шаг в pipeline"""
        self._pipeline_steps.append(step)
    
    async def coordinate(self, initial_data: Any, **context) -> CoordinationResult:
        """Координирует выполнение pipeline"""
        
        await self._emit_event(CoordinatorEvent.STARTED, initial_data)
        
        try:
            result_data = initial_data
            step_results = []
            
            # Устанавливаем контекст
            for key, value in context.items():
                self.set_context(key, value)
            
            # Выполняем каждый шаг pipeline
            for i, step in enumerate(self._pipeline_steps):
                try:
                    self._logger.debug(f"Executing pipeline step {i + 1}")
                    
                    if asyncio.iscoroutinefunction(step):
                        result_data = await step(result_data, self._context)
                    else:
                        result_data = step(result_data, self._context)
                    
                    step_results.append({
                        'step': i + 1,
                        'function': step.__name__ if hasattr(step, '__name__') else str(step),
                        'result': result_data
                    })
                    
                except Exception as e:
                    error_msg = f"Error in pipeline step {i + 1}: {str(e)}"
                    result = CoordinationResult(
                        success=False,
                        data=result_data,
                        errors=[error_msg],
                        metadata={'step_results': step_results, 'failed_step': i + 1}
                    )
                    await self._emit_event(CoordinatorEvent.FAILED, result)
                    return result
            
            # Успешное завершение
            result = CoordinationResult(
                success=True,
                data=result_data,
                metadata={'step_results': step_results, 'steps_count': len(self._pipeline_steps)}
            )
            
            await self._emit_event(CoordinatorEvent.COMPLETED, result)
            return result
            
        except Exception as e:
            error_result = CoordinationResult(
                success=False,
                errors=[str(e)],
                metadata={'steps_count': len(self._pipeline_steps)}
            )
            await self._emit_event(CoordinatorEvent.FAILED, error_result)
            return error_result

# ================================
# 5. ФАБРИКА КООРДИНАТОРОВ
# ================================

class CoordinatorFactory:
    """Фабрика для создания координаторов"""
    
    _coordinator_types: Dict[str, Type[BaseCoordinator]] = {
        'service': ServiceCoordinator,
        'transactional': TransactionalCoordinator,
        'pipeline': PipelineCoordinator
    }
    
    @classmethod
    def create_coordinator(cls, coordinator_type: str, **kwargs) -> BaseCoordinator:
        """Создает координатор указанного типа"""
        if coordinator_type not in cls._coordinator_types:
            raise ValueError(f"Unknown coordinator type: {coordinator_type}")
        
        coordinator_class = cls._coordinator_types[coordinator_type]
        return coordinator_class(**kwargs)
    
    @classmethod
    def register_coordinator_type(cls, name: str, coordinator_class: Type[BaseCoordinator]) -> None:
        """Регистрирует новый тип координатора"""
        cls._coordinator_types[name] = coordinator_class

if __name__ == "__main__":
    # Базовый пример использования
    import asyncio
    
    async def main():
        # Создаем координатор
        coordinator = CoordinatorFactory.create_coordinator('service')
        
        # Регистрируем обработчик событий
        def on_completed(event, data):
            print(f"Operation completed: {data}")
        
        coordinator.register_handler(CoordinatorEvent.COMPLETED, on_completed)
        
        # Пример сервиса
        class ExampleService:
            def process_data(self, data):
                return f"Processed: {data}"
        
        # Регистрируем сервис
        coordinator.register_service('example', ExampleService())
        
        # Выполняем координацию
        result = await coordinator.coordinate('process_data', 'test_data')
        print(f"Result: {result}")
    
    # Запускаем пример
    # asyncio.run(main())