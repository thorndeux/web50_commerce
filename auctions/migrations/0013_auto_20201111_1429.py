# Generated by Django 2.2.12 on 2020-11-11 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0012_auto_20201106_2044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='startingBid',
            field=models.ForeignKey(on_delete=models.SET('deleted'), related_name='startingBid', to='auctions.Bid'),
        ),
    ]