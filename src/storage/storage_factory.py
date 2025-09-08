from src.storage.abstract import AbstractVacancyStorage
from src.storage.postgres_saver import PostgresSaver


class StorageFactory:
    """Фабрика для создания объектов хранилища PostgreSQL"""

    @staticmethod
    def create_storage(storage_type: str = "postgres") -> AbstractVacancyStorage:
        """
        Создает экземпляр хранилища PostgreSQL

        Args:
            storage_type: Тип хранилища (только 'postgres' поддерживается)

        Returns:
            AbstractVacancyStorage: Экземпляр PostgreSQL хранилища
        """
        if storage_type != "postgres":
            raise ValueError(f"Поддерживается только PostgreSQL хранилище, получен: {storage_type}")

        from src.config.app_config import AppConfig

        app_config = AppConfig()
        return PostgresSaver(app_config.get_db_config())

    @staticmethod
    def get_default_storage() -> AbstractVacancyStorage:
        """
        Возвращает хранилище по умолчанию

        Returns:
            AbstractVacancyStorage: PostgreSQL хранилище
        """
        return StorageFactory.create_storage("postgres")
