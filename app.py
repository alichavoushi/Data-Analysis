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
df1['Apt/Unit #'] = df1['Apt/Unit #'].str.replace('#', '')
df1.fillna({'Street #': '', 'Street Name': ''}, inplace=True)
df1['Short Address']=df1['Street #'].astype(str)+" "+df1['Street Name'].astype(str)

def calculate_floor(row):
    unit = str(row['Apt/Unit #'])   
    if pd.isna(row['Apt/Unit #']) or row['Apt/Unit #'] == '':
        return ''  # Return blank if 'Apt/Unit #' is NaN or blank
    elif 'th' in unit.lower():  # Convert to lowercase and check for 'ph'
        return None  # Return 'Ph' if 'Apt/Unit #' contains 'ph'
    elif row['Apt/Unit #'].lower().find('ph') != -1:  # Check if 'Apt/Unit #' contains 'ph' (case-insensitive)
        return 'Ph'
    elif row['Apt/Unit #'].lower().find('p') != -1:  # Check if 'Apt/Unit #' contains 'ph' (case-insensitive)
        return None
    elif row['Apt/Unit #'].lower().find('g') != -1:  # Check if 'Apt/Unit #' contains 'ph' (case-insensitive)
        return None
    
    elif ('Condo' in row['Type'] or 'Apart' in row['Type'] or 'Apt' in row['Type']) and 'Town' not in row['Type'] and 'Park' not in row['Type'] and 'Park' not in row['Apt/Unit #']:
        unit = str(row['Apt/Unit #'])  # Convert to string to handle NaN
        if unit[0].isalpha():  # Check if the first character is a letter
            unit = unit[1:]    # Strip away the leading letter
        if len(unit) > 3:
            return unit[:2]  # Take the first two characters of 'Apt/Unit #'
        elif len(unit) == 3:
            return unit[0]   # Take the first character of 'Apt/Unit #'
    return None  # Return None if none of the conditions are met

# Apply the function to create a new column
df1['Floor'] = df1.apply(calculate_floor, axis=1)

def categorize_floor(floor):
    
    if floor == 'Ph':
        return 'Penthouse'
    elif floor == '':
        return 'Unknown' 
    elif floor is None:
        return 'Unknown'
    else:
        try:
            floor_num = int(floor)
            if floor_num <= 10:
                return 'Low'
            elif 11 <= floor_num <= 25:
                return 'Mid'
            elif 26 <= floor_num <= 40:
                return 'High'
            else:
                return 'Very High'
        except ValueError:
            return 'Invalid'

# Apply categorization to create a new column 'Floor Category'
df1['Floor_Category'] = df1['Floor'].apply(categorize_floor)

df1['Sold Price'] = pd.to_numeric(df1['Sold Price'], errors='coerce')

condition = (df1['Status'] == 'Sold') & (df1['Municipality District'] == 'Toronto C01')& (df1['Sold Price'] < 2000000)

filtered_selected_columns = df1[condition][['Community', 'Short Address','Bedrooms', 'SqFt', 'Sold Price','DOM','Exposure','Floor_Category']]
# Convert 'Sold Price' column to numeric
filtered_selected_columns['Sold Price'] = pd.to_numeric(filtered_selected_columns['Sold Price'], errors='coerce')
filtered_selected_columns['DOM'] = pd.to_numeric(filtered_selected_columns['DOM'], errors='coerce')
#filtered_selected_columns.to_csv(r'C:\TRREB ANALYSIS\filtered_selected_columns.csv', encoding='ISO-8859-1')
filtered_selected_columns.dropna(subset=['SqFt'], inplace=True)
filtered_selected_columns['Exposure'].fillna('Unknown', inplace=True)
filtered_selected_columns['SqFt'] = filtered_selected_columns['SqFt'].astype(str)
filtered_selected_columns['Community'] = filtered_selected_columns['Community'].astype(str)
filtered_selected_columns['Exposure'] = filtered_selected_columns['Exposure'].astype(str)

grouped_df_1 = filtered_selected_columns.groupby(['Community', 'Bedrooms', 'SqFt','Exposure','Floor_Category']).agg(
    avg_sold_price=('Sold Price', 'mean'),
    avg_DOM=('DOM', 'mean'),
    units=('Community', 'size')
).reset_index()


