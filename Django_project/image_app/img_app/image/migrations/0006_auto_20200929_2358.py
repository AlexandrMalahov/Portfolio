# Generated by Django 3.1.1 on 2020-09-29 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('image', '0005_auto_20200929_2312'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagecomment',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
