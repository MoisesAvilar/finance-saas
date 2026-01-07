from django.contrib import admin
from django.urls import path, include
from core.views import DashboardView
from accounts.views import DeleteAccountView
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- ROTAS DE AUTENTICAÇÃO (JWT) ---
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # --- ROTAS DA API ---
    path('api/accounts/', include('accounts.api_urls')),
    path('api/analytics/', include('analytics.api_urls')),
    path('api/common/', include('common.api_urls')),
    path('api/core/', include('core.api_urls')),
    path('api/operations/', include('operations.api_urls')),
    path('api/vehicles/', include('vehicles.api_urls')),

    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('painel/', DashboardView.as_view(), name='dashboard'),
    path('', include('pwa.urls')),

    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('core/', include('core.urls')),
    path('operacoes/', include('operations.urls')),
    path('relatorios/', include('analytics.urls')),
    path('common/', include('common.urls')),
    path('veiculos/', include('vehicles.urls')),

    path('privacidade/', TemplateView.as_view(template_name='legal/privacy.html'), name='privacy'),
    path('termos/', TemplateView.as_view(template_name='legal/terms.html'), name='terms'),
    path('ajuda/', TemplateView.as_view(template_name='support/help.html'), name='help'),
    path('perfil/excluir/', DeleteAccountView.as_view(), name='account_delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)