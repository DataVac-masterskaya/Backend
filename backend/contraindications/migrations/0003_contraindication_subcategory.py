from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contraindications', '0002_alter_contraindication_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='contraindication',
            name='subcategory',
            field=models.CharField(
                blank=True,
                max_length=255,
                null=True,
                verbose_name='Подкатегория',
            ),
        ),
    ]
