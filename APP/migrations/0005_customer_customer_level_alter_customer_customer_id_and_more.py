# Generated by Django 4.2.1 on 2023-06-02 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('APP', '0004_alter_customer_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='customer_level',
            field=models.IntegerField(choices=[(1, '普通會員'), (2, '高级會員'), (3, 'VIP會員')], default=1),
        ),
        migrations.AlterField(
            model_name='customer',
            name='customer_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='customerprogress',
            name='progress_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='profit',
            name='profit_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='sale',
            name='sale_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='salesperson',
            name='salesperson_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