grouped_df_1['avg_sold_price'] = np.ceil(grouped_df_1['avg_sold_price'])
grouped_df_1['avg_DOM'] = np.ceil(grouped_df_1['avg_DOM'])

grouped_df_2 = filtered_selected_columns.groupby(['Community', 'Short Address','Bedrooms', 'SqFt','Exposure','Floor_Category']).agg(
    avg_sold_price=('Sold Price', 'mean'),
    avg_DOM=('DOM', 'mean'),
    units=('Community', 'size')
).reset_index()


grouped_df_2['avg_sold_price'] = np.ceil(grouped_df_2['avg_sold_price'])
grouped_df_2['avg_DOM'] = np.ceil(grouped_df_2['avg_DOM'])

# Define slicers (dropdowns) for filtering data tab-1
community_options_1 = [{'label': community, 'value': community} for community in grouped_df_1['Community'].unique()]
bedroom_options_1 = [{'label': str(bedroom), 'value': bedroom} for bedroom in grouped_df_1['Bedrooms'].unique()]
sqft_options_1 = [{'label': sqft, 'value': sqft} for sqft in grouped_df_1['SqFt'].unique()]
exposure_options_1 = [{'label': exposure, 'value': exposure} for exposure in grouped_df_1['Exposure'].unique()]
floor_category_options_1 = [{'label': floor_category, 'value': floor_category} for floor_category in grouped_df_1['Floor_Category'].unique()]



# Define slicers (dropdowns) for filtering data tab-2
community_options_2 = [{'label': community, 'value': community} for community in grouped_df_2['Community'].unique()]
bedroom_options_2 = [{'label': str(bedroom), 'value': bedroom} for bedroom in grouped_df_2['Bedrooms'].unique()]
sqft_options_2 = [{'label': sqft, 'value': sqft} for sqft in grouped_df_2['SqFt'].unique()]
exposure_options_2 = [{'label': exposure, 'value': exposure} for exposure in grouped_df_2['Exposure'].unique()]
floor_category_options_2 = [{'label': floor_category, 'value': floor_category} for floor_category in grouped_df_2['Floor_Category'].unique()]
short_address_options_2 = [{'label': short_address, 'value': short_address} for short_address in grouped_df_2['Short Address'].unique()]

app = Dash(__name__)
server = app.server

app.config.suppress_callback_exceptions = True
# Define the layout of the web application
app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='2024 YTD Sold Analysis by Community and Unit Details', value='tab-1'),
        dcc.Tab(label='2024 YTD Sold Analysis by Address and Unit details', value='tab-2'),
    ]),
    html.Div(id='tabs-content')
])

@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value')
)

