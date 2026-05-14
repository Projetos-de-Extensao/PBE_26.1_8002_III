from rest_framework import generics
from .models import Contrato
from .serializers import ContratoSerializer

class ContratoPendenteListView(generics.ListAPIView):
    serializer_class = ContratoSerializer

    def get_queryset(self):
        return Contrato.objects.filter(assinatura_faculdade=False)