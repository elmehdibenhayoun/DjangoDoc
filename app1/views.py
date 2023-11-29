from django.shortcuts import render, redirect
from .forms import FileUploadForm
import pandas as pd
import os
import matplotlib.pyplot as plt
from django.conf import settings
from io import BytesIO
import base64
import seaborn as sns

def upload_file(request):
    global df
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save()

            file_extension = instance.file.name.split('.')[-1].lower()
            if file_extension == 'csv':
                df = pd.read_csv(instance.file, delimiter=',')
            elif file_extension == 'json':
                df = pd.read_json(instance.file)
            elif file_extension == 'xlsx':
                df = pd.read_excel(instance.file)
            else:
                os.remove(instance.file.path)
                return redirect('uploaded')

            # Store data in the session
            request.session['column_names'] = df.columns.tolist()

            # Redirect to the 'uploaded' view with column names
            return redirect('uploaded')
    else:
        form = FileUploadForm()

    return render(request, 'upload_file.html', {'form': form})

def uploaded(request):
    # Retrieve column names from the session
    column_names = request.session.get('column_names', [])

    # Retrieve selected columns and graph type from POST data
    selected_column_name1 = request.POST.get('column_name1')
    selected_column_name2 = request.POST.get('column_name2')
    selected_graph_type = request.POST.get('graph')

    # Check if selected columns are valid
    # if selected_column_name1 not in column_names or selected_column_name2 not in column_names:
    #     return HttpResponse("Invalid column names")

    # Create a figure and axis
    fig, ax = plt.subplots()

    # Check the selected graph type
    if selected_graph_type == '1':
        # Line Plot
        sns.lineplot(x=selected_column_name1, y=selected_column_name2, data=df, markers='o', ax=ax)
    elif selected_graph_type == '2':
        # Scatter Plot
        sns.scatterplot(x=selected_column_name1, y=selected_column_name2, data=df, marker='o', s=50, ax=ax)
    elif selected_graph_type == '3':
        # Box Plot
        sns.boxplot(x=selected_column_name1, y=selected_column_name2, data=df, ax=ax)
    elif selected_graph_type == '4':
        # Histogram
        sns.histplot(x=selected_column_name1, data=df, ax=ax)
    elif selected_graph_type == '5':
        # KDE Plot
        sns.kdeplot(x=selected_column_name1, data=df, ax=ax)
    elif selected_graph_type == '6':
        # Violin Plot
        sns.violinplot(x=selected_column_name1, data=df, ax=ax)
    elif selected_graph_type == '7':
        # Bar Plot
        sns.barplot(x=selected_column_name1, y=selected_column_name2, data=df, ax=ax)
    elif selected_graph_type == '8':
        # Heatmap
        dff = df.select_dtypes(include=['number'])
        correlation_matrix = dff.corr()
        sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", ax=ax)
        plt.title('Heatmap')
    elif selected_graph_type == '9':
        # Pie Chart
        category_counts = df[selected_column_name1].value_counts()
        ax.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%', startangle=140)

    # Save the plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Encode the image to base64
    image_data = base64.b64encode(buffer.read()).decode("utf-8")
    buffer.close()

    # Pass the base64 encoded image data to the template
    return render(request, 'uploaded.html', {
        'column_names': column_names,
        'selected_column_name1': selected_column_name1,
        'selected_column_name2': selected_column_name2,
        'graph_image': image_data
    })
