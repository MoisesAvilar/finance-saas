from django.contrib import admin
from django.urls import path, include
from core.views import DashboardView
from accounts.views import DeleteAccountView
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('painel/', DashboardView.as_view(), name='dashboard'),
    path('', include('pwa.urls')),

    # Apps
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('core/', include('core.urls')),
    path('veiculos/', include('vehicles.urls')),
    path('operacoes/', include('operations.urls')),
    path('relatorios/', include('analytics.urls')),

    # Rota da Política de Privacidade (Pública)
    path('privacidade/', TemplateView.as_view(template_name='legal/privacy.html'), name='privacy'),
    path('termos/', TemplateView.as_view(template_name='legal/terms.html'), name='terms'),
    path('ajuda/', TemplateView.as_view(template_name='support/help.html'), name='help'),

    path('perfil/excluir/', DeleteAccountView.as_view(), name='account_delete'),
]
