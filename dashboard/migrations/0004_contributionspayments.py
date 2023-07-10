# Generated by Django 4.1.5 on 2023-06-28 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_alter_member_landlinephone_alter_member_mail_and_more'),
        ('dashboard', '0003_total_amount'),
    ]

    operations = [
        migrations.CreateModel(
            name='contributionsPayments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accountReference', models.CharField(max_length=50)),
                ('paidAmount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('paymentDate', models.DateField()),
                ('transactionId', models.CharField(max_length=150, unique=True)),
                ('contributor', models.ManyToManyField(to='user.member')),
            ],
        ),
    ]
