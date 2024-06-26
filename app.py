import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
    [
        html.H1("Simple Dash App with Bootstrap"),
        dbc.Row(
            dbc.Col(
                dcc.Input(id='input-1', placeholder='Enter text...', type='text', value=''),
                width={'size': 4, 'offset': 4}  # Corrected syntax for width
            ),
            justify='center'
        ),
        dbc.Row(
            dbc.Col(
                html.Div(id='output-1', children=''),
                width={'size': 4, 'offset': 4}  # Corrected syntax for width
            ),
            justify='center'
        ),
    ],
    className="p-5"
)

@app.callback(
    Output('output-1', 'children'),
    [Input('input-1', 'value')]
)
def update_output(value):
    return f'You have entered: {value}'

if __name__ == '__main__':
    app.run_server(debug=True)
