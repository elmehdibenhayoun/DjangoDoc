# Generated by Django 5.0 on 2023-12-29 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0002_selectedgraphtype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='selectedgraphtype',
            name='graph_type',
            field=models.CharField(choices=[('1', 'Line Plot'), ('2', 'Scatter Plot'), ('3', 'Box Plot'), ('4', 'Histogram'), ('5', 'KDE Plot'), ('6', 'Violin Plot'), ('7', 'Bar Plot'), ('8', 'Heatmap'), ('9', 'Pie Chart')], max_length=10),
        ),
    ]
