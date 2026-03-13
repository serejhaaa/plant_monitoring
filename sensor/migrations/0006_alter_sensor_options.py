# Migration created on server by makemigrations - added to repo for merge
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sensor', '0005_extend_models'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sensor',
            options={'ordering': ['board', 'sensor_model']},
        ),
    ]
