from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from library.views import (
    AuthorViewSet,
    BookViewSet,
    BorrowRecordViewSet,
    UserViewSet,
)

# Конфигурация Swagger / OpenAPI документации
schema_view = get_schema_view(
    openapi.Info(
        title="Library Management REST API",
        default_version='v1',
        description="API для управления библиотекой, авторами, книгами и выдачей книг",
        contact=openapi.Contact(email="admin@library.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Регистрация маршрутов DRF
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'books', BookViewSet, basename='book')
router.register(r'borrow-records', BorrowRecordViewSet, basename='borrow-record')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    
    # JWT Аутентификация
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Автодокументация OpenAPI
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]