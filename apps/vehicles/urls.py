from django.urls import path
from . import views

urlpatterns = [
    path("", views.VehicleListView.as_view(), name="vehicle_list"),
    path("novo/", views.VehicleCreateView.as_view(), name="vehicle_create"),
    path("<int:pk>/", views.VehicleDetailView.as_view(), name="vehicle_detail"),
    path("<int:pk>/editar/", views.VehicleUpdateView.as_view(), name="vehicle_update"),
    path("<int:pk>/excluir/", views.VehicleDeleteView.as_view(), name="vehicle_delete"),
]
