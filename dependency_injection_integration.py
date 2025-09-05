"""
Интеграция координаторов с Dependency Injection в Python

Этот файл показывает различные подходы к интеграции координаторов
с популярными DI контейнерами и фреймворками.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, get_type_hints
from dataclasses import dataclass
import inspect
import asyncio
from functools import wraps
import logging

# ================================
# РАСШИРЕННЫЙ DI КОНТЕЙНЕР
# ================================

T = TypeVar('T')

class Dependency:
    """Маркер зависимости для injection"""
    
    def __init__(self, name: Optional[str] = None, optional: bool = False):
        self.name = name
        self.optional = optional

class Singleton:
    """Маркер для singleton сервисов"""
    
    def __init__(self, cls):
        self.cls = cls

def inject(name: str, optional: bool = False):
    """Декоратор для маркировки параметров как зависимостей"""
    return Dependency(name=name, optional=optional)

class AdvancedDIContainer:
    """Расширенный DI контейнер с автоматическим разрешением зависимостей"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, callable] = {}
        self._singletons: Dict[str, Any] = {}
        self._types: Dict[Type, str] = {}
        self._scoped: Dict[str, Any] = {}
        self._logger = logging.getLogger(__name__)
    
    def register_type(self, interface: Type[T], implementation: Type[T], name: Optional[str] = None):
        """Регистрирует тип с его реализацией"""
        key = name or interface.__name__
        self._types[interface] = key
        self._factories[key] = lambda: self._create_instance(implementation)
        self._logger.debug(f"Registered type {interface.__name__} -> {implementation.__name__}")
    
    def register_singleton(self, interface: Type[T], implementation: Type[T], name: Optional[str] = None):
        """Регистрирует singleton сервис"""
        key = name or interface.__name__
        self._types[interface] = key
        
        if key not in self._singletons:
            self._singletons[key] = self._create_instance(implementation)
        
        self._logger.debug(f"Registered singleton {interface.__name__} -> {implementation.__name__}")
        return self._singletons[key]
    
    def register_instance(self, interface: Type[T], instance: T, name: Optional[str] = None):
        """Регистрирует конкретный экземпляр"""
        key = name or interface.__name__
        self._types[interface] = key
        self._services[key] = instance
        self._logger.debug(f"Registered instance {interface.__name__}")
    
    def register_factory(self, interface: Type[T], factory: callable, name: Optional[str] = None):
        """Регистрирует фабрику для создания экземпляров"""
        key = name or interface.__name__
        self._types[interface] = key
        self._factories[key] = factory
        self._logger.debug(f"Registered factory for {interface.__name__}")
    
    def get(self, interface: Type[T], name: Optional[str] = None) -> T:
        """Получает сервис по типу или имени"""
        key = name or self._types.get(interface, interface.__name__ if hasattr(interface, '__name__') else str(interface))
        
        # Проверяем экземпляры
        if key in self._services:
            return self._services[key]
        
        # Проверяем singletons
        if key in self._singletons:
            return self._singletons[key]
        
        # Проверяем фабрики
        if key in self._factories:
            return self._factories[key]()
        
        # Пытаемся создать автоматически
        if isinstance(interface, type):
            try:
                return self._create_instance(interface)
            except Exception as e:
                self._logger.error(f"Failed to auto-create {interface}: {e}")
        
        raise ValueError(f"Service '{key}' not found in DI container")
    
    def _create_instance(self, cls: Type[T]) -> T:
        """Создает экземпляр класса с автоматическим разрешением зависимостей"""
        # Получаем сигнатуру конструктора
        signature = inspect.signature(cls.__init__)
        type_hints = get_type_hints(cls.__init__)
        
        args = {}
        
        # Разрешаем зависимости для каждого параметра
        for param_name, param in signature.parameters.items():
            if param_name == 'self':
                continue
                
            # Проверяем аннотацию типа
            param_type = type_hints.get(param_name)
            dependency = getattr(param, 'default', None)
            
            if isinstance(dependency, Dependency):
                # Это помеченная зависимость
                try:
                    dep_name = dependency.name or param_name
                    args[param_name] = self.get(param_type, dep_name)
                except ValueError as e:
                    if not dependency.optional:
                        raise e
                    # Игнорируем необязательные зависимости
                    
            elif param_type and param_type in self._types:
                # Пытаемся разрешить по типу
                try:
                    args[param_name] = self.get(param_type)
                except ValueError:
                    if param.default == param.empty:
                        raise ValueError(f"Cannot resolve required dependency {param_name} of type {param_type}")
        
        return cls(**args)
    
    def create_scope(self) -> 'ScopedDIContainer':
        """Создает scoped контейнер"""
        return ScopedDIContainer(self)

class ScopedDIContainer:
    """Scoped DI контейнер для управления временем жизни объектов"""
    
    def __init__(self, parent: AdvancedDIContainer):
        self.parent = parent
        self._scoped_services: Dict[str, Any] = {}
    
    def get(self, interface: Type[T], name: Optional[str] = None) -> T:
        """Получает сервис из scope или родительского контейнера"""
        key = name or interface.__name__ if hasattr(interface, '__name__') else str(interface)
        
        # Проверяем scoped сервисы
        if key in self._scoped_services:
            return self._scoped_services[key]
        
        # Создаем через родительский контейнер и кэшируем
        service = self.parent.get(interface, name)
        self._scoped_services[key] = service
        return service
    
    def dispose(self):
        """Освобождает scoped сервисы"""
        for service in self._scoped_services.values():
            if hasattr(service, 'dispose'):
                try:
                    service.dispose()
                except Exception as e:
                    logging.error(f"Error disposing service: {e}")
        
        self._scoped_services.clear()

# ================================
# ИНТЕГРАЦИЯ С КООРДИНАТОРАМИ
# ================================

class DIIntegratedCoordinator(ABC):
    """Базовый класс координатора с DI интеграцией"""
    
    def __init__(self, container: AdvancedDIContainer, name: str = None):
        self.container = container
        self.name = name or self.__class__.__name__
        self._logger = logging.getLogger(self.name)
        
        # Автоматически инжектим зависимости
        self._inject_dependencies()
    
    def _inject_dependencies(self):
        """Автоматически инжектит зависимости в поля класса"""
        type_hints = get_type_hints(self.__class__)
        
        for field_name, field_type in type_hints.items():
            if field_name.startswith('_'):  # Игнорируем приватные поля
                continue
                
            try:
                # Пытаемся получить сервис
                service = self.container.get(field_type)
                setattr(self, field_name, service)
                self._logger.debug(f"Injected {field_type.__name__} into {field_name}")
            except ValueError:
                # Игнорируем неразрешимые зависимости
                pass
    
    @abstractmethod
    async def coordinate(self, operation: str, *args, **kwargs):
        """Основной метод координации"""
        pass

def coordinator_service(container_key: str = "default"):
    """Декоратор для регистрации координатора как сервиса"""
    
    def decorator(cls):
        # Добавляем метаинформацию для DI
        cls._di_container_key = container_key
        cls._is_coordinator_service = True
        return cls
    
    return decorator

# ================================
# КОНКРЕТНЫЕ РЕАЛИЗАЦИИ
# ================================

# Определяем интерфейсы сервисов
class IUserService(ABC):
    @abstractmethod
    async def get_user(self, user_id: str) -> Dict[str, Any]:
        pass

class IOrderService(ABC):
    @abstractmethod
    async def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

class INotificationService(ABC):
    @abstractmethod
    async def send_notification(self, user_id: str, message: str) -> bool:
        pass

# Реализации сервисов
class DatabaseUserService(IUserService):
    """Сервис пользователей с базой данных"""
    
    def __init__(self, db_connection: str = inject("database_url")):
        self.db_connection = db_connection
        self._logger = logging.getLogger(__name__)
    
    async def get_user(self, user_id: str) -> Dict[str, Any]:
        self._logger.info(f"Getting user {user_id} from database")
        # Имитация работы с БД
        return {
            "user_id": user_id,
            "name": "John Doe",
            "email": "john@example.com"
        }

class DefaultOrderService(IOrderService):
    """Стандартный сервис заказов"""
    
    def __init__(self, user_service: IUserService):
        self.user_service = user_service
        self._logger = logging.getLogger(__name__)
    
    async def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        user = await self.user_service.get_user(order_data["user_id"])
        self._logger.info(f"Creating order for user: {user['name']}")
        
        return {
            "order_id": f"ORD_{hash(str(order_data)) % 10000:04d}",
            "user": user,
            "items": order_data["items"],
            "status": "created"
        }

class EmailNotificationService(INotificationService):
    """Сервис email уведомлений"""
    
    def __init__(self, smtp_config: str = inject("smtp_config", optional=True)):
        self.smtp_config = smtp_config
        self._logger = logging.getLogger(__name__)
    
    async def send_notification(self, user_id: str, message: str) -> bool:
        self._logger.info(f"Sending email notification to user {user_id}: {message}")
        return True

