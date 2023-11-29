from django.db import models

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
class SelectedGraphType(models.Model):
    GRAPH_TYPE_CHOICES = [
        ('bar', 'Bar Chart'),
        ('pie', 'Pie Chart'),
        # Add more chart types as needed
    ]

    graph_type = models.CharField(max_length=10, choices=GRAPH_TYPE_CHOICES)

    def __str__(self):
        return self.graph_type