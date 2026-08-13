import json

import pytest
import requests

from instructions.models import OfficialInstruction
from instructions.parsing import (
    check_grls_instruction_update,
    check_official_instruction_update,
    compute_hash,
    extract_grls_id_reg,
    extract_text,
    fetch_grls_instruction_images,
    pick_latest_grls_image,
)

pytestmark = pytest.mark.django_db

GRLS_URL_REV_0 = 'https://grls.rosminzdrav.ru/InstrImg/2026/04/20/1528863/6ef85a9b-old.pdf'
GRLS_URL_REV_1 = 'https://grls.rosminzdrav.ru/InstrImg/2026/07/01/1528863/aaaa1111-new.pdf'


class FakeResponse:
    """Заглушка ответа requests для тестов без реальной сети."""

    def __init__(self, content: bytes, content_type: str = 'text/html'):
        """Сохраняет тело и content-type фиктивного ответа."""
        self.content = content
        self.headers = {'Content-Type': content_type}

    def raise_for_status(self):
        pass


class FakeGrlsDiscoveryResponse:
    """Заглушка ответа веб-метода GRLS_View_V2.aspx/AddInstrImg."""

    def __init__(self, payload: dict):
        """Оборачивает payload так же, как ASP.NET ScriptMethod — строкой в поле 'd'."""
        self._body = {'d': json.dumps(payload, ensure_ascii=False)}

    def raise_for_status(self):
        pass

    def json(self):
        return self._body


def grls_payload(*images: dict) -> dict:
    """Собирает тело ответа ГРЛС с переданными образами инструкции."""
    return {'Sources': [{'SourceName': 'GRLS', 'Instructions': [{'Images': list(images)}]}]}


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


def test_extract_grls_id_reg_from_instrimg_url():
    """Из ссылки на файл ГРЛС достаётся числовой idReg из пути."""
    assert extract_grls_id_reg(GRLS_URL_REV_0) == '1528863'


def test_extract_grls_id_reg_returns_none_for_non_grls_url():
    """Ссылка, не похожая на /InstrImg/.../<idReg>/..., не даёт idReg."""
    assert extract_grls_id_reg('https://grls.rosminzdrav.ru/instruction/pentaxim') is None


def test_fetch_grls_instruction_images_parses_and_filters(monkeypatch):
    """Разбирает ответ ГРЛС: нормализует слэши, добавляет домен, отсекает не-PDF образы."""
    payload = grls_payload(
        {'Url': '\\InstrImg\\2026\\04\\20\\1528863\\old.pdf', 'Label': 'Изм. № 0'},
        {'Url': '\\InstrImg\\2026\\04\\20\\1528863\\scan.jpg', 'Label': 'Скан упаковки'},
    )
    monkeypatch.setattr(
        'instructions.parsing.requests.post',
        lambda *args, **kwargs: FakeGrlsDiscoveryResponse(payload),
    )

    images = fetch_grls_instruction_images('1528863')

    assert images == [
        {'url': 'https://grls.rosminzdrav.ru/InstrImg/2026/04/20/1528863/old.pdf', 'label': 'Изм. № 0'},
    ]


def test_pick_latest_grls_image_returns_max_revision():
    """Из нескольких редакций выбирается образ с наибольшим номером «Изм. №»."""
    images = [
        {'url': GRLS_URL_REV_0, 'label': 'Изм. № 0, ЛП-№(014031)-(РГ-RU), 2026'},
        {'url': GRLS_URL_REV_1, 'label': 'Изм. № 1, ЛП-№(014031)-(РГ-RU), 2026'},
    ]

    latest = pick_latest_grls_image(images)

    assert latest['url'] == GRLS_URL_REV_1


def test_check_grls_instruction_update_returns_none_for_non_grls_url():
    """Для ссылки без определяемого idReg discovery не запускается."""
    instruction = create_official_instruction(url='https://grls.rosminzdrav.ru/instruction/pentaxim')

    assert check_grls_instruction_update(instruction) is None


def test_check_grls_instruction_update_detects_new_revision(monkeypatch):
    """Новый URL из discovery заменяет старый, снэпшот обновляется, взводится has_update."""
    instruction = create_official_instruction(url=GRLS_URL_REV_0, content_hash=compute_hash('Старый текст'))
    payload = grls_payload(
        {'Url': GRLS_URL_REV_0.replace('https://grls.rosminzdrav.ru', ''), 'Label': 'Изм. № 0'},
        {'Url': GRLS_URL_REV_1.replace('https://grls.rosminzdrav.ru', ''), 'Label': 'Изм. № 1'},
    )
    monkeypatch.setattr(
        'instructions.parsing.requests.post',
        lambda *args, **kwargs: FakeGrlsDiscoveryResponse(payload),
    )
    monkeypatch.setattr(
        'instructions.parsing.requests.get',
        lambda *args, **kwargs: FakeResponse(b'%PDF-fake'),
    )
    monkeypatch.setattr(
        'instructions.parsing.extract_text_from_pdf',
        lambda content: 'Новый текст редакции 1',
    )

    changed = check_grls_instruction_update(instruction)

    instruction.refresh_from_db()
    assert changed is True
    assert instruction.url == GRLS_URL_REV_1
    assert instruction.parsed_text == 'Новый текст редакции 1'
    assert instruction.has_update is True


def test_check_grls_instruction_update_no_change_when_url_matches(monkeypatch):
    """Если discovery возвращает тот же URL, обновление не фиксируется."""
    instruction = create_official_instruction(url=GRLS_URL_REV_0)
    payload = grls_payload(
        {'Url': GRLS_URL_REV_0.replace('https://grls.rosminzdrav.ru', ''), 'Label': 'Изм. № 0'},
    )
    monkeypatch.setattr(
        'instructions.parsing.requests.post',
        lambda *args, **kwargs: FakeGrlsDiscoveryResponse(payload),
    )

    changed = check_grls_instruction_update(instruction)

    instruction.refresh_from_db()
    assert changed is False
    assert instruction.has_update is False
    assert instruction.last_checked_at is not None


def test_check_official_instruction_update_prefers_grls_discovery(monkeypatch):
    """Основная функция сверки использует discovery для ссылок ГРЛС вместо хэша по старому URL."""
    instruction = create_official_instruction(url=GRLS_URL_REV_0)
    payload = grls_payload(
        {'Url': GRLS_URL_REV_1.replace('https://grls.rosminzdrav.ru', ''), 'Label': 'Изм. № 1'},
    )
    monkeypatch.setattr(
        'instructions.parsing.requests.post',
        lambda *args, **kwargs: FakeGrlsDiscoveryResponse(payload),
    )
    monkeypatch.setattr(
        'instructions.parsing.requests.get',
        lambda *args, **kwargs: FakeResponse(b'%PDF-fake'),
    )
    monkeypatch.setattr(
        'instructions.parsing.extract_text_from_pdf',
        lambda content: 'Новый текст',
    )

    changed = check_official_instruction_update(instruction)

    instruction.refresh_from_db()
    assert changed is True
    assert instruction.url == GRLS_URL_REV_1
