# Generated by Django 4.2.1 on 2023-06-14 07:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('APP', '0019_delete_branch_remove_product_category_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BRANCH',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('Name', models.CharField(max_length=100)),
                ('Address', models.CharField(max_length=100)),
                ('District', models.IntegerField(choices=[(1, '北區'), (2, '中區'), (3, '南區')], default=1)),
            ],
            options={
                'verbose_name': '分店',
                'verbose_name_plural': '分店',
            },
        ),
        migrations.CreateModel(
            name='CUSTOMER',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('Name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': '顧客',
                'verbose_name_plural': '顧客',
            },
        ),
        migrations.CreateModel(
            name='PRODUCT',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('Cost', models.DecimalField(decimal_places=0, max_digits=10)),
                ('Purchase_Date', models.DateField(db_index=True)),
                ('State', models.IntegerField(choices=[(1, '庫存'), (2, '已售出'), (3, '體驗椅')], default=1)),
            ],
            options={
                'verbose_name': '產品',
                'verbose_name_plural': '產品',
            },
        ),
        migrations.CreateModel(
            name='PRODUCT_MODEL',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('Name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': '產品型號',
                'verbose_name_plural': '產品型號',
            },
        ),
        migrations.CreateModel(
            name='SELLER',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('Name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': '銷售員',
                'verbose_name_plural': '銷售員',
            },
        ),
        migrations.CreateModel(
            name='SALE',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('Selling_Price', models.DecimalField(decimal_places=0, max_digits=10)),
                ('Sale_Date', models.DateField(db_index=True)),
                ('Customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='APP.customer')),
                ('Product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='APP.product')),
                ('Seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='APP.seller')),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='APP.branch')),
            ],
            options={
                'verbose_name': '銷售',
                'verbose_name_plural': '銷售',
            },
        ),
        migrations.CreateModel(
            name='PUBLIC_MASSAGE_CHAIR',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('Date', models.DateField(db_index=True)),
                ('Customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='APP.customer')),
                ('Seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='APP.seller')),
            ],
            options={
                'verbose_name': '按摩椅體驗',
                'verbose_name_plural': '按摩椅體驗',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='Category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='APP.product_model'),
        ),
    ]