def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.Label('Select Community:', style={'font-size': 'smaller'}),
            dcc.Dropdown(
                id='community-filter-1',
                options=community_options_1,
                value=['University'],
                #value=[option['value'] for option in community_options_1],  # Set default value to all communities
                multi=True,  # Allow multiple selections
                style={'font-size': 'smaller', 'width': '100%'}
            ),
            html.Label('Select Bedrooms:', style={'font-size': 'smaller'}),
            dcc.Dropdown(
                id='bedroom-filter-1',
                options=bedroom_options_1,
                value=[option['value'] for option in bedroom_options_1],  # Set default value to all bedrooms
                multi=True,  # Allow multiple selections
                style={'font-size': 'smaller', 'width': '100%'}
            ),
            html.Label('Select SqFt:', style={'font-size': 'smaller'}),
            dcc.Dropdown(
                id='sqft-filter-1',
                options=sqft_options_1,
                value=[option['value'] for option in sqft_options_1],  # Set default value to all SqFt
                multi=True,  # Allow multiple selections
                style={'font-size': 'smaller', 'width': '100%'}
            ),
            html.Label('Select Exposure:', style={'font-size': 'smaller'}),
            dcc.Dropdown(
                id='exposure-filter-1',
                options=exposure_options_1,
                value=[option['value'] for option in exposure_options_1],  # Set default value to all Exposures
                multi=True,  # Allow multiple selections
                style={'font-size': 'smaller', 'width': '100%'}  # Adjust font size
            ),
            html.Label('Select Floor Category:', style={'font-size': 'smaller'}),
            dcc.Dropdown(
                id='floor-category-filter-1',
                options=floor_category_options_1,
                value=[option['value'] for option in floor_category_options_1],  # Set default value to all Floor Categories
                multi=True,  # Allow multiple selections
                style={'font-size': 'smaller', 'width': '100%'}
            ),
            dcc.Graph(id='scatter-plot-1', style={'height': '80vh'})  # Set height using viewport units
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.Label('Select Community:', style={'font-size': 'smaller'}),
            dcc.Dropdown(
                id='community-filter-2',
                options=community_options_2,
                value=['University'],
                #value=[option['value'] for option in community_options_2],  # Set default value to all communities
                multi=True,  # Allow multiple selections
                style={'font-size': 'smaller', 'width': '100%'}
            ),
            html.Label('Select Address:', style={'font-size': 'smaller'}),
            dcc.Dropdown(
                id='short-address-filter-2',
                #options=short_address_options_2,
                #value=[option['value'] for option in short_address_options_2],  # Set default value to all communities
                multi=True,  # Allow multiple selections
                style={'font-size': 'smaller', 'width': '100%'}
            ),
            html.Label('Select Bedrooms:', style={'font-size': 'smaller'}),
            dcc.Dropdown(
                id='bedroom-filter-2',
                options=bedroom_options_2,
                value=[option['value'] for option in bedroom_options_2],  # Set default value to all bedrooms
                multi=True,  # Allow multiple selections
                style={'font-size': 'smaller', 'width': '100%'}
            ),
            html.Label('Select SqFt:', style={'font-size': 'smaller'}),
            dcc.Dropdown(
                id='sqft-filter-2',
                options=sqft_options_2,
                value=[option['value'] for option in sqft_options_2],  # Set default value to all SqFt
                multi=True,  # Allow multiple selections
                style={'font-size': 'smaller', 'width': '100%'}
            ),
            html.Label('Select Exposure:', style={'font-size': 'smaller'}),
            dcc.Dropdown(
                id='exposure-filter-2',
                options=exposure_options_2,
                value=[option['value'] for option in exposure_options_2],  # Set default value to all Exposures
                multi=True,  # Allow multiple selections
                style={'font-size': 'smaller', 'width': '100%'}  # Adjust font size
            ),
            html.Label('Select Floor Category:', style={'font-size': 'smaller'}),
            dcc.Dropdown(
                id='floor-category-filter-2',
                options=floor_category_options_2,
                value=[option['value'] for option in floor_category_options_2],  # Set default value to all Floor Categories
                multi=True,  # Allow multiple selections
                style={'font-size': 'smaller', 'width': '100%'}
            ),
            dcc.Graph(id='scatter-plot-2', style={'height': '80vh'})  # Set height using viewport units
        ])


# Callback to update the options for short address based on selected community
@app.callback(
    Output('short-address-filter-2', 'options'),
    Output('short-address-filter-2', 'value'),
    Input('community-filter-2', 'value')
)
def set_short_address_options(selected_communities):
    if not selected_communities:
        filtered_df = grouped_df_2
    else:
        filtered_df = grouped_df_2[grouped_df_2['Community'].isin(selected_communities)]
    
    short_address_options = [{'label': short_address, 'value': short_address} for short_address in filtered_df['Short Address'].unique()]
    
    # Debug: Print filtered short address options
    #print("Filtered Short Address Options: ", short_address_options)
    
    return short_address_options, [option['value'] for option in short_address_options]


# Callback to update scatter plot based on slicer values for tab-1
# Define callback to update scatter plot based on slicer values
@app.callback(
    Output('scatter-plot-1', 'figure'),
    [Input('community-filter-1', 'value'),
     Input('bedroom-filter-1', 'value'),
     Input('sqft-filter-1', 'value'),
     Input('exposure-filter-1', 'value'),
     Input('floor-category-filter-1', 'value')]
)

