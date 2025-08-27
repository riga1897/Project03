import abc

class AbstractVacancy(abc.ABC):
    @abc.abstractmethod
    def get_title(self) -> str:
        pass

    @abc.abstractmethod
    def get_salary(self) -> str:
        pass

    @abc.abstractmethod
    def get_url(self) -> str:
        pass

    @abc.abstractmethod
    def get_description(self) -> str:
        pass

    @abc.abstractmethod
    def get_city(self) -> str:
        pass


class Vacancy(AbstractVacancy):
    def __init__(self, title: str, salary: str, url: str, description: str, city: str):
        self.title = title
        self.salary = salary
        self.url = url
        self.description = description
        self.city = city

    def get_title(self) -> str:
        return self.title

    def get_salary(self) -> str:
        return self.salary

    def get_url(self) -> str:
        return self.url

    def get_description(self) -> str:
        return self.description

    def get_city(self) -> str:
        return self.city


class BaseJobAPI(abc.ABC):
    @abc.abstractmethod
    def get_jobs(self, search_query: str) -> list[AbstractVacancy]:
        pass


class BaseParser(abc.ABC):
    @abc.abstractmethod
    def parse(self, html_content: str) -> list[AbstractVacancy]:
        pass


class BaseDBManager(abc.ABC):
    @abc.abstractmethod
    def save_vacancy(self, vacancy: AbstractVacancy) -> None:
        pass

    @abc.abstractmethod
    def get_vacancies(self, search_params: dict) -> list[AbstractVacancy]:
        pass

    @abc.abstractmethod
    def delete_vacancy(self, vacancy_id: int) -> None:
        pass

    @abc.abstractmethod
    def count_vacancies(self) -> int:
        pass