# Миграция вручную создана для модуля справочника противопоказаний.

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ContraindicationCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'Contraindication category',
                'verbose_name_plural': 'Contraindication categories',
                'db_table': 'contraindication_categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Contraindication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('search_select_count', models.PositiveBigIntegerField(default=0)),
                ('search_weight', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                (
                    'categories',
                    models.ManyToManyField(
                        blank=True,
                        db_table='contraindication_categories_contraindications',
                        related_name='contraindications',
                        to='contraindications.contraindicationcategory',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Contraindication',
                'verbose_name_plural': 'Contraindications',
                'db_table': 'contraindications',
                'ordering': ['name'],
            },
        ),
    ]
