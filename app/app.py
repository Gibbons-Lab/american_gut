import dash
import dash_daq as daq
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from start import samples, find_closest


app = dash.Dash(__name__, external_stylesheets=[
    "https://fonts.googleapis.com/css?family=Lato:300,400,700&display=swap"])

app.layout = html.Div(style={"max-width": "1000px", "margin": 0,
                             "font-family": "Lato, sans-serif"},
                      children=[
    html.H1(style={"color": "#3F51B5", "font-weight": "300"},
            children="Who am I?"),

    html.Div(children=[
        html.P("Find close participants in the American Gut project."),
        html.P("What is the percentage of Bacteroides and Firmicutes you want"
               " to query?")
    ]),
    html.Br(),

    daq.Slider(
        id="bac_slider",
        min=0,
        max=100,
        step=1,
        value=40,
        size=400,
        color="red",
        handleLabel={"showCurrentValue": True, "label": "Bacteroidetes"}
    ),
    daq.Slider(
        id="firm_slider",
        min=0,
        max=100,
        step=1,
        value=20,
        size=400,
        color="blue",
        handleLabel={"showCurrentValue": True, "label": "Firmicutes"}
    ),

    dcc.Graph(
        id="phyla_graph",
        figure={
            "data": [
                go.Scatter(
                    x=samples.PC1,
                    y=samples.PC2,
                    text=[
                        "Bacteroides: %.1f%%<br />Firmicutes: %.1f%%" %
                        (s["Bacteroidetes"] * 100, s["Firmicutes"] * 100)
                        for _, s in samples.iterrows()],
                    mode="markers",
                    opacity=0.75,
                    marker={
                        "color": samples.Bacteroidetes - samples.Firmicutes,
                        "colorscale": "RdBu",
                        "showscale": True,
                        "size": (samples.Bacteroidetes + samples.Firmicutes) * 20,
                        "line": {"width": 1, "color": "white"}
                    }
                )
            ],
            "layout": go.Layout()
        },
        style={"height": "80vh"}
    ),
    html.P("Principal components plot of the American Gut participants.")
])

if __name__ == "__main__":
    app.run_server(debug=True)
