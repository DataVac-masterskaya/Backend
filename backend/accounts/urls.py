from django.urls import path
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.constants import ANY_ROLE, AUTH_TAG
from accounts.serializers import TokenPairResponseSerializer

urlpatterns = [
    path(
        'auth/login/',
        extend_schema(
            tags=[AUTH_TAG],
            summary='Получение токена по логину/паролю',
            description=ANY_ROLE,
            responses={
                status.HTTP_200_OK: TokenPairResponseSerializer,
            },
        )(TokenObtainPairView).as_view(),
        name='token_obtain',
    ),
    path(
        'auth/token/refresh/',
        extend_schema(tags=[AUTH_TAG], summary='Обновление токена', description=ANY_ROLE)(TokenRefreshView).as_view(),
        name='token_refresh',
    ),
]
