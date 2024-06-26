import logging
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dbc.Button("Hello", id="hello-button")
])

if __name__ == "__main__":
    logging.debug("Starting the app...")
    app.run_server(debug=True)
