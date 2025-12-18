from django.urls import path
from . import views

urlpatterns = [
    # Rotas de DailyRecord (Mantenha as que já existem)
    path('', views.DailyRecordListView.as_view(), name='dailyrecord_list'),
    path('novo/', views.DailyRecordCreateView.as_view(), name='dailyrecord_create'),
    path('<int:pk>/editar/', views.DailyRecordUpdateView.as_view(), name='dailyrecord_update'),
    path('<int:pk>/excluir/', views.DailyRecordDeleteView.as_view(), name='dailyrecord_delete'),

    # Rotas de Manutenção (Novas)
    path('manutencao/', views.MaintenanceListView.as_view(), name='maintenance_list'),
    path('manutencao/nova/', views.MaintenanceCreateView.as_view(), name='maintenance_create'),
    path('manutencao/<int:pk>/editar/', views.MaintenanceUpdateView.as_view(), name='maintenance_update'),
    path('manutencao/<int:pk>/excluir/', views.MaintenanceDeleteView.as_view(), name='maintenance_delete'),
]
