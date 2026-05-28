from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import Aluno, Processo
from .serializers import AlunoSerializer, ProcessoSerializer
from .permissions import IsSecretaria, IsAluno

@api_view(['GET', 'POST', 'PATCH'])
@permission_classes([IsSecretaria])
def aluno(request):
    if request.method == 'PATCH':
        parsed_data = request.data
        matricula = request.GET.get('matricula_aluno', None)
        if matricula is not None:
            try:
                old_data = Aluno.objects.get(matricula=matricula)
            except Aluno.DoesNotExist:
                return Response({"error": "Aluno não encontrado"}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = AlunoSerializer(old_data, data=parsed_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "updated"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Matrícula não informada"}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'POST':
        parsed_data = request.data
        serializer = AlunoSerializer(data=parsed_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message":"Aluno criado com sucesso!"}, status=status.HTTP_201_CREATED)

    if request.method == 'GET':
        data = Aluno.objects.all()
        params = request.GET.get('matricula', None)
        if params is not None:
            data = data.filter(matricula=params)    
        
        serializer = AlunoSerializer(data, many=True)
        # O DRF já renderiza a resposta automaticamente com o Response
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'PATCH'])
@permission_classes([IsAluno | IsSecretaria])
def processo(request):
    if request.method == 'POST':
        parsed_data = request.data
        serializer = ProcessoSerializer(data=parsed_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"created":"successfull"}, status=status.HTTP_201_CREATED)
        
    if request.method == 'GET':
        data = Processo.objects.all()
        params = request.GET.get('matricula_aluno', None)
        if params is not None:
            data = Processo.objects.select_related('matricula_aluno')
        serializer = ProcessoSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    if request.method == 'PATCH':
        parsed_data = request.data
        id = request.GET.get('processo_id', None)
        if id is not None:
            try:
                old_data = Processo.objects.get(id=id)
            except Processo.DoesNotExist:
                return Response({"error": "Processo não encontrado"}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = ProcessoSerializer(old_data, data=parsed_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "updated"}, status=status.HTTP_200_OK)
            
        else:
            return Response({"error": "Id não informado"}, status=status.HTTP_400_BAD_REQUEST)


class MultipleObjectAPIView(ListAPIView):       
    authentication_classes = [TokenAuthentication]
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        print(request.user)
        response = super().get(request, *args, **kwargs)
        return response

class SingleObjectAPIView(RetrieveAPIView):
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer