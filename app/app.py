"""The American Gut App."""

import dash
import dash_daq as daq
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.figure_factory as ff
import numpy as np
import pandas as pd
from start import samples, find_closest, healthiest_sample, meta, describe, bact_plot, firm_plot


close = pd.Series(0, index=samples.index)
meta = meta[meta.sample_name.isin(samples.index)]
colors = pd.Series(["#3F51B5", "#E91E63", "#009688"])


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
                x=[healthiest_sample.PC1],
                y=[healthiest_sample.PC2],
                showlegend=False,
                text=[
                    "Bacteroidetes: %.1f%%<br />Firmicutes: %.1f%%"
                    % (
                        healthiest_sample["Bacteroidetes"] * 100,
                        healthiest_sample["Firmicutes"] * 100,
                    )
                ],
                mode="markers",
                marker={
                    "color": "#ab7be3",
                    "showscale": False,
                    "size": 1.1 * size,
                    "line": {"width": size / 3, "color": "#42056e"},
                    "opacity": 1.0,
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
           go.Scattergl(
                name="",
                x=[ns.PC1.mean()],
                y=[ns.PC2.mean()],
                showlegend=False,
                text=[
                    "Bacteroidetes: %.1f%%<br />Firmicutes: %.1f%%"
                    % (r["Bacteroidetes"] * 100, r["Firmicutes"] * 100)
                    for _, r in ns.iterrows()
                ],
                mode="markers",
                marker={
                    "color": "#32e382",
                    "showscale": False,
                    "size": 1.1 * size,
                    "line": {"width": size / 3, "color": "#07b556"},
                    "opacity": 1.0,
                },
            )
        ],
        "layout": go.Layout(
            title="Bray-Curtis PCoA",
            hovermode="closest",
            coloraxis={"cmin": -1, "cmax": 1},
        ),
    }


def info_fields(description):
    """Draw an info field."""
    if description.shape[0] == 0:
        return None
    description = description[~description.names.str.contains("Average")]
    description["color"] = colors[
        [i % len(colors) for i in range(description.shape[0])]
    ].values
    fields = [
        html.Div(
            [
                html.I(
                    className="fas fa-%s fa-2x" % row.icon,
                    style={
                        "vertical-align": "middle",
                        "padding": "0 8px",
                        "color": row["color"],
                    },
                ),
                html.Span(
                    "%d of %d" % (row["values"], sum(close == 1)),
                    style={
                        "font": "24px Lato",
                        "vertical-align": "middle",
                        "color": "#666",
                    },
                ),
            ],
            title=row["names"],
            style={"margin": "0.5em 2em"},
        )
        for _, row in description.iterrows()
    ]
    return fields


def info_text(description):
    return (
        "The 5 persons that are the closest to you in the Bacteroidetes "
        "and Firmicutes percentages are on average %.1f years old, "
        "have a BMI of %.1f and are %.1f cm tall."
        % (
            description[description.names == "Average age"]["values"],
            description[description.names == "Average BMI"]["values"],
            description[description.names == "Average height (cm)"]["values"],
        )
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
                    "Introduction:"
                ),
                html.P(
                    "The human gut is comprised primarily of two bacterial phyla, Firmicutes and Bacteroidetes. The ratio of these two bacteria in the gut have strong correlations to the diet, exercise, and potential obesity of a person. Understanding their relationship has important implications to our health. Input your distributions to see where you fall on the Bray-Curtis plot of 1000 random individuals from the American Gut Project."
                ),
                html.P("Legend:"),
                html.P(
                    "The green point is you!"
                ),
                html.P("Bluer points represent a higher ratio of Firmicutes."),
                html.P(
                    "Redder points represent a higher ratio of Bacteroidetes."
                ),
                html.P(
                    "Pink points show the 5 closest individuals to your distribution."
                ),
                html.P(
                    "The purple point represents the ideal distribution for a healthy individual."
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
              dcc.Graph(
            id="firmicutes_plot",
            figure=firm_plot(samples, .2, healthiest_sample),
            style={"height": "70vh", "margin": 0, "padding": 0},
                  
        ),
              dcc.Graph(
            id="bacteroidetes_plot",
            figure=bact_plot(samples, .4, healthiest_sample),
            style={"height": "70vh", "margin": 0, "padding": 0},
                  
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
                    "have a BMI of 26.",
                    id="info_text",
                ),
                html.P("And here some more info:"),
            ],
            style={"font": "16px Lato", "color": "#777", "margin": "0 5vw"},
        ),
        html.Div(
            None,
            style={
                "display": "flex",
                "justify-content": "start",
                "flex-wrap": "wrap",
                "margin": "1em 5vw",
            },
            id="info",
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
    [
        dash.dependencies.Output("phyla_graph", "figure"),
        dash.dependencies.Output("info", "children"),
        dash.dependencies.Output("info_text", "children"),
        dash.dependencies.Output("bacteroidetes_plot", "figure"),
        dash.dependencies.Output("firmicutes_plot", "figure"),

    ],
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
    description = describe(samples[close == 1], meta)
    return (
        beta_figure(close, s),
        info_fields(description),
        info_text(description),
        bact_plot(samples, bac/100, healthiest_sample),
        firm_plot(samples, firm/100, healthiest_sample)

    )


if __name__ == "__main__":
    app.run_server(debug=True)
