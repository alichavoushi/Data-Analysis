import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Output, Input
from dash import dcc, html, Input, Output
import os

url="https://raw.githubusercontent.com/alichavoushi/Data-Analysis/main/Trreb%20Analysis%20Toronto_C.csv?token=GHSAT0AAAAAACTJ6SFA3RDVKP5BJISQ2XDUZTCMYRQ"

df = pd.read_csv(url, index_col=0, encoding='ISO-8859-1')

# Create a DataFrame
df1 = pd.DataFrame(df)
df1['Sold Price'] = pd.to_numeric(df1['Sold Price'], errors='coerce')

condition = (df1['Status'] == 'Sold') & (df1['Municipality District'] == 'Toronto C01')& (df1['Sold Price'] < 2000000)

filtered_selected_columns = df[condition][['Community', 'Bedrooms', 'SqFt', 'Sold Price','DOM','Exposure']]
# Convert 'Sold Price' column to numeric
filtered_selected_columns['Sold Price'] = pd.to_numeric(filtered_selected_columns['Sold Price'], errors='coerce')
filtered_selected_columns['DOM'] = pd.to_numeric(filtered_selected_columns['DOM'], errors='coerce')
#filtered_selected_columns.to_csv(r'C:\TRREB ANALYSIS\filtered_selected_columns.csv', encoding='ISO-8859-1')
filtered_selected_columns.dropna(subset=['SqFt'], inplace=True)
filtered_selected_columns['Exposure'].fillna('Unknown', inplace=True)
filtered_selected_columns['SqFt'] = filtered_selected_columns['SqFt'].astype(str)
filtered_selected_columns['Community'] = filtered_selected_columns['Community'].astype(str)
filtered_selected_columns['Exposure'] = filtered_selected_columns['Exposure'].astype(str)

grouped_df = filtered_selected_columns.groupby(['Community', 'Bedrooms', 'SqFt','Exposure']).agg(
    avg_sold_price=('Sold Price', 'mean'),
    avg_DOM=('DOM', 'mean'),
    units=('Community', 'size')
).reset_index()


grouped_df['avg_sold_price'] = np.ceil(grouped_df['avg_sold_price'])
grouped_df['avg_DOM'] = np.ceil(grouped_df['avg_DOM'])

# Define slicers (dropdowns) for filtering data
community_options = [{'label': community, 'value': community} for community in filtered_selected_columns['Community'].unique()]
bedroom_options = [{'label': str(bedroom), 'value': bedroom} for bedroom in filtered_selected_columns['Bedrooms'].unique()]
sqft_options = [{'label': sqft, 'value': sqft} for sqft in filtered_selected_columns['SqFt'].unique()]
exposure_options = [{'label': exposure, 'value': exposure} for exposure in filtered_selected_columns['Exposure'].unique()]
app = Dash(__name__)
server = app.server
# Define the layout of the web application
app.layout = html.Div([
    html.Label('Select Community:'),
    dcc.Dropdown(
        id='community-filter',
        options=community_options,
        value=[option['value'] for option in community_options],  # Set default value to all communities
        multi=True,  # Allow multiple selections
        style={'font-size': 'smaller','width': '100%'}
    ),
    html.Label('Select Bedrooms:'),
    dcc.Dropdown(
        id='bedroom-filter',
        options=bedroom_options,
        value=[option['value'] for option in bedroom_options],  # Set default value to all bedrooms
        multi=True,  # Allow multiple selections
        style={'font-size': 'smaller','width': '100%'}
    ),
    html.Label('Select SqFt:'),
    dcc.Dropdown(
        id='sqft-filter',
        options=sqft_options,
        value=[option['value'] for option in sqft_options],  # Set default value to all SqFt
        multi=True,  # Allow multiple selections
        style={'font-size': 'smaller','width': '100%'}
    ),
    html.Label('Select Exposure:'),
    dcc.Dropdown(
        id='exposure-filter',
        options=exposure_options,
        value=[option['value'] for option in exposure_options],  # Set default value to all Exposures
        multi=True,  # Allow multiple selections
        style={'font-size': 'smaller','width': '100%'}  # Adjust font size
    ),
    dcc.Graph(id='scatter-plot')
])

# Define callback to update scatter plot based on slicer values
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('community-filter', 'value'),
     Input('bedroom-filter', 'value'),
     Input('sqft-filter', 'value'),
     Input('exposure-filter', 'value')]
)

def update_scatter_plot(selected_communities, selected_bedrooms, selected_sqft, selected_exposure):
    filtered_df = grouped_df[grouped_df['Community'].isin(selected_communities) & 
                             grouped_df['Bedrooms'].isin(selected_bedrooms) & 
                             grouped_df['SqFt'].isin(selected_sqft) &
                             grouped_df['Exposure'].isin(selected_exposure)]
    
#def update_scatter_plot(selected_communities, selected_bedrooms):
 #   filtered_df = grouped_df[grouped_df['Community'].isin(selected_communities) & grouped_df['Bedrooms'].isin(selected_bedrooms)]
    #filtered_df = filtered_df[filtered_df['SqFt'] != 0]
    def extract_lower_bound(s):
        try:
            return int(s.split('-')[0])
        except ValueError:
            return 0  # If the value is not convertible to an integer, return 0


    sorted_x_values = sorted(filtered_df['SqFt'].unique(), key=extract_lower_bound)
    
    
    fig = px.scatter(filtered_df, x='SqFt', y='avg_sold_price', color='Community',
                     size='units',# hover_name='Community',
                     hover_data=['Bedrooms','Exposure','units','avg_DOM'],
                     labels={'SqFt': 'Square Feet', 'Sold Price': 'Average Sold Price'},
                     title='Average Sold Price by Square Feet and Community')
    
    


    fig.update_yaxes(range=[400000, 2000000], tickformat='$,.0f', dtick=200000)
    fig.update_xaxes(categoryorder='array', categoryarray=sorted_x_values)
    fig.update_layout(height=600)
    fig.update_layout(legend=dict(font=dict(size=8))) 
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
