# Generated by Django 2.1.5 on 2019-02-17 02:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oikos', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='miband',
            name='user',
        ),
        migrations.DeleteModel(
            name='MibandEntry',
        ),
        migrations.RemoveField(
            model_name='localservices',
            name='miband',
        ),
        migrations.RemoveField(
            model_name='wifi',
            name='on_boot',
        ),
        migrations.DeleteModel(
            name='Miband',
        ),
    ]