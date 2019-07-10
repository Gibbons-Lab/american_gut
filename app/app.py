"""The American Gut App."""

import dash
import dash_daq as daq
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from start import samples, find_closest


close = pd.Series(0, index=samples.index)


def beta_figure(close, size=16):
    """Generate the beta diversity figure."""
    s = samples[close == 0]
    ns = samples[close == 1]
    return {
        "data": [
            go.Scattergl(
                name="",
                x=s.PC1,
                y=s.PC2,
                showlegend=False,
                text=[
                    "Bacteroidetes: %.1f%%<br />Firmicutes: %.1f%%"
                    % (r["Bacteroidetes"] * 100, r["Firmicutes"] * 100)
                    for _, r in s.iterrows()
                ],
                mode="markers",
                marker={
                    "color": s.Bacteroidetes - s.Firmicutes,
                    "colorscale": "RdBu",
                    "showscale": True,
                    "size": (s.Bacteroidetes + s.Firmicutes) * size,
                    "line": {"width": 1, "color": "white"},
                    "opacity": 0.75,
                },
            ),
            go.Scattergl(
                name="",
                x=ns.PC1,
                y=ns.PC2,
                showlegend=False,
                text=[
                    "Bacteroidetes: %.1f%%<br />Firmicutes: %.1f%%"
                    % (r["Bacteroidetes"] * 100, r["Firmicutes"] * 100)
                    for _, r in ns.iterrows()
                ],
                mode="markers",
                marker={
                    "color": "#F8BBD0",
                    "showscale": False,
                    "size": max(size * 1.25, 2),
                    "line": {"width": size / 3, "color": "#C51162"},
                    "opacity": 1.0,
                },
            ),
        ],
        "layout": go.Layout(
            title="Bray-Curtis PCoA",
            hovermode="closest",
            coloraxis={"cmin": -1, "cmax": 1},
        ),
    }


def info_field(icon, text, color):
    """Draw an info field."""
    return html.Div(
        [
            html.I(
                className="fas fa-%s fa-2x" % icon,
                style={
                    "vertical-align": "middle",
                    "padding": "0 8px",
                    "color": color,
                },
            ),
            html.Span(
                text,
                style={
                    "font": "24px Lato",
                    "vertical-align": "middle",
                    "color": "#666",
                },
            ),
        ]
    )


app = dash.Dash(
    __name__,
    external_stylesheets=[
        "https://fonts.googleapis.com/css?family=Lato:300,400,700&display=swap",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.9.0/css/all.min.css",
    ],
)

app.layout = html.Div(
    style={
        "max-width": "1000px",
        "margin": 0,
        "font": "16px Lato, sans-serif",
    },
    children=[
        html.H1(
            style={"color": "#3F51B5", "font-weight": "300"},
            children="Who am I?",
        ),
        html.Div(
            children=[
                html.P(
                    "Find who your gut is most similar to from the American Gut Project. Use the sliders to input your Bacteroidetes and Firmicutes percentages."
                ),
                html.P("Legend:"),
                html.P("Bluer points represent a higher ratio of Firmicutes."),
                html.P(
                    "Redder points represent a higher ratio of Bacteroidetes."
                ),
                html.P(
                    "Pink points show the 5 closest individuals to your distribution."
                ),
                html.P(
                    "Size of the points is based on overall percentages of Firmicutes and Bacteroidetes in relation to overall gut bacteria."
                ),
            ],
            style={
                "box-shadow": "1px 1px 3px #aaa",
                "border": "1px solid gray",
                "border-radius": "5px",
                "margin": "1em",
                "padding": "0.25em 1em",
                "max-width": "90%",
                "color": "#666",
            },
        ),
        html.Br(),
        html.Div(
            [
                daq.Slider(
                    id="bac_slider",
                    min=0,
                    max=100,
                    step=1,
                    value=40,
                    size=360,
                    color="red",
                    handleLabel={
                        "showCurrentValue": True,
                        "label": "%Bacteroidetes",
                    },
                ),
                daq.Slider(
                    id="firm_slider",
                    min=0,
                    max=100,
                    step=1,
                    value=20,
                    size=360,
                    color="blue",
                    handleLabel={
                        "showCurrentValue": True,
                        "label": "%Firmicutes",
                    },
                ),
            ],
            style={
                "display": "flex",
                "justify-content": "space-around",
                "flex-wrap": "wrap",
            },
        ),
        dcc.Graph(
            id="phyla_graph",
            figure=beta_figure(close),
            style={"height": "70vh", "margin": 0, "padding": 0},
        ),
        html.Div(
            [
                "point size",
                dcc.Slider(
                    id="size_slider",
                    min=2,
                    max=30,
                    step=1,
                    value=16,
                    marks={
                        str(i): str(i) for i in ([2] + list(range(5, 31, 5)))
                    },
                ),
            ],
            style={"margin": "0 5vw", "margin-bottom": "2em"},
        ),
        html.Br(),
        html.H2(
            style={"color": "#3F51B5", "font-weight": "300"},
            children="Meet your microbial neighbours...",
        ),
        html.P(
            [
                html.P(
                    "The 5 persons that are the closest to you in the Bacteroidetes "
                    "and Firmicutes percentages are on average 42.2 years old and"
                    "have a BMI of 26."
                ),
                html.P("And here some more info:"),
            ],
            style={"font": "16px Lato", "color": "#777", "margin": "0 5vw"},
        ),
        html.Div(
            [
                info_field("dog", "5 of 5", "#3F51B5"),
                info_field("ambulance", "2 of 5", "#E91E63"),
            ],
            style={
                "display": "flex",
                "justify-content": "space-around",
                "flex-wrap": "wrap",
                "margin": "1em 5vw",
            },
        ),
    ],
)


@app.callback(
    dash.dependencies.Output("firm_slider", "max"),
    [dash.dependencies.Input("bac_slider", "value")],
    [dash.dependencies.State("firm_slider", "value")],
)
def update_firm(bac, firm):
    """Update the Firmicutes slider."""
    return 100 - bac


@app.callback(
    dash.dependencies.Output("bac_slider", "max"),
    [dash.dependencies.Input("firm_slider", "value")],
    [dash.dependencies.State("bac_slider", "value")],
)
def update_bac(firm, bac):
    """Update the Bacteroidetes slider."""
    return 100 - firm


@app.callback(
    dash.dependencies.Output("phyla_graph", "figure"),
    [
        dash.dependencies.Input("firm_slider", "value"),
        dash.dependencies.Input("bac_slider", "value"),
        dash.dependencies.Input("size_slider", "value"),
    ],
)
def update_figure(firm, bac, s):
    """Update the beta diversity figure."""
    best = find_closest(bac / 100, firm / 100, samples, n=5)
    close[:] = 0
    if best is not None:
        close[best] = 1
    return beta_figure(close, s)


if __name__ == "__main__":
    app.run_server(debug=True)
