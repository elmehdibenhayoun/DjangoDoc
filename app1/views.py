from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import FileUploadForm
from .models import SelectedGraphType
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from django.conf import settings
from io import BytesIO
import base64
import plotly.express as px
import plotly.io as pio
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import json
import plotly


def get_numeric_columns(df):
 # This function checks if the dtype of each column is numeric
    return [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]


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


            # Convert DataFrame to a format that can be serialized
            serialized_df = df.to_dict(orient='records')

            # Store data in the session
            request.session['column_names'] = df.columns.tolist()
            request.session['df'] = serialized_df
            request.session['numeric_columns'] = get_numeric_columns(df)

            # Redirect to the 'uploaded' view with column names
            return redirect('uploaded')
    else:
        form = FileUploadForm()

    return render(request, 'upload_file.html', {'form': form})





def calculate_statistics(df, selected_column_name1, selected_column_name2):
    # Calculate your custom statistics
    mean_value = df[selected_column_name2].mean()
    median_value = df[selected_column_name2].median()
    mode_value = df[selected_column_name2].mode().iloc[0]
    range_value = df[selected_column_name2].max() - df[selected_column_name2].min()
    variance_value = df[selected_column_name2].var()
    std_deviation_value = df[selected_column_name2].std()
    count_value = df[selected_column_name2].count()

    # Create a dictionary to store the statistics
    statistics_dict = {
        'Moyenne': mean_value,
        'Médiane': median_value,
        'Mode': mode_value,
        'Variance': variance_value,
        'Écart-type': std_deviation_value,
        'Nombre': count_value,
    }

    # Convert the dictionary to a DataFrame for better formatting
    statistics_df = pd.DataFrame(list(statistics_dict.items()), columns=['Statistic', 'Value'])

    return statistics_df.to_html(classes='table table-striped table-bordered', index=False)




def uploaded(request):
    # Retrieve column names from the session
    column_names = request.session.get('column_names', [])
    serialized_df = request.session.get('df')
    numeric_columns = request.session.get('numeric_columns',[])
    print("numeric columns:", numeric_columns)
    # Convert serialized DataFrame back to a DataFrame
    df = pd.DataFrame(serialized_df)

    # Initialize numeric_columns before the try block
    # numeric_columns = get_numeric_columns(df)
    # print("numeric columns:", numeric_columns)


    if request.method == 'POST':
        # Retrieve selected columns and graph type from POST data
        selected_column_name1 = request.POST.get('column_name1')
        selected_column_name2 = request.POST.get('column_name2')
        selected_graph_type = request.POST.get('graph')
        
        aggregated_df = df.groupby(selected_column_name1, as_index=False).agg({selected_column_name2: 'mean'})

        print("Selected Column 1:", selected_column_name1)
        print("Selected Column 2:", selected_column_name2)
        print("Selected Graph Type:", selected_graph_type)
        print("numeric columns:", numeric_columns)

        try:
            # Check if selected columns are valid
            if selected_column_name1 not in column_names or selected_column_name2 not in numeric_columns:
                return HttpResponse("Invalid column names")


            if selected_graph_type:
                # Check the selected graph type
                if selected_graph_type == '1':
                    # Line Plot
                    if selected_column_name1 != selected_column_name2:
                        # If x and y columns are different, create a line plot
                        fig = px.line(aggregated_df, x=selected_column_name1, y=selected_column_name2, markers=True)
                    else:
                        # If x and y columns are the same, aggregate and create a line plot
                        aggregated_df = df.groupby(selected_column_name1, as_index=False).agg(
                            {selected_column_name2: np.mean})
                        fig = px.line(aggregated_df, x=selected_column_name1, y=selected_column_name2, markers=True)
                elif selected_graph_type == '2':
                    # Scatter Plot
                    fig = px.scatter(aggregated_df, x=selected_column_name1, y=selected_column_name2,
                                     title=f'Scatter Plot for {selected_column_name1} and {selected_column_name2}')
                elif selected_graph_type == '3':
                    # Box Plot
                    fig = px.box(df, x=selected_column_name1, y=selected_column_name2)
                elif selected_graph_type == '4':
                    # Histogram
                    fig = px.histogram(df, x=selected_column_name1)
                elif selected_graph_type == '5':
                    # KDE Plot
                    fig = px.density_heatmap(df, x=selected_column_name1, y=selected_column_name2,
                                             marginal_x="rug", marginal_y="rug")
                elif selected_graph_type == '6':
                    # Violin Plot
                    fig = px.violin(df, x=selected_column_name1, y=selected_column_name2, box=True, points="all")
                elif selected_graph_type == '7':
                    # Bar Plot
                    fig = px.bar(df, x=selected_column_name1, y=selected_column_name2)
                elif selected_graph_type == '8':
                    # Heatmap
                    correlation_matrix = df.corr()
                    fig = px.imshow(df.corr(),
                        labels=dict(color="Correlation"),
                        x=df.columns,
                        y=df.columns,
                        color_continuous_scale='Viridis')
                    fig.update_layout(title='Heatmap')

                elif selected_graph_type == '9':
                    # Pie Chart
                    category_counts = df[selected_column_name1].value_counts()
                    fig = px.pie(category_counts,
                                 values=category_counts,
                                 names=category_counts.index,
                                 title='Pie Chart for {selected_column_name1}')

                else:
                    print("Invalid graph type")

                if 'fig' not in locals():
                    print("The 'fig' variable is not defined.")

                if fig is None:
                    return render(request, 'uploaded.html', {
                        'column_names': column_names,
                        'numeric_columns': numeric_columns,
                        'selected_column_name1': selected_column_name1,
                        'selected_column_name2': selected_column_name2,
                        'selected_graph_type': selected_graph_type,
                        'graph_type_choices': SelectedGraphType.GRAPH_TYPE_CHOICES,
                        'graph_html': None,  # Pass None when fig is None
                        'error_message': "Invalid graph type or data for the selected columns",
                    })

                # If 'fig' is still not defined, return a response
                if 'fig' not in locals():
                    return HttpResponse("Invalid graph type")

                if 'df':
                    print(" df is present ")

                # Calculate custom statistics
                statistics = calculate_statistics(df, selected_column_name1, selected_column_name2)

                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',  # Transparent
                    plot_bgcolor='rgba(0,0,0,0)'  # Transparent
                )

                # Convert the Plotly figure to HTML
                graph_html = fig.to_html(full_html=False)
                #print(graph_html)

                return render(request, 'uploaded.html', {
                    'column_names': column_names,
                    'numeric_columns': numeric_columns,
                    'selected_column_name1': selected_column_name1,
                    'selected_column_name2': selected_column_name2,
                    'selected_graph_type': selected_graph_type,
                    'graph_type_choices': SelectedGraphType.GRAPH_TYPE_CHOICES,
                    'statistics': statistics,
                    'graph_html': graph_html
                })

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            return render(request, 'uploaded.html', {
                'column_names': numeric_columns,
                'graph_type_choices': SelectedGraphType.GRAPH_TYPE_CHOICES,
                'error_message': error_message,
            })

    # Render the initial form
    return render(request, 'uploaded.html', {
        'numeric_columns': numeric_columns,
        'column_names': column_names,
        'graph_type_choices': SelectedGraphType.GRAPH_TYPE_CHOICES,
    })
