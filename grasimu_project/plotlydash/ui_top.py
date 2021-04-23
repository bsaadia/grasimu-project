# Stores the layout of the app
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

# APP LAYOUT LEVEL 1
# the style arguments for the sidebar. We use position:fixed and a fixed width
sidebar_style = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
content_style = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem"
}

# The links in the sidebar.
sidebar = html.Div(
    [
        html.H2("GRASIMU", className="display-4"),
        html.Hr(),
        html.P(
            "Configure and visualize your gravimetry survey.", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Target Configuration", href="/dashapp/page-1", id="page-1-link"),
                dbc.NavLink("Terrain Configuration", href="/dashapp/page-2", id="page-2-link"),
                dbc.NavLink("Survey Configuration", href="/dashapp/page-3", id="page-3-link"),
                dbc.NavLink("Visualization Dashboard", href="/dashapp/page-4", id="page-4-link"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=sidebar_style,
)
