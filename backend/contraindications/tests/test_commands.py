import pytest
from openpyxl import Workbook
import tempfile
import os

from django.core.management import call_command

from contraindications.models import Contraindication


def make_excel_file(sheets: dict):
    wb = Workbook()
    wb.remove(wb.active)

    for sheet_name, rows in sheets.items():
        ws = wb.create_sheet(sheet_name)
        for row in rows:
            ws.append(row)
    return wb

@pytest.fixture
def contraindication_simple_excel_file():
    wb = make_excel_file({
        'contraindications_list': [
        ['contraindication_ID', 'contraindication_name'],
        [1, 'диарея'],
        [2, 'рвота'],
    ],
    })
    tmp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    path = tmp_file.name
    tmp_file.close()

    wb.save(path)

    yield path

    os.remove(path)

@pytest.fixture
def contraindication_incorrect_excel_file():
    wb = make_excel_file({
        'contraindications_list': [
        ['contraindication_ID', 'contraindication_name'],
        [1, 'диарея'],
        [2, None],
    ],
    })
    tmp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    path = tmp_file.name
    tmp_file.close()

    wb.save(path)

    yield path

    os.remove(path)

@pytest.fixture
def contraindication_full_excel_file():
    wb = make_excel_file({
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
            [3, 'Гепатит']
        ],
    })

    tmp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    path = tmp_file.name
    tmp_file.close()

    wb.save(path)

    yield path

    os.remove(path)


@pytest.mark.django_db
def test_import_contraindications(contraindication_simple_excel_file):
    call_command(
        'import_contraindications', contraindication_simple_excel_file)

    assert Contraindication.objects.count() == 2

@pytest.mark.django_db
def test_import_contraindications_twice(contraindication_simple_excel_file):
    call_command(
        'import_contraindications', contraindication_simple_excel_file)
    call_command(
        'import_contraindications', contraindication_simple_excel_file)
    assert Contraindication.objects.count() == 2

@pytest.mark.django_db
def test_correct_contraindications_names(contraindication_simple_excel_file):
    call_command(
        'import_contraindications', contraindication_simple_excel_file)
    assert Contraindication.objects.first().name == 'диарея'

@pytest.mark.django_db
def test_import_contraindications(contraindication_incorrect_excel_file):
    with pytest.raises(Exception):
        call_command(
            'import_contraindications', contraindication_incorrect_excel_file)

def test_import_contraindications_complicated(
    contraindication_full_excel_file):
    call_command(
        'import_contraindications', contraindication_full_excel_file)
    assert Contraindication.objects.count() == 2