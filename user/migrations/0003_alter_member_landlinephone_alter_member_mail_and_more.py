# Generated by Django 4.1.5 on 2023-06-27 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_alter_member_borrowerphoto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='landlinePhone',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='mail',
            field=models.EmailField(max_length=254, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='phone',
            field=models.IntegerField(null=True, unique=True),
        ),
    ]