@coordinator_service("order_processing")
class OrderProcessingCoordinator(DIIntegratedCoordinator):
    """Координатор обработки заказов с DI"""
    
    # Зависимости будут автоматически инжектированы
    user_service: IUserService
    order_service: IOrderService
    notification_service: INotificationService
    
    async def coordinate(self, operation: str, *args, **kwargs):
        """Координирует обработку заказа"""
        
        if operation == "process_order":
            return await self._process_order(*args, **kwargs)
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    async def _process_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обрабатывает заказ через координацию сервисов"""
        
        try:
            # Создаем заказ
            order = await self.order_service.create_order(order_data)
            
            # Отправляем уведомление
            await self.notification_service.send_notification(
                order_data["user_id"],
                f"Order {order['order_id']} has been created"
            )
            
            return {
                "success": True,
                "order": order,
                "message": "Order processed successfully"
            }
            
        except Exception as e:
            self._logger.error(f"Order processing failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# ================================
# ИНТЕГРАЦИЯ С ПОПУЛЯРНЫМИ ФРЕЙМВОРКАМИ
# ================================

class FastAPIIntegration:
    """Интеграция с FastAPI"""
    
    def __init__(self, container: AdvancedDIContainer):
        self.container = container
    
    def create_dependency(self, interface: Type[T]):
        """Создает FastAPI dependency"""
        def dependency():
            return self.container.get(interface)
        return dependency
    
    def setup_coordinators(self, app):
        """Настраивает координаторы для FastAPI приложения"""
        @app.on_event("startup")
        async def setup_di():
            # Настройка DI контейнера при запуске приложения
            pass
        
        @app.on_event("shutdown") 
        async def cleanup_di():
            # Очистка ресурсов при остановке
            pass

class FlaskIntegration:
    """Интеграция с Flask"""
    
    def __init__(self, container: AdvancedDIContainer):
        self.container = container
    
    def init_app(self, app):
        """Инициализирует интеграцию с Flask приложением"""
        app.di_container = self.container
        
        @app.teardown_appcontext
        def cleanup_di(error):
            # Очистка scoped сервисов
            if hasattr(app, 'current_scope'):
                app.current_scope.dispose()

# ================================
# ПРИМЕР ИСПОЛЬЗОВАНИЯ
# ================================

async def demonstrate_di_integration():
    """Демонстрация интеграции координаторов с DI"""
    print("\n" + "=" * 60)
    print("🔌 DEPENDENCY INJECTION INTEGRATION EXAMPLE") 
    print("=" * 60)
    
    # Создаем DI контейнер
    container = AdvancedDIContainer()
    
    # Регистрируем конфигурации
    container.register_instance(str, "postgresql://localhost/mydb", "database_url")
    container.register_instance(str, "smtp://localhost:587", "smtp_config")
    
    # Регистрируем сервисы
    container.register_type(IUserService, DatabaseUserService)
    container.register_type(IOrderService, DefaultOrderService)
    container.register_singleton(INotificationService, EmailNotificationService)
    
    # Создаем координатор
    coordinator = OrderProcessingCoordinator(container)
    
    # Используем координатор
    order_data = {
        "user_id": "user_123",
        "items": [
            {"product_id": "prod_1", "quantity": 2},
            {"product_id": "prod_2", "quantity": 1}
        ]
    }
    
    result = await coordinator.coordinate("process_order", order_data)
    
    if result["success"]:
        print("✅ Order processing completed with DI!")
        print(f"📦 Order ID: {result['order']['order_id']}")
        print(f"👤 Customer: {result['order']['user']['name']}")
    else:
        print(f"❌ Order processing failed: {result['error']}")
    
    # Демонстрируем scoped контейнер
    print("\n🔄 Demonstrating scoped container...")
    with container.create_scope() as scope:
        scoped_coordinator = OrderProcessingCoordinator(scope)
        scoped_result = await scoped_coordinator.coordinate("process_order", order_data)
        print(f"✅ Scoped processing: {scoped_result['success']}")

def setup_production_container() -> AdvancedDIContainer:
    """Настройка production DI контейнера"""
    container = AdvancedDIContainer()
    
    # Конфигурации из переменных окружения
    import os
    container.register_instance(str, os.getenv("DATABASE_URL", "sqlite:///app.db"), "database_url")
    container.register_instance(str, os.getenv("SMTP_CONFIG", "smtp://localhost"), "smtp_config")
    
    # Регистрируем все сервисы
    container.register_singleton(IUserService, DatabaseUserService)
    container.register_singleton(IOrderService, DefaultOrderService)
    container.register_singleton(INotificationService, EmailNotificationService)
    
    # Регистрируем координаторы
    container.register_factory(OrderProcessingCoordinator, 
                              lambda: OrderProcessingCoordinator(container))
    
    return container

if __name__ == "__main__":
    # Настраиваем логирование
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Запускаем демонстрацию
    asyncio.run(demonstrate_di_integration())