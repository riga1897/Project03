# Project03 - Job Vacancy Search System

## Overview
Russian coursework project (#3) - a comprehensive job vacancy management system that retrieves data from job sites (HeadHunter and SuperJob), stores it in PostgreSQL database, and provides analytical capabilities.

## Purpose
- Retrieve company and vacancy data from hh.ru using public API
- Design PostgreSQL database tables for storing employer and vacancy data  
- Implement DBManager class for database operations and analytics
- Provide console interface for searching, filtering, and managing vacancies

## Key Features
- **API Integration**: HeadHunter (hh.ru) and SuperJob APIs with caching
- **Database Storage**: PostgreSQL with psycopg2, automatic table creation
- **Console Interface**: Interactive Russian language menu system
- **Analytics**: DBManager with methods for statistical analysis
- **Filtering**: Advanced search and filtering capabilities
- **Caching**: API response caching with configurable TTL

## Current Setup Status
✅ **Environment**: Successfully migrated from Python 3.13 to Python 3.12.11  
✅ **Dependencies**: pydantic ^2.11.8 + pydantic-core compatible versions, all compatibility issues resolved  
✅ **Database**: PostgreSQL database created and configured with psycopg2-binary  
✅ **Application**: Console app launches successfully with interactive Russian menu  
✅ **Workflow**: Console App workflow configured and running  
✅ **Tests**: 2120+ tests passing, comprehensive test coverage verified  

## Project Architecture
```
src/
├── api_modules/       # API integration (HH, SuperJob, unified)
├── config/           # Configuration classes for all components
├── storage/          # Database management, repositories, services
├── ui_interfaces/    # Console interface and user interaction
├── utils/           # Utilities (formatters, parsers, helpers)
└── vacancies/       # Data models and parsers
```

## Environment Configuration
- **Database**: PostgreSQL (DATABASE_URL configured)
- **Package Manager**: Poetry 
- **Python Version**: 3.12.11
- **Cache Directory**: data/cache/ (HH and SJ caches)

## Running the Application
- **Main Application**: `poetry run python main.py`
- **Via run.sh**: `./run.sh app` (default) or `./run.sh` 
- **Tests**: `./run.sh test` or `poetry run pytest`

## Available Menu Options
1. Search vacancies by query (source selection + API call)
2. Show all saved vacancies
3. Top N saved vacancies by salary
4. Search in saved vacancies by keyword
5. Advanced search (multiple keywords)
6. Filter saved vacancies by salary  
7. Delete saved vacancies
8. Clear API cache
9. SuperJob API configuration
10. DBManager demonstration (database analysis)

## Dependencies
- **Core**: pydantic, psycopg2-binary, requests, python-dotenv
- **Development**: pytest, mypy, black, flake8, isort
- **Web**: flask, gunicorn (for potential web interface)

## Recent Changes
- **Setup completed**: Fixed pydantic dependencies, configured PostgreSQL database
- **Workflow configured**: Console App workflow for interactive use
- **Environment ready**: All dependencies installed via Poetry

## User Preferences
- **Language**: Russian interface
- **Interface**: Console-based interactive system
- **Architecture**: Modular design following SOLID principles
- **Testing**: Comprehensive test coverage with pytest

## Notes
- This is a console application, not a web application
- Requires interactive terminal for user input
- Database tables are automatically created on first run
- API keys for SuperJob can be configured via menu option 9