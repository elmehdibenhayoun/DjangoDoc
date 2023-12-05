from django import forms
from .models import SelectedGraphType, UploadedFile
from django.core.validators import FileExtensionValidator

class FileUploadForm(forms.ModelForm):
    # Add hidden input fields to store selected column name and graph type
    selected_column_name1 = forms.CharField(widget=forms.HiddenInput(), required=False)
    selected_column_name2 = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = UploadedFile
        fields = ['file']


class GraphTypeForm(forms.Form):
    # Form for selecting the graph type
    selected_graph_type = forms.ChoiceField(choices=[('bar', 'Bar Chart'), ('line', 'Line Chart')])  