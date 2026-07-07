import os
import tempfile

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from openpyxl import Workbook

from contraindications.models import Contraindication


def make_excel_file(sheets: dict):
    """Создает Excel-файл."""
    wb = Workbook()
    wb.remove(wb.active)

    for sheet_name, rows in sheets.items():
        ws = wb.create_sheet(sheet_name)
        for row in rows:
            ws.append(row)
    return wb


@pytest.fixture
def contraindication_simple_excel_file():
    """Создает упрощенный Excel-файл с одним листом."""
    wb = make_excel_file(
        {
            'contraindications_list': [
                ['contraindication_ID', 'contraindication_name'],
                [1, 'диарея'],
                [2, 'рвота'],
            ],
        }
    )
    tmp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    path = tmp_file.name
    tmp_file.close()

    wb.save(path)

    yield path

    os.remove(path)


@pytest.fixture
def contraindication_update():
    """Создает упрощенный Excel-файл с обновленными данными."""
    wb = make_excel_file(
        {
            'contraindications_list': [
                ['contraindication_ID', 'contraindication_name'],
                [1, 'острая диарея'],
                [2, 'непрекращающася рвота'],
            ],
        }
    )
    tmp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    path = tmp_file.name
    tmp_file.close()

    wb.save(path)

    yield path

    os.remove(path)


@pytest.fixture
def contraindication_incorrect_excel_file():
    """Создает некорректный файл."""
    wb = make_excel_file(
        {
            'contraindications_list': [
                ['contraindication_ID', 'contraindication_name'],
                [1, 'диарея'],
                [2, None],
            ],
        }
    )
    tmp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    path = tmp_file.name
    tmp_file.close()

    wb.save(path)

    yield path

    os.remove(path)


@pytest.fixture
def contraindication_double_old_id():
    """Создает файл с дублирующимся ID."""
    wb = make_excel_file(
        {
            'contraindications_list': [
                ['contraindication_ID', 'contraindication_name'],
                [1, 'диарея'],
                [2, 'рвота'],
                [2, 'ВИЧ'],
            ],
        }
    )
    tmp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    path = tmp_file.name
    tmp_file.close()

    wb.save(path)

    yield path

    os.remove(path)


@pytest.fixture
def contraindication_no_sheet():
    """Создает упрощенный Excel-файл с одним листом."""
    wb = make_excel_file(
        {
            'Sheet1': [
                ['contraindication_ID', 'contraindication_name'],
                [1, 'диарея'],
                [2, 'рвота'],
            ],
        }
    )
    tmp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    path = tmp_file.name
    tmp_file.close()

    wb.save(path)

    yield path

    os.remove(path)


@pytest.fixture
def contraindication_wrong_column():
    """Создает упрощенный Excel-файл с одним листом."""
    wb = make_excel_file(
        {
            'contraindications_list': [
                ['contraindication_ID', 'name'],
                [1, 'диарея'],
                [2, 'рвота'],
            ],
        }
    )
    tmp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    path = tmp_file.name
    tmp_file.close()

    wb.save(path)

    yield path

    os.remove(path)


@pytest.fixture
def contraindication_full_excel_file():
    """Создает близкий к реальности сложный файл."""
    wb = make_excel_file(
        {
            'contraindications_list': [
                ['contraindication_ID', 'contraindication_name'],
                [1, 'диарея'],
                [2, 'рвота'],
            ],
            'other_sheet': [
                ['vaccine_ID', 'contraindication_ID'],
                [1, 1],
                [2, 2],
            ],
            'double_list': [
                ['contraindication_ID', 'contraindication_name'],
                [1, ',беременность'],
                [2, 'ВИЧ'],
                [3, 'гепатит'],
            ],
        }
    )

    tmp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    path = tmp_file.name
    tmp_file.close()

    wb.save(path)

    yield path

    os.remove(path)


@pytest.mark.django_db
def test_import_contraindications(contraindication_simple_excel_file):
    """Проверяет, что корректный файл загружается."""
    call_command('import_contraindications', contraindication_simple_excel_file)

    assert Contraindication.objects.count() == 2

    contraindication = Contraindication.objects.get(old_id=1)
    assert contraindication.name == 'диарея'


@pytest.mark.django_db
def test_import_contraindications_twice(contraindication_simple_excel_file):
    """Проверяет, что при повторной загрузке количество записей не меняется."""
    call_command('import_contraindications', contraindication_simple_excel_file)
    call_command('import_contraindications', contraindication_simple_excel_file)
    assert Contraindication.objects.count() == 2


@pytest.mark.django_db
def test_import_updates_names(contraindication_simple_excel_file, contraindication_update):
    """Проверяет, что при обновлении меняется название противопоказания."""
    call_command('import_contraindications', contraindication_simple_excel_file)
    call_command('import_contraindications', contraindication_update)
    assert Contraindication.objects.count() == 2
    contraindication = Contraindication.objects.get(old_id=1)
    assert contraindication.name == 'острая диарея'


@pytest.mark.django_db
def test_import_contraindications_incorrect_file(contraindication_incorrect_excel_file):
    """Проверяет, что при загрузке файла с некорректными данными выпадает ошибка."""
    with pytest.raises(CommandError):
        call_command('import_contraindications', contraindication_incorrect_excel_file)


@pytest.mark.django_db
def test_import_contraindications_double_id(contraindication_double_old_id):
    """Проверяет, что при загрузке файла с дублирующимся ID выпадает ошибка."""
    with pytest.raises(CommandError):
        call_command('import_contraindications', contraindication_double_old_id)


@pytest.mark.django_db
def test_import_contraindications_transaction_works(contraindication_double_old_id):
    """Проверяет, что при ошибке импорт полностью откатывается."""
    with pytest.raises(CommandError):
        call_command(
            'import_contraindications',
            contraindication_double_old_id,
        )
    assert Contraindication.objects.count() == 0


@pytest.mark.django_db
def test_import_contraindications_wrong_sheet_name(contraindication_no_sheet):
    """Проверяет, что при загрузке файла с неправильным названием листа выпадает ошибка."""
    with pytest.raises(CommandError):
        call_command('import_contraindications', contraindication_no_sheet)


@pytest.mark.django_db
def test_import_contraindications_wrong_column_name(contraindication_wrong_column):
    """Проверяет, что при загрузке файла с неправильным названием колонки выпадает ошибка."""    
    with pytest.raises(CommandError):
        call_command('import_contraindications', contraindication_wrong_column)


@pytest.mark.django_db
def test_import_ignores_other_sheets(contraindication_full_excel_file):
    """Проверяет, что сложный файл загружается корректно."""
    call_command('import_contraindications', contraindication_full_excel_file)
    assert Contraindication.objects.count() == 2
    contraindication = Contraindication.objects.get(old_id=1)
    assert contraindication.name == 'диарея'
