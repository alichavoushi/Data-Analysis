import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Output, Input
from dash import dcc, html, Input, Output
from collections import defaultdict
import json
#from geopy.geocoders import GoogleV3
#from geopy.extra.rate_limiter import RateLimiter
import os

#google_api_key = os.getenv('GOOGLE_API_KEY')
 

#google_api_key = os.getenv('GOOGLE_API_KEY')

url="https://raw.githubusercontent.com/alichavoushi/Data-Analysis/main/Trreb%20Analysis%20Toronto_C_geo2.csv?token=GHSAT0AAAAAACTJ6SFA3RDVKP5BJISQ2XDUZTCMYRQ"
#df = pd.read_csv(r'C:\TRREB ANALYSIS\Trreb Analysis Toronto_C_geo.csv', encoding='ISO-8859-1')
df = pd.read_csv(url, index_col=0, encoding='ISO-8859-1')

# Create a DataFrame
df1 = pd.DataFrame(df)
df1['Apt/Unit #'] = df1['Apt/Unit #'].str.replace('#', '')
df1.fillna({'Street #': '', 'Street Name': ''}, inplace=True)
df1['Short Address']=df1['Street #'].astype(str)+" "+df1['Street Name'].astype(str)
df1['Sold Price'] = pd.to_numeric(df1['Sold Price'], errors='coerce')
df1['Short Address']=df1['Street #'].astype(str)+" "+df1['Street Name'].astype(str)#+" st, Toronto, ON, Canada"
# Initialize geocoder

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

def map_sqft_to_category(sqft):
    if pd.isna(sqft):
        return 'Unknown'
    elif sqft in ['0-499', '500-599', '600-699']:
        return '<700'
    elif sqft in ['700-799', '800-899']:
        return '700-899'
    elif sqft in ['900-999', '1000-1099', '1100-1199']:
        return '900-1199'
    elif sqft in ['1200-1399', '1400-1599', '1600-1799', '1800-1999', '2000+']:
        return '1200+'
    else:
        return 'Unknown'

df1['SqFt_Category'] = df1['SqFt'].apply(map_sqft_to_category)

# Expoure Category
def map_exposure_to_category(exposure):
    
    if exposure in ['N', 'Ne', 'Nw']:
        return 'N-Ne-Nw'
    elif exposure in ['S', 'Sw', 'Se','Ns']:
        return 'S-Se-Sw'
    elif exposure in ['E', 'W', 'Ew']:
        return 'E-W-Ew'
    else:
        return 'Unknown'

df1['Exposure_Category'] = df1['Exposure'].apply(map_exposure_to_category)

condition = (df1['Status'] == 'Sold') & (df1['Municipality District'] == 'Toronto C01')& (df1['Sold Price'] < 2000000)

filtered_selected_columns = df1[condition][['Community', 'Short Address','Bedrooms', 'SqFt_Category', 'Sold Price','DOM','Exposure_Category','Floor_Category','Latitude','Longitude']]
# Convert 'Sold Price' column to numeric
filtered_selected_columns['Sold Price'] = pd.to_numeric(filtered_selected_columns['Sold Price'], errors='coerce')
filtered_selected_columns['DOM'] = pd.to_numeric(filtered_selected_columns['DOM'], errors='coerce')
#filtered_selected_columns.dropna(subset=['SqFt'], inplace=True)
#filtered_selected_columns['Exposure'].fillna('Unknown', inplace=True)
#filtered_selected_columns['SqFt'] = filtered_selected_columns['SqFt'].astype(str)
filtered_selected_columns['Community'] = filtered_selected_columns['Community'].astype(str)
#filtered_selected_columns['Exposure'] = filtered_selected_columns['Exposure'].astype(str)

grouped_df_1 = filtered_selected_columns.groupby(['Community', 'SqFt_Category','Bedrooms', 'Floor_Category','Exposure_Category']).agg(
    avg_sold_price=('Sold Price', 'mean'),
    avg_DOM=('DOM', 'mean'),
    units=('Community', 'size')
).reset_index()

grouped_df_1['avg_sold_price'] = np.ceil(grouped_df_1['avg_sold_price'])
grouped_df_1['avg_DOM'] = np.ceil(grouped_df_1['avg_DOM'])

grouped_df_2 = filtered_selected_columns.groupby(['Community', 'Short Address','SqFt_Category','Bedrooms','Floor_Category','Exposure_Category','Latitude','Longitude']).agg(
    avg_sold_price=('Sold Price', 'mean'),
    avg_DOM=('DOM', 'mean'),
    units=('Community', 'size')
).reset_index()

