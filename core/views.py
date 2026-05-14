from rest_framework import generics, filters
from .models import Aluno
from .serializers import AlunoSerializer

class AlunoListView(generics.ListAPIView):
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['matricula', 'nome', 'cpf']
