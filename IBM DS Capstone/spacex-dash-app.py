import pandas as pd
import dash

from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px


# Load the dataset
spacex_df = pd.read_csv("spacex_launch_dash.csv")

min_payload = int(spacex_df["Payload Mass (kg)"].min())
max_payload = int(spacex_df["Payload Mass (kg)"].max())

launch_sites = sorted(spacex_df["Launch Site"].unique())

site_options = [
    {"label": "All Sites", "value": "ALL"}
]

for site in launch_sites:
    site_options.append({
        "label": site,
        "value": site
    })


# Create the Dash application
app = dash.Dash(__name__)


# Dashboard layout
app.layout = html.Div(
    children=[
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={
                "textAlign": "center",
                "color": "#503D36",
                "fontSize": "40px"
            }
        ),

        # TASK 1: Launch-site dropdown
        dcc.Dropdown(
            id="site-dropdown",
            options=site_options,
            value="ALL",
            placeholder="Select a Launch Site here",
            searchable=True,
            clearable=False,
            style={
                "width": "80%",
                "margin": "auto"
            }
        ),

        html.Br(),

        # TASK 2: Success pie chart
        html.Div(
            dcc.Graph(id="success-pie-chart")
        ),

        html.Br(),

        html.P(
            "Payload range (kg):",
            style={
                "fontSize": "18px",
                "fontWeight": "bold"
            }
        ),

        # TASK 3: Payload range slider
        dcc.RangeSlider(
            id="payload-slider",
            min=0,
            max=10000,
            step=1000,
            marks={
                value: f"{value:,}"
                for value in range(0, 10001, 1000)
            },
            value=[min_payload, max_payload],
            tooltip={
                "placement": "bottom",
                "always_visible": False
            }
        ),

        html.Br(),

        # TASK 4: Payload scatter chart
        html.Div(
            dcc.Graph(
                id="success-payload-scatter-chart"
            )
        )
    ],
    style={
        "maxWidth": "1200px",
        "margin": "auto",
        "padding": "20px"
    }
)


# TASK 2: Update the success pie chart
@app.callback(
    Output(
        component_id="success-pie-chart",
        component_property="figure"
    ),
    Input(
        component_id="site-dropdown",
        component_property="value"
    )
)
def update_pie_chart(selected_site):
    if selected_site == "ALL":
        success_by_site = (
            spacex_df.groupby(
                "Launch Site",
                as_index=False
            )["class"]
            .sum()
            .rename(
                columns={
                    "class": "Successful Launches"
                }
            )
        )

        figure = px.pie(
            success_by_site,
            values="Successful Launches",
            names="Launch Site",
            title="Total Successful Launches by Site"
        )

    else:
        selected_df = spacex_df[
            spacex_df["Launch Site"] == selected_site
        ]

        outcome_counts = (
            selected_df.groupby("class")
            .size()
            .reindex([0, 1], fill_value=0)
            .reset_index(name="Count")
        )

        outcome_counts["Outcome"] = (
            outcome_counts["class"].map({
                0: "Failed",
                1: "Successful"
            })
        )

        figure = px.pie(
            outcome_counts,
            values="Count",
            names="Outcome",
            title=f"Launch Outcomes for {selected_site}",
            color="Outcome",
            color_discrete_map={
                "Successful": "#00CC96",
                "Failed": "#EF553B"
            }
        )

    return figure


# TASK 4: Update the payload scatter chart
@app.callback(
    Output(
        component_id="success-payload-scatter-chart",
        component_property="figure"
    ),
    [
        Input(
            component_id="site-dropdown",
            component_property="value"
        ),
        Input(
            component_id="payload-slider",
            component_property="value"
        )
    ]
)
def update_scatter_chart(selected_site, payload_range):
    minimum_payload = payload_range[0]
    maximum_payload = payload_range[1]

    filtered_df = spacex_df[
        (
            spacex_df["Payload Mass (kg)"]
            >= minimum_payload
        )
        & (
            spacex_df["Payload Mass (kg)"]
            <= maximum_payload
        )
    ]

    if selected_site != "ALL":
        filtered_df = filtered_df[
            filtered_df["Launch Site"]
            == selected_site
        ]

        chart_title = (
            f"Payload vs. Launch Outcome "
            f"for {selected_site}"
        )

    else:
        chart_title = (
            "Payload vs. Launch Outcome "
            "for All Sites"
        )

    figure = px.scatter(
        filtered_df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        symbol="class",
        hover_data=[
            "Launch Site",
            "Booster Version",
            "Flight Number"
        ],
        title=chart_title,
        labels={
            "class": "Launch Outcome",
            "Payload Mass (kg)": "Payload Mass (kg)"
        }
    )

    figure.update_yaxes(
        tickmode="array",
        tickvals=[0, 1],
        ticktext=["Failure", "Success"]
    )

    return figure


# Run the application
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8050,
        debug=False
    )