grouped_df_2['avg_sold_price'] = np.ceil(grouped_df_2['avg_sold_price'])
grouped_df_2['avg_DOM'] = np.ceil(grouped_df_2['avg_DOM'])

# Define slicers (dropdowns) for filtering data tab-1
community_options_1 = [{'label': community, 'value': community} for community in grouped_df_1['Community'].unique()]
bedroom_options_1 = [{'label': str(bedroom), 'value': bedroom} for bedroom in grouped_df_1['Bedrooms'].unique()]
sqft_options_1 = [{'label': sqft, 'value': sqft} for sqft in grouped_df_1['SqFt_Category'].unique()]
exposure_options_1 = [{'label': exposure, 'value': exposure} for exposure in grouped_df_1['Exposure_Category'].unique()]
floor_category_options_1 = [{'label': floor_category, 'value': floor_category} for floor_category in grouped_df_1['Floor_Category'].unique()]

# Define slicers (dropdowns) for filtering data tab-2
community_options_2 = [{'label': community, 'value': community} for community in grouped_df_2['Community'].unique()]
bedroom_options_2 = [{'label': str(bedroom), 'value': bedroom} for bedroom in grouped_df_2['Bedrooms'].unique()]
sqft_options_2 = [{'label': sqft, 'value': sqft} for sqft in grouped_df_2['SqFt_Category'].unique()]
exposure_options_2 = [{'label': exposure, 'value': exposure} for exposure in grouped_df_2['Exposure_Category'].unique()]
floor_category_options_2 = [{'label': floor_category, 'value': floor_category} for floor_category in grouped_df_2['Floor_Category'].unique()]
short_address_options_2 = [{'label': short_address, 'value': short_address} for short_address in grouped_df_2['Short Address'].unique()]


app = Dash(__name__)
server = app.server

app.config.suppress_callback_exceptions = True
# Define the layout of the web application

