from rest_framework import serializers

class LoginRequestSerializer(serializers.Serializer):
    """
    Valida a entrada de dados para o endpoint de Login.
    Não interage diretamente com banco de dados, apenas garante que
    os campos 'username' (matrícula) e 'password' estejam presentes e no formato correto.
    """
    username = serializers.CharField(max_length=150, help_text="Matrícula do aluno ou nome de usuário")
    password = serializers.CharField(write_only=True, help_text="Senha do usuário")

class LoginResponseSerializer(serializers.Serializer):
    """
    Serializer de documentação. Mostra como o JWT é retornado ao cliente
    (com os tokens de acesso e refresh).
    """
    access = serializers.CharField(help_text="Token JWT de acesso")
    refresh = serializers.CharField(help_text="Token JWT para renovar o acesso")

class PrimeiroAcessoRequestSerializer(serializers.Serializer):
    """
    Usado no fluxo de redefinição obrigatória de senha (primeiro acesso).
    Exige a senha antiga temporária e a nova senha que será cadastrada, 
    tudo sendo protegido via write_only.
    """
    username = serializers.CharField(max_length=150, help_text="Matrícula do aluno")
    old_password = serializers.CharField(write_only=True, help_text="Senha temporária atual")
    new_password = serializers.CharField(write_only=True, help_text="Nova senha a ser cadastrada")

class MessageResponseSerializer(serializers.Serializer):
    message = serializers.CharField(help_text="Mensagem descritiva do resultado da operação")

class UserMeSerializer(serializers.Serializer):
    """
    Serializer de retorno para o endpoint /me/.
    Contém os dados básicos do usuário logado e o seu papel (role).
    """
    id = serializers.IntegerField(help_text="ID do usuário na tabela de domínio")
    nome = serializers.CharField(help_text="Nome do usuário")
    email = serializers.EmailField(help_text="E-mail do usuário")
    matricula = serializers.CharField(help_text="Matrícula do usuário")
    role = serializers.CharField(help_text="Papel do usuário (ALUNO, SECRETARIA, COORDENADOR)")
