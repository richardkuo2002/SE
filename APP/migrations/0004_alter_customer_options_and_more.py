# Generated by Django 4.2.1 on 2023-06-02 05:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('APP', '0003_alter_branch_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'verbose_name': '顧客', 'verbose_name_plural': '顧客'},
        ),
        migrations.AlterModelOptions(
            name='customerprogress',
            options={'verbose_name': '客戶進度', 'verbose_name_plural': '客戶進度'},
        ),
        migrations.AlterModelOptions(
            name='profit',
            options={'verbose_name': '毛利', 'verbose_name_plural': '毛利'},
        ),
        migrations.AlterModelOptions(
            name='sale',
            options={'verbose_name': '銷量', 'verbose_name_plural': '銷量'},
        ),
        migrations.AlterModelOptions(
            name='salesperson',
            options={'verbose_name': '業務員', 'verbose_name_plural': '業務員'},
        ),
    ]