app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='2024 YTD Sold Analysis by Community and Unit Details', value='tab-1', style={'font-size': '12px'}),
        dcc.Tab(label='2024 YTD Sold Analysis by Address and Unit Details', value='tab-2', style={'font-size': '12px'}),
        dcc.Tab(label='Map View', value='tab-3', style={'font-size': '12px'}),
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
                clearable=False,
                multi=True,
                style={'font-size': 'smaller', 'width': '100%'}

            ), 
            html.Label('Select Bedrooms:', style={'font-size': 'smaller'}),
            dcc.Dropdown(
                id='bedroom-filter-1',
                options=bedroom_options_1,
                value=[option['value'] for option in bedroom_options_1],
                multi=True,
                style={'font-size': 'smaller', 'width': '100%'}
            ),
            html.Label('Select SqFt:', style={'font-size': 'smaller'}),
            dcc.Dropdown(
                id='sqft-filter-1',
                options=sqft_options_1,
                value=[option['value'] for option in sqft_options_1],
                multi=True,
                style={'font-size': 'smaller', 'width': '100%'}
            ),
            html.Label('Select Exposure:', style={'font-size': 'smaller'}),
            dcc.Dropdown(
                id='exposure-filter-1',
                options=exposure_options_1,
                value=[option['value'] for option in exposure_options_1],
                multi=True,
                style={'font-size': 'smaller', 'width': '100%'}
            ),
            html.Label('Select Floor Category:', style={'font-size': 'smaller'}),
            dcc.Dropdown(
                id='floor-category-filter-1',
                options=floor_category_options_1,
                value=[option['value'] for option in floor_category_options_1],
                multi=True,
                style={'font-size': 'smaller', 'width': '100%'}
            ),
            html.Div(id='floor-summary-1', style={'font-size': 'smaller'}),
            html.Div([
                html.Div([
                    dcc.Graph(id='scatter-plot-1', style={'height': '80vh'}),
                    html.Div(id='unit-count-1', style={'font-size': 'larger', 'font-weight': 'bold', 'margin-top': '20px'}),
                ], style={'width': '100%', 'display': 'inline-block'}),
            ])
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.Label('Select Community:', style={'font-size': 'smaller'}),
            dcc.Dropdown(
                id='community-filter-2',
                options=community_options_2,
                value=['University'],
                multi=True,
                style={'font-size': 'smaller', 'width': '100%'}
            ),
            html.Label('Select Address:', style={'font-size': 'smaller'}),                
            dcc.Dropdown(
                id='short-address-filter-2',
                options=short_address_options_2,
                value=[option['value'] for option in short_address_options_2],
                multi=True,
                clearable=False,
                className='dropdown-container',
                style={'font-size': 'smaller', 'width': '100%'}
            ),

            html.Label('Select Bedrooms:', style={'font-size': 'smaller'}),
            dcc.Dropdown(
                id='bedroom-filter-2',
                options=bedroom_options_2,
                value=[option['value'] for option in bedroom_options_2],
                multi=True,
                style={'font-size': 'smaller', 'width': '100%'}
            ),
            html.Label('Select SqFt:', style={'font-size': 'smaller'}),
            dcc.Dropdown(
                id='sqft-filter-2',
                options=sqft_options_2,
                value=[option['value'] for option in sqft_options_2],
                multi=True,
                style={'font-size': 'smaller', 'width': '100%'}
            ),
            html.Label('Select Exposure:', style={'font-size': 'smaller'}),
            dcc.Dropdown(
                id='exposure-filter-2',
                options=exposure_options_2,
                value=[option['value'] for option in exposure_options_2],
                multi=True,
                style={'font-size': 'smaller', 'width': '100%'}
            ),
            html.Label('Select Floor Category:', style={'font-size': 'smaller'}),
            dcc.Dropdown(
                id='floor-category-filter-2',
                options=floor_category_options_2,
                value=[option['value'] for option in floor_category_options_2],
                multi=True,
                style={'font-size': 'smaller', 'width': '100%'}
            ),
            html.Div([
                html.Div([
                    dcc.Graph(id='scatter-plot-2', style={'height': '80vh'}),
                    html.Div(id='unit-count-2', style={'font-size': 'larger', 'font-weight': 'bold', 'margin-top': '20px'}),
                ], style={'width': '100%', 'display': 'inline-block'}),
            ])
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3('Google Map'),
            html.Div([
                html.Label('Select Community:', style={'font-size': 'smaller'}),
                dcc.Dropdown(
                    id='community-filter-3',
                    options=community_options_2,
                    value=['University'],
                    multi=True,
                    style={'font-size': 'smaller', 'width': '100%'}
                ),
                html.Label('Select Address:', style={'font-size': 'smaller'}),
                dcc.Dropdown(
                    id='short-address-filter-3',
                    options=short_address_options_2,
                    value=[option['value'] for option in short_address_options_2],
                    multi=True,
                    style={'font-size': 'smaller', 'width': '100%'}
                ),
                html.Label('Select Bedrooms:', style={'font-size': 'smaller'}),
                dcc.Dropdown(
                    id='bedroom-filter-3',
                    options=bedroom_options_2,
                    value=[option['value'] for option in bedroom_options_2],
                    multi=True,
                    style={'font-size': 'smaller', 'width': '100%'}
                ),
                html.Label('Select SqFt:', style={'font-size': 'smaller'}),
                dcc.Dropdown(
                    id='sqft-filter-3',
                    options=sqft_options_2,
                    value=[option['value'] for option in sqft_options_2],
                    multi=True,
                    style={'font-size': 'smaller', 'width': '100%'}
                ),
                html.Label('Select Exposure:', style={'font-size': 'smaller'}),
                dcc.Dropdown(
                    id='exposure-filter-3',
                    options=exposure_options_2,
                    value=[option['value'] for option in exposure_options_2],
                    multi=True,
                    style={'font-size': 'smaller', 'width': '100%'}
                ),
                html.Label('Select Floor Category:', style={'font-size': 'smaller'}),
                dcc.Dropdown(
                    id='floor-category-filter-3',
                    options=floor_category_options_2,
                    value=[option['value'] for option in floor_category_options_2],
                    multi=True,
                    style={'font-size': 'smaller', 'width': '100%'}
                ),
            ]),
            html.Div(id='map', children=[
                html.Iframe(
                    id='map-frame',
                    srcDoc='''
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>Addresses Map</title>
                            <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyAyOkoHPze8R50hkEJpqZD9veJzJIWQxUg&callback=initMap" async defer></script>
                            <script src="https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/markerclusterer.js"></script>
                            <script>
                                function initMap() {
                                    var map = new google.maps.Map(document.getElementById('map'), {
                                        zoom: 12,
                                        center: {lat: 43.65107, lng: -79.347015}
                                    });
                                    
                            </script>
                        </head>
                        <body onload="initMap()">
                            <div id="map" style="height: 500px; width: 100%;"></div>
                        </body>
                        </html>
                    ''',
                    width='100%',
                    height='500'
                )
            ])
        ])


@app.callback(
    [Output('short-address-filter-3', 'options'),
    Output('short-address-filter-3', 'value')],
    Input('community-filter-3', 'value')
)

