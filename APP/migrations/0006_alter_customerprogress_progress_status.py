# Generated by Django 4.2.1 on 2023-06-02 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('APP', '0005_customer_customer_level_alter_customer_customer_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerprogress',
            name='progress_status',
            field=models.IntegerField(choices=[(1, ''), (2, ''), (3, '完成')], default=1),
        ),
    ]
