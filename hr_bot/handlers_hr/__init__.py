from .search import router as search_router
from .vacancies import router as vacancies_router
from .analytics import router as analytics_router

__all__ = ['search_router', 'vacancies_router', 'analytics_router']