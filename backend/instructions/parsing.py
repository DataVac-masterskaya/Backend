import hashlib
import json
import logging
import re
from io import BytesIO

import requests
from bs4 import BeautifulSoup
from django.utils import timezone
from pypdf import PdfReader

from instructions.models import OfficialInstruction

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 20
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; DataVacInstructionBot/1.0; +https://datavac.ru)',
}
NOISE_TAGS = ('script', 'style', 'nav', 'header', 'footer')

GRLS_BASE_URL = 'https://grls.rosminzdrav.ru'
GRLS_DISCOVERY_URL = f'{GRLS_BASE_URL}/GRLS_View_V2.aspx/AddInstrImg'
GRLS_ID_REG_RE = re.compile(r'/InstrImg/\d+/\d+/\d+/(\d+)/', re.IGNORECASE)
GRLS_REVISION_RE = re.compile(r'Изм\.\s*№\s*(\d+)')


def fetch_source_content(url: str) -> tuple[bytes, str]:
    """Скачивает страницу/файл по сохранённому URL источника (ГРЛС/ОХЛП)."""
    response = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    content_type = response.headers.get('Content-Type', '')
    return response.content, content_type


def extract_text(content: bytes, content_type: str, url: str) -> str:
    """Извлекает читаемый текст инструкции из ответа источника."""
    if 'pdf' in content_type.lower() or url.lower().endswith('.pdf'):
        return extract_text_from_pdf(content)
    return extract_text_from_html(content)


def extract_text_from_pdf(content: bytes) -> str:
    """Извлекает текстовое содержимое из PDF-файла."""
    reader = PdfReader(BytesIO(content))
    pages_text = (page.extract_text() or '' for page in reader.pages)
    return '\n'.join(text.strip() for text in pages_text if text.strip())


def extract_text_from_html(content: bytes) -> str:
    """Извлекает текстовое содержимое из HTML-страницы, удаляя шумовые теги."""
    soup = BeautifulSoup(content, 'lxml')
    for tag in soup.find_all(NOISE_TAGS):
        tag.decompose()
    return soup.get_text(separator='\n', strip=True)


def compute_hash(text: str) -> str:
    """Возвращает sha256 текста инструкции для сверки на изменения."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def extract_grls_id_reg(url: str) -> str | None:
    """Достаёт внутренний идентификатор регистрации (idReg) из ссылки ГРЛС на файл инструкции."""
    match = GRLS_ID_REG_RE.search(url)
    return match.group(1) if match else None


def fetch_grls_instruction_images(id_reg: str) -> list[dict]:
    """Запрашивает у ГРЛС актуальный список файлов инструкции по idReg.

    Повторяет запрос, который на сайте делает кнопка «Показать инструкции»
    (веб-метод GRLS_View_V2.aspx/AddInstrImg). regNumber сервером не проверяется,
    поэтому не передаём его, чтобы не возиться с кодировкой кириллицы.
    """
    response = requests.post(
        GRLS_DISCOVERY_URL,
        json={'regNumber': '', 'idReg': id_reg},
        headers=REQUEST_HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    payload = json.loads(response.json()['d'])

    images = []
    for source in payload.get('Sources') or []:
        for instr in source.get('Instructions') or []:
            for image in instr.get('Images') or []:
                image_url = image.get('Url') or ''
                if '.pdf' not in image_url.lower():
                    continue
                images.append({
                    'url': GRLS_BASE_URL + image_url.replace('\\', '/'),
                    'label': image.get('Label') or '',
                })
    return images


def pick_latest_grls_image(images: list[dict]) -> dict | None:
    """Возвращает образ с максимальным номером «Изм. №» — последнюю редакцию инструкции."""

    def revision_number(image: dict) -> int:
        match = GRLS_REVISION_RE.search(image['label'])
        return int(match.group(1)) if match else -1

    return max(images, key=revision_number, default=None)


def check_grls_instruction_update(instruction: OfficialInstruction) -> bool | None:
    """Сверяет инструкцию ГРЛС через discovery-метод сайта, а не по хэшу PDF.
    """
    id_reg = extract_grls_id_reg(instruction.url)
    if not id_reg:
        return None

    try:
        images = fetch_grls_instruction_images(id_reg)
    except (requests.RequestException, ValueError, KeyError) as exc:
        logger.warning('ГРЛС discovery не удался для инструкции #%s: %s', instruction.pk, exc)
        return None

    latest = pick_latest_grls_image(images)
    if latest is None:
        return None

    if latest['url'] == instruction.url:
        instruction.last_checked_at = timezone.now()
        instruction.save(update_fields=['last_checked_at'])
        return False

    try:
        content, content_type = fetch_source_content(latest['url'])
        text = extract_text(content, content_type, latest['url'])
    except (requests.RequestException, ValueError) as exc:
        logger.warning(
            'Не удалось скачать новую редакцию инструкции #%s (%s): %s', instruction.pk, latest['url'], exc,
        )
        return None

    instruction.url = latest['url']
    instruction.parsed_text = text
    instruction.content_hash = compute_hash(text)
    instruction.last_checked_at = timezone.now()
    instruction.has_update = True
    instruction.save(update_fields=['url', 'parsed_text', 'content_hash', 'last_checked_at', 'has_update'])
    return True


def check_official_instruction_update(instruction: OfficialInstruction) -> bool:
    """Сверяет инструкцию с источником, обновляет снэпшот.
    """
    grls_result = check_grls_instruction_update(instruction)
    if grls_result is not None:
        return grls_result

    try:
        content, content_type = fetch_source_content(instruction.url)
        text = extract_text(content, content_type, instruction.url)
    except (requests.RequestException, ValueError) as exc:
        logger.warning('Не удалось проверить инструкцию #%s (%s): %s', instruction.pk, instruction.url, exc)
        return False

    new_hash = compute_hash(text)
    is_changed = bool(instruction.content_hash) and new_hash != instruction.content_hash

    instruction.parsed_text = text
    instruction.content_hash = new_hash
    instruction.last_checked_at = timezone.now()
    if is_changed:
        instruction.has_update = True
    instruction.save(update_fields=['parsed_text', 'content_hash', 'last_checked_at', 'has_update'])

    return is_changed
