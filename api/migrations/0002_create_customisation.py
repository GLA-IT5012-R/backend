# api/migrations/0002_create_customisation.py
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customisation',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('user_id', models.BigIntegerField(help_text='用户ID')),
                ('p_size', models.CharField(max_length=50, blank=True, help_text='用户选择尺寸，例如 160')),
                ('p_finish', models.CharField(max_length=50, blank=True, help_text='板面工艺')),
                ('p_flex', models.CharField(max_length=50, blank=True, help_text='软硬度')),
                ('p_textures', models.JSONField(default=list, blank=True, help_text='用户选择纹理，可能多个，存 JSON')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='customisations',
                    to='api.product'
                )),
            ],
            options={
                'db_table': 'customisations',
            },
        ),
    ]
