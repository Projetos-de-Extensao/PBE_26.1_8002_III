from rest_framework import generics
from .models import Aluno
from .serializers import AlunoSerializer

class AlunoListView(generics.ListAPIView):
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer
