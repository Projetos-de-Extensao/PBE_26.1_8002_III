from rest_framework import serializers

class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, help_text="Matrícula do aluno ou nome de usuário")
    password = serializers.CharField(write_only=True, help_text="Senha do usuário")

class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField(help_text="Token JWT de acesso")
    refresh = serializers.CharField(help_text="Token JWT para renovar o acesso")

class PrimeiroAcessoRequestSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, help_text="Matrícula do aluno")
    old_password = serializers.CharField(write_only=True, help_text="Senha temporária atual")
    new_password = serializers.CharField(write_only=True, help_text="Nova senha a ser cadastrada")

class MessageResponseSerializer(serializers.Serializer):
    message = serializers.CharField(help_text="Mensagem descritiva do resultado da operação")
