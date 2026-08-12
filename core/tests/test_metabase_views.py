"""
Testes para MetabaseDashboardAPIView.

Cobre todos os caminhos:
- RBAC (Secretaria → 200, Coordenador → 200, Aluno → 403)
- Não autenticado → 401
- Payload JWT (dashboard ID correto, expiração 10 min)
- Configuração ausente → 503
"""

import time

import jwt
import pytest
from django.test import override_settings
from rest_framework.test import APIClient

METABASE_URL = "/dashboard/metabase/"
TEST_SECRET = "test-metabase-secret-key"
DASHBOARD_IDS = {"secretaria": 1, "coordenador": 2}

METABASE_OVERRIDES = {
    "METABASE_SECRET_KEY": TEST_SECRET,
    "METABASE_SITE_URL": "http://localhost:3000",
    "METABASE_DASHBOARD_IDS": DASHBOARD_IDS,
}


def _extract_token(iframe_url: str) -> str:
    """
    Extrai o JWT da URL de embedding do Metabase.

    Formato esperado:
        http://localhost:3000/embed/dashboard/<JWT>#bordered=false&titled=true
    """
    # Remove o fragment (#bordered=false&titled=true)
    url_without_fragment = iframe_url.split("#")[0]
    # O token é o último segmento do path
    return url_without_fragment.rsplit("/", 1)[-1]


@pytest.mark.django_db
class TestMetabaseDashboardAPIView:
    """Testes do endpoint /api/dashboard/metabase/."""

    # ── RBAC ──────────────────────────────────────────────────────────

    @override_settings(**METABASE_OVERRIDES)
    def test_secretaria_gets_200_with_iframe_url(self, secretaria):
        client = APIClient()
        client.force_authenticate(user=secretaria)

        response = client.get(METABASE_URL)

        assert response.status_code == 200
        assert "iframe_url" in response.data
        assert "/embed/dashboard/" in response.data["iframe_url"]

    @override_settings(**METABASE_OVERRIDES)
    def test_coordenador_gets_200_with_iframe_url(self, coordenador):
        client = APIClient()
        client.force_authenticate(user=coordenador)

        response = client.get(METABASE_URL)

        assert response.status_code == 200
        assert "iframe_url" in response.data
        assert "/embed/dashboard/" in response.data["iframe_url"]

    @override_settings(**METABASE_OVERRIDES)
    def test_aluno_gets_403(self, aluno):
        client = APIClient()
        client.force_authenticate(user=aluno)

        response = client.get(METABASE_URL)

        assert response.status_code == 403
        assert "detail" in response.data

    def test_unauthenticated_gets_401(self):
        client = APIClient()

        response = client.get(METABASE_URL)

        assert response.status_code == 401

    # ── JWT Payload ───────────────────────────────────────────────────

    @override_settings(**METABASE_OVERRIDES)
    def test_jwt_contains_correct_dashboard_id_for_secretaria(self, secretaria):
        client = APIClient()
        client.force_authenticate(user=secretaria)

        response = client.get(METABASE_URL)
        assert response.status_code == 200

        token = _extract_token(response.data["iframe_url"])
        payload = jwt.decode(token, TEST_SECRET, algorithms=["HS256"])

        assert payload["resource"]["dashboard"] == DASHBOARD_IDS["secretaria"]

    @override_settings(**METABASE_OVERRIDES)
    def test_jwt_contains_correct_dashboard_id_for_coordenador(self, coordenador):
        client = APIClient()
        client.force_authenticate(user=coordenador)

        response = client.get(METABASE_URL)
        assert response.status_code == 200

        token = _extract_token(response.data["iframe_url"])
        payload = jwt.decode(token, TEST_SECRET, algorithms=["HS256"])

        assert payload["resource"]["dashboard"] == DASHBOARD_IDS["coordenador"]

    @override_settings(**METABASE_OVERRIDES)
    def test_jwt_token_expires_in_10_minutes(self, secretaria):
        client = APIClient()
        client.force_authenticate(user=secretaria)

        now = int(time.time())
        response = client.get(METABASE_URL)
        assert response.status_code == 200

        token = _extract_token(response.data["iframe_url"])
        payload = jwt.decode(token, TEST_SECRET, algorithms=["HS256"])

        exp = payload["exp"]
        # Tolerância de 5 segundos para o tempo de execução do teste
        assert 595 <= (exp - now) <= 605

    # ── Configuração ausente ──────────────────────────────────────────

    @override_settings(METABASE_SECRET_KEY="")
    def test_missing_secret_key_returns_503(self, secretaria):
        client = APIClient()
        client.force_authenticate(user=secretaria)

        response = client.get(METABASE_URL)

        assert response.status_code == 503
        assert "METABASE_SECRET_KEY" in response.data["detail"]
