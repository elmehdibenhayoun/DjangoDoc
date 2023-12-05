from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import FileUploadForm
from .models import SelectedGraphType
import pandas as pd
import os
import matplotlib.pyplot as plt
from django.conf import settings
from io import BytesIO
import base64
import seaborn as sns
import plotly.express as px
import plotly.io as pio
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import json
import plotly


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

            # Redirect to the 'uploaded' view with column names
            return redirect('uploaded')
    else:
        form = FileUploadForm()

    return render(request, 'upload_file.html', {'form': form})


def uploaded(request):
    # Retrieve column names from the session
    column_names = request.session.get('column_names', [])
    serialized_df = request.session.get('df')

    # Convert serialized DataFrame back to a DataFrame
    df = pd.DataFrame(serialized_df)

    if request.method == 'POST':
        # Retrieve selected columns and graph type from POST data
        selected_column_name1 = request.POST.get('column_name1')
        selected_column_name2 = request.POST.get('column_name2')
        selected_graph_type = request.POST.get('graph')

        print("Selected Column 1:", selected_column_name1)
        print("Selected Column 2:", selected_column_name2)
        print("Selected Graph Type:", selected_graph_type)

        # Check if selected columns are valid
        if selected_column_name1 not in column_names or selected_column_name2 not in column_names:
            return HttpResponse("Invalid column names")

        fig = None
        if selected_graph_type:
        # Check the selected graph type
            if selected_graph_type == '1':
                # Line Plot
                fig = px.line(df, x=selected_column_name1, y=selected_column_name2, markers=True)
            elif selected_graph_type == '2':
                # Scatter Plot
                fig = px.scatter(df, x=selected_column_name1, y=selected_column_name2, title=f'Scatter Plot for {selected_column_name1} and {selected_column_name2}')
            elif selected_graph_type == '3':
                # Box Plot
                fig = px.box(df, x=selected_column_name1, y=selected_column_name2)
            elif selected_graph_type == '4':
                # Histogram
                fig = px.histogram(df, x=selected_column_name1)
            elif selected_graph_type == '5':
                # KDE Plot
                fig = px.density_heatmap(df, x=selected_column_name1, y=selected_column_name2,
                                        marginal_x="histogram", marginal_y="histogram")
            elif selected_graph_type == '6':
                # Violin Plot
                fig = px.violin(df, x=selected_column_name1, y=selected_column_name2, box=True, points="all")
            elif selected_graph_type == '7':
                # Bar Plot
                fig = px.bar(df, x=selected_column_name1, y=selected_column_name2)
            elif selected_graph_type == '8':
                # Heatmap
                correlation_matrix = df.corr()
                fig = px.imshow(correlation_matrix,
                                labels=dict(color="Correlation"),
                                x=column_names,
                                y=column_names,
                                color_continuous_scale='Viridis')
                fig.update_layout(title='Heatmap')
            elif selected_graph_type == '9':
                # Pie Chart
                category_counts = df[selected_column_name1].value_counts()
                fig = px.pie(category_counts,
                            values=category_counts,
                            names=category_counts.index,
                            title=f'Pie Chart for {selected_column_name1}')

            else:
                print("Invalid graph type")

            if 'fig' not in locals():
                print("The 'fig' variable is not defined.")

            if fig is None:
                return render(request, 'uploaded.html', {
                    'column_names': column_names,
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

            if 'df' : 
                print(" df is present ")

            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',  # Transparent
                plot_bgcolor='rgba(0,0,0,0)'    # Transparent
            )

            # Convert the Plotly figure to HTML
            graph_html = fig.to_html(full_html=False)

            return render(request, 'uploaded.html', {
                'column_names': column_names,
                'selected_column_name1': selected_column_name1,
                'selected_column_name2': selected_column_name2,
                'selected_graph_type': selected_graph_type,
                'graph_type_choices': SelectedGraphType.GRAPH_TYPE_CHOICES,
                'graph_html': graph_html
            })

    # Render the initial form
    return render(request, 'uploaded.html', {
        'column_names': column_names,
        'graph_type_choices': SelectedGraphType.GRAPH_TYPE_CHOICES,
    })


































































# def uploaded(request):
#     # Retrieve column names from the session
#     column_names = request.session.get('column_names', [])

#     # Retrieve selected columns and graph type from POST data
#     selected_column_name1 = request.POST.get('column_name1')
#     selected_column_name2 = request.POST.get('column_name2')
#     selected_graph_type = request.POST.get('graph')

#     # Check the selected graph type
#     graph_type_choices = SelectedGraphType.GRAPH_TYPE_CHOICES
#     selected_graph_display = dict(graph_type_choices).get(selected_graph_type, 'Unknown Graph Type')

#     if selected_graph_type:
#         selected_graph_obj = SelectedGraphType(graph_type=selected_graph_type)
#         selected_graph_obj.save()

#     # Set the title for the selected graph type
#     if selected_graph_type and selected_graph_display:
#         plt.title(f'{selected_graph_display} for {selected_column_name1} and {selected_column_name2}')

#      # Create a Plotly figure
#     fig = make_subplots()

#     # Check the selected graph type
#     if selected_graph_type == '1':
#         # Line Plot
#         fig.add_trace(go.Scatter(x=df[selected_column_name1], y=df[selected_column_name2], mode='lines+markers'))
#     elif selected_graph_type == '2':
#         # Scatter Plot
#         fig.add_trace(go.Scatter(x=df[selected_column_name1], y=df[selected_column_name2], mode='markers'))
#     elif selected_graph_type == '3':
#         # Box Plot
#         fig.add_trace(go.Box(x=df[selected_column_name1], y=df[selected_column_name2]))
#     elif selected_graph_type == '4':
#         # Histogram
#         fig.add_trace(go.Histogram(x=df[selected_column_name1]))
#     elif selected_graph_type == '5':
#         # KDE Plot
#         fig.add_trace(go.Histogram2dContour(
#             x=df[selected_column_name1],
#             y=df[selected_column_name2],
#             colorscale='Viridis',
#             reversescale=True,
#             contours=dict(coloring='heatmap')
#     ))
#     elif selected_graph_type == '6':
#         # Violin Plot
#         fig.add_trace(go.Violin(
#             x=df[selected_column_name1],
#             y=df[selected_column_name2],
#             box_visible=True,
#             line_color='black',
#             meanline_visible=True,
#             fillcolor='lightseagreen',
#             opacity=0.6,
#             box_mean='sd'
#         ))
#     elif selected_graph_type == '7':
#         # Bar Plot
#         fig.add_trace(go.Bar(
#             x=df[selected_column_name1],
#             y=df[selected_column_name2]
#         ))
#     elif selected_graph_type == '8':
#         # Heatmap
#         correlation_matrix = df.corr()
#         fig = px.imshow(correlation_matrix,
#                         labels=dict(color="Correlation"),
#                         x=column_names,
#                         y=column_names,
#                         color_continuous_scale='Viridis')
#         fig.update_layout(title='Heatmap')
#     elif selected_graph_type == '9':
#         # Pie Chart
#         category_counts = df[selected_column_name1].value_counts()
#         fig = px.pie(category_counts,
#                     values=category_counts,
#                     names=category_counts.index,
#                     title=f'Pie Chart for {selected_column_name1}')


#     # Update layout as needed
#     fig.update_layout(title=f'{selected_graph_type} for {selected_column_name1} and {selected_column_name2}')

#     # Convert the figure to HTML
#     graph_html = pio.to_html(fig, full_html=False)

#     # Pass the Plotly HTML to the template
#     return render(request, 'uploaded.html', {
#         'column_names': column_names,
#         'selected_column_name1': selected_column_name1,
#         'selected_column_name2': selected_column_name2,
#         'selected_graph_type': selected_graph_type,
#         'graph_type_choices': graph_type_choices,
#         'graph_html': graph_html
#     })
