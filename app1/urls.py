from django.urls import path
from .views import upload_file, uploaded

urlpatterns = [
    path('', upload_file, name='upload_file'),
    path('uploaded/', uploaded, name='uploaded'),
]
