import pytest
import requests

from instructions.models import OfficialInstruction
from instructions.parsing import check_official_instruction_update, compute_hash, extract_text

pytestmark = pytest.mark.django_db


class FakeResponse:
    """Заглушка ответа requests для тестов без реальной сети."""

    def __init__(self, content: bytes, content_type: str = 'text/html'):
        """Сохраняет тело и content-type фиктивного ответа."""
        self.content = content
        self.headers = {'Content-Type': content_type}

    def raise_for_status(self):
        pass


def create_official_instruction(**kwargs):
    """Создает тестовую официальную инструкцию."""
    defaults = {
        'title': 'Инструкция Пентаксим',
        'url': 'https://grls.rosminzdrav.ru/instruction/pentaxim',
    }
    defaults.update(kwargs)
    return OfficialInstruction.objects.create(**defaults)


def test_extract_text_strips_noise_tags():
    """Скрипты/навигация вырезаются, текст контента остаётся."""
    html = '<html><body><nav>Меню</nav><script>x</script><p>Показания.</p></body></html>'.encode()

    text = extract_text(html, 'text/html', 'https://example.com/page')

    assert 'Показания.' in text
    assert 'Меню' not in text


def test_check_official_instruction_update_detects_change(monkeypatch):
    """Изменившийся текст источника взводит has_update и обновляет снэпшот."""
    instruction = create_official_instruction(content_hash=compute_hash('Старый текст'), parsed_text='Старый текст')
    monkeypatch.setattr(
        'instructions.parsing.requests.get',
        lambda *args, **kwargs: FakeResponse('<p>Новый текст</p>'.encode()),
    )

    changed = check_official_instruction_update(instruction)

    instruction.refresh_from_db()
    assert changed is True
    assert instruction.has_update is True
    assert instruction.parsed_text == 'Новый текст'


def test_check_official_instruction_update_first_check_does_not_flag(monkeypatch):
    """Первая проверка (пустой content_hash) только сохраняет снэпшот, без флага."""
    instruction = create_official_instruction()
    monkeypatch.setattr(
        'instructions.parsing.requests.get',
        lambda *args, **kwargs: FakeResponse('<p>Текст</p>'.encode()),
    )

    changed = check_official_instruction_update(instruction)

    instruction.refresh_from_db()
    assert changed is False
    assert instruction.has_update is False


def test_check_official_instruction_update_network_error_is_swallowed(monkeypatch):
    """Сетевая ошибка логируется и не всплывает наружу; last_checked_at не трогается."""
    instruction = create_official_instruction()

    def raise_error(*args, **kwargs):
        raise requests.ConnectionError('boom')

    monkeypatch.setattr('instructions.parsing.requests.get', raise_error)

    changed = check_official_instruction_update(instruction)

    instruction.refresh_from_db()
    assert changed is False
    assert instruction.last_checked_at is None
