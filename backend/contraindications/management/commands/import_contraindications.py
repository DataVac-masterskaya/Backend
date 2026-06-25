import pandas as pd
from django.core.management.base import BaseCommand

from contraindications.models import Contraindication


class Command(BaseCommand):
    help = ('Импортирует противопоказания из excel-файла ', 'со страницы contraindications_list')

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Путь к excel-файлу')

    def handle(self, *args, **options):
        file_path = options['excel_file']
        try:
            df = pd.read_excel(file_path, sheet_name='contraindications_list')
        except Exception as e:
            self.stderr.write(f'Ошибка при чтении файла: {e}')
            return

        self.stdout.write(
            f'Файл {file_path} успешно прочитан. Строк: {len(df)}')

        for _, row in df.iterrows():
            contraindication_id = row['contraindication_id']
            contraindication_name = row['contraindication_name']
            # contraindication_long_name = row['contraindication_long_name']

            contraindication, created = Contraindication.objects.get_or_create(
                id=contraindication_id,
                defaults={
                    'name': contraindication_name,
                },
            )
            if not created:
                contraindication.name = contraindication_name
                contraindication.save()
                self.stdout.write(f'Обновлено противопоказание {contraindication_id}')
            else:
                self.stdout.write(f'Создано противопоказание {contraindication_id}')

        self.stdout.write('Импорт противопоказаний завершён.')
