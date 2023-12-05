from django.db import models

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')

class SelectedGraphType(models.Model):
    GRAPH_TYPE_CHOICES = [
        ('1', 'Line Plot'),
        ('2', 'Scatter Plot'),
        ('3', 'Box Plot'),
        ('4', 'Histogram'),
        ('5', 'KDE Plot'),
        ('6', 'Violin Plot'),
        ('7', 'Bar Plot'),
        ('8', 'Heatmap'),
        ('9', 'Pie Chart'),
    ]

    graph_type = models.CharField(max_length=10, choices=GRAPH_TYPE_CHOICES)

    def __str__(self):
        return self.graph_type