def update_scatter_plot_1(selected_communities, selected_bedrooms, selected_sqft, selected_exposure, selected_floor_category):
    filtered_df_1 = grouped_df_1[grouped_df_1['Community'].isin(selected_communities) & 
                             grouped_df_1['Bedrooms'].isin(selected_bedrooms) & 
                             grouped_df_1['SqFt'].isin(selected_sqft) &
                             grouped_df_1['Exposure'].isin(selected_exposure) &
                             grouped_df_1['Floor_Category'].isin(selected_floor_category)]
    
#def update_scatter_plot(selected_communities, selected_bedrooms):
 #   filtered_df = grouped_df[grouped_df['Community'].isin(selected_communities) & grouped_df['Bedrooms'].isin(selected_bedrooms)]
    #filtered_df = filtered_df[filtered_df['SqFt'] != 0]
    def extract_lower_bound(s):
        try:
            return int(s.split('-')[0])
        except ValueError:
            return 0  # If the value is not convertible to an integer, return 0


    sorted_x_values = sorted(filtered_df_1['SqFt'].unique(), key=extract_lower_bound)
    
    
    fig = px.scatter(filtered_df_1, x='SqFt', y='avg_sold_price', color='Community',
                     size='units',# hover_name='Community',
                     hover_data=['Bedrooms','Floor_Category','Exposure','units','avg_DOM'],
                     labels={'SqFt': 'Square Feet', 'Sold Price': 'Average Sold Price'},
                     title='Average Sold Price by Square Feet and Community')
    
    


    fig.update_yaxes(range=[300000, 2000000], tickformat='$,.0f', dtick=200000)
    fig.update_xaxes(categoryorder='array', categoryarray=sorted_x_values)
    fig.update_layout(
        height=600,
        margin=dict(t=100),  # Add margin to the top
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1,  # Adjust y position to move the legend above the title
            xanchor='left',
            x=0,
            title='',
            font=dict(size=10)
        )
    )
    return fig

# Callback to update scatter plot based on slicer values for tab-2
# Define callback to update scatter plot based on slicer values
@app.callback(
    Output('scatter-plot-2', 'figure'),
    [Input('community-filter-2', 'value'),
     Input('short-address-filter-2', 'value'),
     Input('bedroom-filter-2', 'value'),
     Input('sqft-filter-2', 'value'),
     Input('exposure-filter-2', 'value'),
     Input('floor-category-filter-2', 'value')]
)

def update_scatter_plot_2(selected_communities, selected_short_address,selected_bedrooms, selected_sqft, selected_exposure, selected_floor_category):
    filtered_df_2 = grouped_df_2[grouped_df_2['Community'].isin(selected_communities) & 
                             grouped_df_2['Short Address'].isin(selected_short_address) & 
                             grouped_df_2['Bedrooms'].isin(selected_bedrooms) & 
                             grouped_df_2['SqFt'].isin(selected_sqft) &
                             grouped_df_2['Exposure'].isin(selected_exposure) &
                             grouped_df_2['Floor_Category'].isin(selected_floor_category)]
    

    def extract_lower_bound(s):
        try:
            return int(s.split('-')[0])
        except ValueError:
            return 0  # If the value is not convertible to an integer, return 0


    sorted_x_values = sorted(filtered_df_2['Short Address'].unique(), key=extract_lower_bound)
    
    
    fig = px.scatter(filtered_df_2, x='Short Address', y='avg_sold_price', color='Short Address',
                     size='units',# hover_name='Community',
                     hover_data=['SqFt','Bedrooms','Floor_Category','Exposure','units','avg_DOM'],
                     labels={'Short Address': 'Address', 'Sold Price': 'Average Sold Price'},
                     title='Average Sold Price by Address')
    
    


    fig.update_yaxes(range=[300000, 2000000], tickformat='$,.0f', dtick=200000)
    fig.update_xaxes(categoryorder='array', categoryarray=sorted_x_values)
    fig.update_layout(
        height=600,
        margin=dict(t=100),  # Add margin to the top
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1,  # Adjust y position to move the legend above the title
            xanchor='left',
            x=0,
            title='',
            font=dict(size=10)
        )
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
