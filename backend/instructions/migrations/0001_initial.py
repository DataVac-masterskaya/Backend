# Миграция вручную создана для справочника официальных инструкций.

from django.db import migrations, models


class Migration(migrations.Migration):
    """Создает таблицу официальных инструкций."""

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='OfficialInstruction',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('title', models.CharField(max_length=255, unique=True)),
                ('url', models.URLField(max_length=500, unique=True)),
                ('source', models.CharField(default='ГРЛС', max_length=255)),
                ('description', models.TextField(blank=True)),
                ('search_select_count', models.PositiveBigIntegerField(default=0)),
                (
                    'search_weight',
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=10,
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Official instruction',
                'verbose_name_plural': 'Official instructions',
                'db_table': 'official_instructions',
                'ordering': ['title'],
            },
        ),
    ]
