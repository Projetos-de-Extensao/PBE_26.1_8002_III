import jwt
from django.conf import settings
from django.http import JsonResponse

class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        rotas_livres = ['/admin/', '/api/login/']
        
        for rota in rotas_livres:
            if request.path.startswith(rota):
                return self.get_response(request)

        auth_header = request.headers.get('Authorization')

        if auth_header == None:
            return JsonResponse({'erro': 'Token JWT não foi enviado.'}, status=401)
            
        if not auth_header.startswith('Bearer '):
            return JsonResponse({'erro': 'O token precisa começar com Bearer.'}, status=401)

        partes_do_token = auth_header.split(' ')
        token_real = partes_do_token[1]

        try:
            payload = jwt.decode(token_real, settings.SECRET_KEY, algorithms=['HS256'])
            
            request.user_id = payload.get('user_id')
            
        except jwt.ExpiredSignatureError:
            return JsonResponse({'erro': 'Token expirado. Faça login de novo.'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'erro': 'Token inválido.'}, status=401)

        return self.get_response(request)