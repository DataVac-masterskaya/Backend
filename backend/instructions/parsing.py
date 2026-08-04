import hashlib
import logging
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


def check_official_instruction_update(instruction: OfficialInstruction) -> bool:
    """Сверяет текст инструкции с источником, обновляет снэпшот. Возвращает True, если по сравнению с предыдущим успешным снэпшотом обнаружено изменение текста."""
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
