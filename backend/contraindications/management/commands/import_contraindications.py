from openpyxl import load_workbook

from django.core.management.base import BaseCommand

from contraindications.models import Contraindication


class Command(BaseCommand):
    help = ('Импортирует противопоказания из указанного excel-файла '
            'со страницы contraindications_list')

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Путь к excel-файлу')

    def handle(self, *args, **options):
        file_path = options['excel_file']
        try:
            wb = load_workbook(file_path, read_only=True)
            ws = wb['contraindications_list']
            headers = [cell.value for cell in next(
                ws.iter_rows(min_row=1, max_row=1))]
            name_idx = headers.index('contraindication_name')
        except Exception as e:
            self.stderr.write(f'Ошибка при чтении файла: {e}')
            return
        name_count = 0
        try:
            for row in ws.iter_rows(min_row=2, values_only=True):
                contraindication_name = row[name_idx]
                _, created = Contraindication.objects.get_or_create(
                    name = contraindication_name)
                if created:
                    self.stdout.write(
                        f'Создано противопоказание "{contraindication_name}"')
                    name_count += 1
                else:
                    self.stdout.write(
                        f'Противопоказание "{contraindication_name}" '
                        'уже существует')
        except Exception as e:
            self.stderr.write(f'Ошибка при загрузке противопоказаний: {e}')
            return

        self.stdout.write(
            f'Импорт противопоказаний завершён. Добавлено {name_count} штук.')
        wb.close()
