from django.urls import path
from . import views

urlpatterns = [
    # Histórico (Lista)
    path('', views.DailyRecordListView.as_view(), name='dailyrecord_list'),

    # --- NOVAS ROTAS DE PLANTÃO ---
    path('iniciar/', views.StartShiftView.as_view(), name='shift_start'),
    path('encerrar/', views.EndShiftView.as_view(), name='shift_end'),
    path('adicionar/<str:type>/', views.AddFinanceView.as_view(), name='shift_add_finance'),

    # Edição/Exclusão de histórico
    path('<int:pk>/editar/', views.DailyRecordUpdateView.as_view(), name='dailyrecord_update'),
    path('<int:pk>/excluir/', views.DailyRecordDeleteView.as_view(), name='dailyrecord_delete'),

    # Rotas de Manutenção
    path('manutencao/', views.MaintenanceListView.as_view(), name='maintenance_list'),
    path('manutencao/nova/', views.MaintenanceCreateView.as_view(), name='maintenance_create'),
    path('manutencao/<int:pk>/editar/', views.MaintenanceUpdateView.as_view(), name='maintenance_update'),
    path('manutencao/<int:pk>/excluir/', views.MaintenanceDeleteView.as_view(), name='maintenance_delete'),

    # Rotas de Categorias
    path('categorias/', views.CategoryListView.as_view(), name='category_list'),
    path('categorias/nova/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categorias/<int:pk>/editar/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categorias/<int:pk>/excluir/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # Rota da API (AJAX)
    path('api/get-km/<int:vehicle_id>/', views.get_last_km, name='get_last_km'),
]
