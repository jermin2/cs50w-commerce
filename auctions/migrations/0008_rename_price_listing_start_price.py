# Generated by Django 3.2.7 on 2021-09-05 07:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0007_alter_bid_listing'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listing',
            old_name='price',
            new_name='start_price',
        ),
    ]