def set_short_address_options_3(selected_communities):
    if not selected_communities:
        filtered_df = grouped_df_2
    else:
        filtered_df = grouped_df_2[grouped_df_2['Community'].isin(selected_communities)]
    
    short_address_options = [{'label': short_address, 'value': short_address} for short_address in filtered_df['Short Address'].unique()]
   
    return short_address_options, [option['value'] for option in short_address_options]

@app.callback(
    Output('map-frame', 'srcDoc'),
    [Input('community-filter-3', 'value'),
    Input('short-address-filter-3', 'value'),
    Input('bedroom-filter-3', 'value'),
    Input('sqft-filter-3', 'value'),
    Input('exposure-filter-3', 'value'),
    Input('floor-category-filter-3', 'value')]
)


def update_map(communities, addresses, bedrooms, sqft_categories, exposures, floor_categories):
    filtered_df_3 = grouped_df_2[
        grouped_df_2['Community'].isin(communities) &
        grouped_df_2['Short Address'].isin(addresses) &
        grouped_df_2['Bedrooms'].isin(bedrooms) &
        grouped_df_2['SqFt_Category'].isin(sqft_categories) &
        grouped_df_2['Exposure_Category'].isin(exposures) &
        grouped_df_2['Floor_Category'].isin(floor_categories)
    ]
    
    # Group by latitude and longitude to aggregate data for each unique location
    grouped_locations = defaultdict(list)
    for _, row in filtered_df_3.iterrows():
        key = (row['Latitude'], row['Longitude'])
        grouped_locations[key].append(row)

    # Generate JavaScript to update map markers based on grouped_locations
    js_code = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Addresses Map</title>
            <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyAyOkoHPze8R50hkEJpqZD9veJzJIWQxUg&callback=initMap" async defer></script>
            <script src="https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/markerclusterer.js"></script>
            <script>
                var map;
                var markers = [];
                var markerCluster;
                
                function initMap() {
                    map = new google.maps.Map(document.getElementById('map'), {
                        zoom: 12,
                        center: {lat: 43.65107, lng: -79.347015}
                    });
                    updateMap();
                }
                
                function updateMap() {
                    // Clear existing markers
                    markers.forEach(function(marker) {
                        marker.setMap(null);
                    });
                    markers = [];

                    // Define locations and their aggregated data
                    var locations = [
    '''

    # Construct each location with aggregated data in JavaScript format
    for location, rows in grouped_locations.items():
        js_code += f"{{lat: {location[0]}, lng: {location[1]}, shortAddress: '{rows[0]['Short Address']}', data: {json.dumps([{'Bedrooms': row['Bedrooms'], 'SqFt_Category': row['SqFt_Category'], 'Exposure_Category': row['Exposure_Category'], 'Floor_Category': row['Floor_Category'],'units': row['units'], 'avgSoldPrice': row['avg_sold_price'], 'DOM': row['avg_DOM']} for row in rows])}}},\n"

    js_code += '''
                    ];
                    
                    
                    // Loop through locations to create markers
                    locations.forEach(function(loc) {
                        var marker = new google.maps.Marker({
                            position: {lat: loc.lat, lng: loc.lng},
                            map: map,
                            title: loc.shortAddress,
                            icon: {
                                url: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
                                scaledSize: new google.maps.Size(32, 32) // Adjust the size here
                            }
                        });
                        
                        markers.push(marker);
                    
                        // Create content for the tooltip
                        var tooltipContent = '<div style="font-size: 10px;">'; 
                        
                        tooltipContent += `<strong>Address:</strong> ${loc.shortAddress}<br><br>`;

                        loc.data.forEach(function(row) {
                            tooltipContent += `
                                <strong>Bedrooms:</strong> ${row.Bedrooms}<br>
                                <strong>SqFt:</strong> ${row.SqFt_Category}<br>
                                <strong>Exposure:</strong> ${row.Exposure_Category}<br>
                                <strong>Floor Level:</strong> ${row.Floor_Category}<br>
                                <strong>Units:</strong> ${row.units}<br>
                                <strong>Avg Sold Price:</strong> $${row.avgSoldPrice.toLocaleString()}<br>
                                <strong>Avg DOM:</strong> ${row.DOM}<br><br>
                            `;
                        });


                        tooltipContent += '</div>';

                        // Create info window for each marker
                        var infoWindow = new google.maps.InfoWindow({
                            content: tooltipContent
                        });

                        // Event listener to show info window on marker hover
                        marker.addListener('click', function() {
                            infoWindow.open(map, marker);
                        });

                        
                    });
                    
                    // Add MarkerClusterer to manage markers
                    var markerCluster = new MarkerClusterer(map, markers, {
                        imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m'
                    });

                }
                
                // Function to keep the info window open while interacting with it
                function keepInfoWindowOpen() {
                    if (infoWindow) {
                        google.maps.event.addListener(infoWindow, 'domready', function() {
                            var iwOuter = document.querySelector('.gm-style-iw');
                            if (iwOuter) {
                                iwOuter.parentNode.style.pointerEvents = 'auto';
                            }
                        });
                    }
                }
            </script>
        </head>
        <body onload="initMap()">
            <div id="map" style="height: 500px; width: 100%;"></div>
        </body>
        </html>
    '''

    return js_code
    
    

# Make sure to replace YOUR_API_KEY with your actual Google Maps API key

# Callback to update scatter plot based on slicer values for tab-1
# Define callback to update scatter plot based on slicer values
@app.callback(
    [Output('scatter-plot-1', 'figure'),
    Output('unit-count-1', 'children')],
    [Input('community-filter-1', 'value'),
     Input('bedroom-filter-1', 'value'),
     Input('sqft-filter-1', 'value'),
     Input('exposure-filter-1', 'value'),
     Input('floor-category-filter-1', 'value')]
)


def update_scatter_plot_1(selected_communities, selected_bedrooms, selected_sqft, selected_exposure, selected_floor_category):
    filtered_df_1 = grouped_df_1[grouped_df_1['Community'].isin(selected_communities) & 
                             grouped_df_1['Bedrooms'].isin(selected_bedrooms) & 
                             grouped_df_1['SqFt_Category'].isin(selected_sqft) &
                             grouped_df_1['Exposure_Category'].isin(selected_exposure) &
                             grouped_df_1['Floor_Category'].isin(selected_floor_category)]
    
    
    units_sold = filtered_df_1['units'].sum()
    unit_count_text = f"Total Units Sold: {units_sold}"
        
    custom_order = ['<700', '700-899', '900-1199', '1200+','Unknown']
        
        # Sort the unique values of the 'SqFt_Category' column based on the custom order
    sorted_x_values = sorted(filtered_df_1['SqFt_Category'].unique(), key=lambda x: custom_order.index(x))
    
    fig = px.scatter(filtered_df_1, x='SqFt_Category', y='avg_sold_price', color='Community',
                     size='units',# hover_name='Community',
                     hover_data=['Bedrooms','Floor_Category','Exposure_Category','units','avg_DOM'],
                     labels={'SqFt_Category': 'Square Feet', 'Sold Price': 'Average Sold Price'},
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
            font=dict(size=8)
        ),
        annotations=[
            dict(
                x=1,
                y=1,
                xref='paper',
                yref='paper',
                text=unit_count_text,
                showarrow=False,
                font=dict(size=6)
            )
        ]
    )
    return fig, None #unit_count_text

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

    
    return short_address_options, [option['value'] for option in short_address_options]
# Callback to update scatter plot based on slicer values for tab-2
# Define callback to update scatter plot based on slicer values
@app.callback(
    [Output('scatter-plot-2', 'figure'),
    Output('unit-count-2', 'children')],
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
                             grouped_df_2['SqFt_Category'].isin(selected_sqft) &
                             grouped_df_2['Exposure_Category'].isin(selected_exposure) &
                             grouped_df_2['Floor_Category'].isin(selected_floor_category)]
 
    units_sold = filtered_df_2['units'].sum()
    unit_count_text = f"Total Units Sold: {units_sold}"   
    
    fig = px.scatter(filtered_df_2, x='Short Address', y='avg_sold_price', color='Short Address',
                     size='units',# hover_name='Community',
                     hover_data=['SqFt_Category','Bedrooms','Floor_Category','Exposure_Category','units','avg_DOM'],
                     labels={'Short Address': 'Address', 'Sold Price': 'Average Sold Price'},
                     title='Average Sold Price by Address')

    fig.update_yaxes(range=[300000, 2000000], tickformat='$,.0f', dtick=200000)
    #fig.update_xaxes(categoryorder='array', categoryarray=sorted_x_values)
    fig.update_layout(
        height=600,
        margin=dict(t=100),  # Add margin to the top
        showlegend=False,
        annotations=[
            dict(
                x=1,
                y=1,
                xref='paper',
                yref='paper',
                text=unit_count_text,
                showarrow=False,
                font=dict(size=10)
            )
        ]
        
    )
    return fig, None #unit_count_text

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
