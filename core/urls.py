from django.urls import path
from .views import ContratoPendenteListView

urlpatterns = [
    path('contratos/pendentes/', ContratoPendenteListView.as_view(), name='listar-contratos-pendentes'),
]