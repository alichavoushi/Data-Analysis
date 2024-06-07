import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Output, Input
from dash import dcc, html, Input, Output
import os

url='https://raw.githubusercontent.com/alichavoushi/Data-Analysis/main/Trreb%20Analysis%20Toronto_C.csv?token=GHSAT0AAAAAACTJ6SFA3RDVKP5BJISQ2XDUZTCMYRQ'

df = pd.read_csv(url, index_col=0)
#df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'Trreb Analysis Toronto_C.csv.csv'), encoding='ISO-8859-1')
   
#df = pd.read_csv(r'C:\TRREB ANALYSIS\Trreb Analysis Toronto_C.csv', encoding='ISO-8859-1')

# Read the CSV file
#df = pd.read_csv(r'C:\TRREB ANALYSIS\Trreb Analysis Toronto_C.csv', encoding='ISO-8859-1')

# Create a DataFrame
df1 = pd.DataFrame(df)
df1['Sold Price'] = pd.to_numeric(df1['Sold Price'], errors='coerce')
condition = (df1['Status'] == 'Sold') & (df1['Municipality District'] == 'Toronto C01')& (df1['Sold Price'] < 2000000)
filtered_selected_columns = df[condition][['Community', 'Bedrooms', 'SqFt', 'Sold Price','DOM']]
# Convert 'Sold Price' column to numeric
filtered_selected_columns['Sold Price'] = pd.to_numeric(filtered_selected_columns['Sold Price'], errors='coerce')
filtered_selected_columns['DOM'] = pd.to_numeric(filtered_selected_columns['DOM'], errors='coerce')
filtered_selected_columns.to_csv(r'C:\TRREB ANALYSIS\filtered_selected_columns.csv', encoding='ISO-8859-1')
grouped_df = filtered_selected_columns.groupby(['Community', 'Bedrooms', 'SqFt']).agg(
    avg_sold_price=('Sold Price', 'mean'),
    avg_DOM=('DOM', 'mean'),
    count=('Community', 'size')
).reset_index()

grouped_df['avg_sold_price'] = np.ceil(grouped_df['avg_sold_price'])
grouped_df['avg_DOM'] = np.ceil(grouped_df['avg_DOM'])

grouped_df = grouped_df.reset_index().sort_values(by=['Community', 'Bedrooms','SqFt'])

#grouped_df.to_csv(r'C:\TRREB ANALYSIS\Average_Sold_Price.csv', encoding='ISO-8859-1')
# Create a scatter plot using Plotly


# Define slicers (dropdowns) for filtering data
community_options = [{'label': community, 'value': community} for community in filtered_selected_columns['Community'].unique()]
bedroom_options = [{'label': str(bedroom), 'value': bedroom} for bedroom in filtered_selected_columns['Bedrooms'].unique()]

app = Dash(__name__)
server = app.server
# Define the layout of the web application
app.layout = html.Div([
    html.Label('Select Community:'),
    dcc.Dropdown(
        id='community-filter',
        options=community_options,
        value=[option['value'] for option in community_options],  # Set default value to all communities
        multi=True  # Allow multiple selections
    ),
    html.Label('Select Bedrooms:'),
    dcc.Dropdown(
        id='bedroom-filter',
        options=bedroom_options,
        value=[option['value'] for option in bedroom_options],  # Set default value to all bedrooms
        multi=True  # Allow multiple selections
    ),
    dcc.Graph(id='scatter-plot')
])

# Define callback to update scatter plot based on slicer values
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('community-filter', 'value'),
     Input('bedroom-filter', 'value')]
)

def update_scatter_plot(selected_communities, selected_bedrooms):
    filtered_df = grouped_df[grouped_df['Community'].isin(selected_communities) & grouped_df['Bedrooms'].isin(selected_bedrooms)]
    fig = px.scatter(filtered_df, x='SqFt', y='avg_sold_price', color='Community',
                     size='count', hover_name='Community', 
                     labels={'SqFt': 'Square Feet', 'Sold Price': 'Average Sold Price'},
                     title='Average Sold Price by Square Feet and Community')

    fig.update_yaxes(range=[400000, 2000000], tickformat='$,.0f', dtick=100000)
    
    fig.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>SqFt: %{x}<br>Average Sold Price: %{y}<br>Bedrooms: %{customdata[0]}<br>DOM: %{customdata[2]}<br>Count: %{customdata[1]}<extra></extra>',
        customdata=filtered_df[['Bedrooms', 'count','avg_DOM']]
    )
    fig.update_layout(height=600)
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
