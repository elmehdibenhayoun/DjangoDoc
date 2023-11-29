from django.urls import path
from .views import upload_file, uploaded

urlpatterns = [
    path('upload/', upload_file, name='upload_file'),
    path('uploaded/', uploaded, name='uploaded'),
]
