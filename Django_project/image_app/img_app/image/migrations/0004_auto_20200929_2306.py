# Generated by Django 3.1.1 on 2020-09-29 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('image', '0003_auto_20200929_0048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagecomment',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]