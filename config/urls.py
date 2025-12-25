from django.contrib import admin
from django.urls import path, include
from core.views import DashboardView
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('painel/', DashboardView.as_view(), name='dashboard'),
    path('', include('pwa.urls')),

    # Apps
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('veiculos/', include('vehicles.urls')),
    path('operacoes/', include('operations.urls')),
    path('relatorios/', include('analytics.urls')),
]
