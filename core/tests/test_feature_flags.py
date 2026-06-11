import pytest
import sys
from unittest.mock import patch
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.admin import AdminSite
from django.core.files.uploadedfile import SimpleUploadedFile

from core.models import FeatureFlag, Contrato
from core.admin import FeatureFlagAdmin


@pytest.fixture(autouse=True)
def clear_django_cache():
    """Limpa o cache do Django antes de cada teste."""
    cache.clear()
    yield
    cache.clear()


@pytest.mark.django_db
class TestFeatureFlagModel:

    def test_create_feature_flag_populates_cache(self):
        """Salvar uma feature flag deve atualizar o cache imediatamente sem expiração."""
        flag = FeatureFlag.objects.create(name="test_flag", is_enabled=True)
        
        # O cache deve conter o valor True imediatamente
        cached_val = cache.get("feature_flag:test_flag")
        assert cached_val is True

    def test_update_feature_flag_updates_cache(self):
        """Atualizar o status de uma feature flag deve refletir no cache imediatamente."""
        flag = FeatureFlag.objects.create(name="test_flag", is_enabled=True)
        assert cache.get("feature_flag:test_flag") is True

        flag.is_enabled = False
        flag.save()
        assert cache.get("feature_flag:test_flag") is False

    def test_is_active_cache_hit(self):
        """Se o valor estiver no cache, deve retornar o valor do cache sem consultar o banco."""
        # Coloca manualmente no cache
        cache.set("feature_flag:cache_only_flag", True, timeout=60)
        
        # Como o cache tem prioridade, deve retornar True mesmo não existindo no banco
        assert FeatureFlag.is_active("cache_only_flag") is True

    def test_is_active_cache_miss_found_in_db(self):
        """Se houver cache miss, deve buscar no banco, salvar no cache por 24h e retornar o valor."""
        flag = FeatureFlag.objects.create(name="db_flag", is_enabled=True)
        # Limpa o cache após a criação automática para simular cache miss
        cache.clear()
        assert cache.get("feature_flag:db_flag") is None

        # Primeira chamada (cache miss) -> busca no banco e cacheia
        assert FeatureFlag.is_active("db_flag") is True
        
        # O valor deve ter sido salvo no cache (Cache-Aside)
        assert cache.get("feature_flag:db_flag") is True

    def test_is_active_not_found(self):
        """Se a flag não existir nem no cache nem no banco, retorna False."""
        assert FeatureFlag.is_active("non_existent_flag") is False

    def test_validation_invalid_names(self):
        """Validadores devem impedir nomes com letras maiúsculas, espaços ou caracteres especiais."""
        invalid_names = ["TestFlag", "test-flag", "test flag", "test_flag!", "TEST_FLAG"]
        
        for name in invalid_names:
            flag = FeatureFlag(name=name, is_enabled=True)
            with pytest.raises(ValidationError):
                flag.full_clean()

    def test_validation_valid_name(self):
        """Validadores devem aceitar nomes com letras minúsculas, números e sublinhados."""
        valid_names = ["test_flag", "async_contract_ai", "flag_123", "flag"]
        for name in valid_names:
            flag = FeatureFlag(name=name, is_enabled=True)
            # Não deve lançar ValidationError
            flag.full_clean()


@pytest.mark.django_db
class TestFeatureFlagAdmin:

    def test_save_model_sets_updated_by(self):
        """O método save_model do admin deve associar automaticamente o usuário logado."""
        site = AdminSite()
        admin_instance = FeatureFlagAdmin(FeatureFlag, site)

        # Mock de request com usuário autenticado
        class MockRequest:
            def __init__(self, user):
                self.user = user

        from django.contrib.auth.hashers import make_password
        user = User.objects.create(matricula="admin_user", email="admin@ibmec.edu.br", password=make_password("test"))
        request = MockRequest(user)
        
        flag = FeatureFlag(name="admin_flag", is_enabled=True)
        
        # Executa save_model
        admin_instance.save_model(request, flag, form=None, change=False)
        
        assert flag.updated_by == user
        assert FeatureFlag.objects.filter(name="admin_flag", updated_by=user).exists()


@pytest.fixture
def run_in_prod():
    """Remove 'pytest' de sys.modules temporariamente para simular ambiente de produção."""
    pytest_entry = sys.modules.get('pytest')
    if 'pytest' in sys.modules:
        del sys.modules['pytest']
    yield
    if pytest_entry is not None:
        sys.modules['pytest'] = pytest_entry


@pytest.mark.django_db
class TestFeatureFlagIntegration:

    def test_upload_contrato_with_flag_active(self, api_client, processo, run_in_prod):
        """Se a flag 'async_contract_ai' estiver ativa, deve agendar a task no Celery."""
        # Ativa a feature flag
        FeatureFlag.objects.create(name="async_contract_ai", is_enabled=True)

        arquivo = SimpleUploadedFile(
            "contrato.pdf",
            b"%PDF-1.4 fake content for test",
            content_type="application/pdf"
        )
        
        with patch('core.tasks.processarContratoComIa.delay') as mock_delay:
            response = api_client.post(
                f"/processo/{processo.id}/contrato/",
                {"arquivo": arquivo},
                format="multipart"
            )
            assert response.status_code == 201
            mock_delay.assert_called_once()

    def test_upload_contrato_with_flag_inactive(self, api_client, processo, run_in_prod):
        """Se a flag 'async_contract_ai' estiver inativa, NÃO deve agendar a task no Celery."""
        # Cria a feature flag inativa
        FeatureFlag.objects.create(name="async_contract_ai", is_enabled=False)

        arquivo = SimpleUploadedFile(
            "contrato.pdf",
            b"%PDF-1.4 fake content for test",
            content_type="application/pdf"
        )
        
        with patch('core.tasks.processarContratoComIa.delay') as mock_delay:
            response = api_client.post(
                f"/processo/{processo.id}/contrato/",
                {"arquivo": arquivo},
                format="multipart"
            )
            assert response.status_code == 201
            mock_delay.assert_not_called()

    def test_upload_contrato_without_flag_in_db(self, api_client, processo, run_in_prod):
        """Se a flag 'async_contract_ai' não existir no banco, assume inativa (NÃO agenda Celery)."""
        # Garante que não existe nenhuma flag
        FeatureFlag.objects.all().delete()

        arquivo = SimpleUploadedFile(
            "contrato.pdf",
            b"%PDF-1.4 fake content for test",
            content_type="application/pdf"
        )
        
        with patch('core.tasks.processarContratoComIa.delay') as mock_delay:
            response = api_client.post(
                f"/processo/{processo.id}/contrato/",
                {"arquivo": arquivo},
                format="multipart"
            )
            assert response.status_code == 201
            mock_delay.assert_not_called()
