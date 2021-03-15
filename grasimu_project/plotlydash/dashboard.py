"""Instantiate a Dash app."""
import json
import pandas as pd
import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from ..constructors import Scene
import dash_table
from plotly.subplots import make_subplots
import plotly.express as px


def init_dashboard(server):
    """Create a Plotly Dash dashboard."""
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/dashapp/',
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=False,
    )

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

    content = html.Div(id="page-content", style=content_style)
    dash_app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

    # this callback uses the current pathname to set the active state of the
    # corresponding nav link to true, allowing users to see what page they are on.
    @dash_app.callback(
        [Output(f"page-{i}-link", "active") for i in range(1, 4)],
        [Input("url", "pathname")],
    )
    def toggle_active_links(pathname):
        if pathname == "/dashapp/":
            # Treat page 1 as the homepage / index
            return True, False, False
        return [pathname == f"/dashapp/page-{i}" for i in range(1, 4)]

    # APP LAYOUT LEVEL 2
    # Page 1 content, where the user configures their target.

    mesh_plot_card = dbc.Card(
        [
            dbc.CardHeader("3D Mesh Plot"),
            dbc.CardBody(
                [
                    dcc.Graph(id='target_mesh_plot')
                ]
            )
        ]
    )

    mesh_opts_card = dbc.Card([
        dbc.CardHeader("Mesh Setup"),
        dbc.CardBody([
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        dbc.FormGroup([
                            dbc.Label('Select Geometry'),
                            dbc.RadioItems(id='target_geometry_radio',
                                           options=[
                                               {'label': "Sphere", 'value': 'sphere'},
                                               {'label': "Cylinder", 'value': 'cylinder'},
                                               {'label': "Custom .stl", 'value': 'custom'},
                                           ],
                                           persistence=True),

                        ]),

                    ]),
                    dbc.Col([
                        dbc.FormGroup([
                            dbc.Label('Radius'),
                            dbc.InputGroup([
                                dbc.Input(id='radius_comp_input', type='number', persistence=True,
                                          disabled=True),
                                dbc.InputGroupAddon("metres", addon_type="append")
                            ]),
                        ]),

                        dbc.FormGroup([
                            dbc.Label('Length'),
                            dbc.InputGroup([
                                dbc.Input(id='length_comp_input', type='number', persistence=True,
                                          disabled=True),
                                dbc.InputGroupAddon("metres", addon_type="append")
                            ]),

                        ])

                    ]),
                ]),
                dbc.Label('Mesh Position'),
                dbc.Row([
                    dbc.Col([
                        dbc.FormGroup([
                            dbc.InputGroup([
                                dbc.InputGroupAddon("x", addon_type="prepend"),
                                dbc.Input(id='cen_x_input', type='number', persistence=True,
                                          disabled=False),
                            ]),

                        ]),

                    ]),
                    dbc.Col([
                        dbc.FormGroup([
                            dbc.InputGroup([
                                dbc.InputGroupAddon("y", addon_type="prepend"),
                                dbc.Input(id='cen_y_input', type='number', persistence=True,
                                          disabled=False),
                            ]),

                        ]),

                    ]),
                    dbc.Col([
                        dbc.FormGroup([
                            dbc.InputGroup([
                                dbc.InputGroupAddon("z", addon_type="prepend"),
                                dbc.Input(id='cen_z_input', type='number', persistence=True,
                                          disabled=False),
                            ]),
                            dbc.FormText('Negative value for depth, e.g. -10 m.'),
                        ]),

                    ]),

                ], form=True),
                dbc.FormGroup([
                    dbc.Label("File Path for custom *.stl"),
                    dbc.Input(id='target_upload_path',
                              placeholder="e.g., /home/user/mesh_files/mesh.stl",
                              type="text",
                              disabled=True),
                    dbc.FormText("Filename must include .stl"),
                ]),
                dbc.FormGroup([
                    dbc.Button('Render Mesh',
                               id='target_render_button',
                               color='primary',
                               size='lg',
                               outline=True,
                               block=True)

                ]),

            ]),

        ]),

    ])

    vox_plot_card = dbc.Card(
        [
            dbc.CardHeader("3D Voxel Plot"),
            dbc.CardBody(
                [
                    dcc.Graph(id='target_voxel_plot')
                ]
            )
        ]
    )

    vox_opts_card = dbc.Card([
        dbc.CardHeader("Voxel Setup"),
        dbc.CardBody([
            dbc.FormGroup([
                dbc.Label('Voxel Resolution'),
                dbc.InputGroup([
                    dbc.Input(id='voxel_resolution_input', type='number', persistence=True,
                              disabled=False),
                    dbc.InputGroupAddon("metres", addon_type="append")
                ]),
                dbc.FormText("Size of each cubic voxel along its 3 dimensions.")
            ]),
            dbc.FormGroup([
                dbc.Button('Voxelize Mesh',
                           id='voxel_button',
                           color='primary',
                           size='lg',
                           outline=True,
                           block=True,
                           disabled=True),
                dbc.FormText("No mesh in memory.",
                             id='voxel_button_text')
            ]),
        ])
    ])

    target_grav_plot_card = dbc.Card(
        [
            dbc.CardHeader("Gravity at Surface (z=0)"),
            dbc.CardBody(
                [
                    dcc.Graph(id='target_grav_plot')
                ]
            )
        ]
    )

    target_grav_opts_card = dbc.Card([
        dbc.CardHeader(" "),
        dbc.CardBody([
            dbc.FormGroup([
                dbc.Label('Gravity Station Spacing'),
                dbc.InputGroup([
                    dbc.Input(id='calculation_resolution_input', type='number', persistence=True,
                              disabled=False),
                    dbc.InputGroupAddon("metres", addon_type="append")
                ]),
                dbc.FormText(
                    "Spacing between calculation points.")
            ]),
            dbc.FormGroup([
                dbc.Label('Target Density Contrast'),
                dbc.InputGroup([
                    dbc.Input(id='density_input', type='number', persistence=True,
                              disabled=False),
                    dbc.InputGroupAddon("kg/m^3", addon_type="append")
                ]),

            ]),
            dbc.FormGroup([
                dbc.Label('Extent modelling area by a factor of'),
                dcc.Slider(
                    id='calculation_extent',
                    min=1.5,
                    max=5,
                    step=None,
                    marks={
                        1.5: '1.5x',
                        3: '3x',
                        5: '5x',
                    },
                    value=1.5,
                ),
            ]),

            dbc.FormGroup([
                dbc.Button('Calculate Gravity',
                           id='gravity_button',
                           color='primary',
                           size='lg',
                           outline=True,
                           block=True,
                           disabled=True),
                dbc.FormText("No voxel model in memory.",
                             id='gravity_button_text')
            ]),
        ])
    ])

    mesh_cards = dbc.CardGroup([
        mesh_plot_card,
        mesh_opts_card
    ])

    vox_cards = dbc.CardGroup([
        vox_plot_card,
        vox_opts_card
    ])

    target_grav_cards = dbc.CardGroup([
        target_grav_plot_card,
        target_grav_opts_card
    ])

    target_header = html.Div([html.H1(children='Target Configuration'),
                              html.Hr()])

    target_layout = html.Div(children=[target_header,
                                       mesh_cards,
                                       vox_cards,
                                       target_grav_cards])

    # Page 2 content, where the user configures the terrain parameters.

    terrain_plot_card = dbc.Card(
        [
            dbc.CardHeader(
                dbc.Tabs([
                    dbc.Tab(label="3D Surface", tab_id="terrain_tab_1"),
                    dbc.Tab(label="2D Raster", tab_id="terrain_tab_2")
                ], id='terrain_tabs', card=True, active_tab='terrain_tab_1')
            ),
            dbc.CardBody(
                [
                    dbc.Col([
                        dbc.Label("Digital Terrain Model"),
                        dcc.Graph(id='terrain_plot'),

                    ])
                ]
            )
        ]
    )

    terrain_opts_card = dbc.Card([
        dbc.CardHeader("Synthetic Terrain Generation (DTM)"),
        dbc.CardBody([
            dbc.Col([
                dbc.FormGroup([
                    dbc.Label('Select Autocorrelation Function for Random Terrain Generator'),
                    dcc.Dropdown(id='terrain_dropdown',
                                 options=[
                                     {'label': "Gaussian", 'value': 1},
                                     {'label': "Exponential", 'value': 2},
                                     {'label': "Zero-Mean Exponential", 'value': 3},
                                     {'label': "Anisotropic", 'value': 4},
                                     {'label': "von Karman", 'value': 5},
                                     {'label': "Custom From File", 'value': 6}
                                 ],
                                 persistence=True),

                ]),
            ]),
            dbc.Col([
                dbc.FormGroup([
                    dbc.Label('Seed'),
                    dbc.InputGroup([
                        dbc.Input(id='seed_input', type='number', persistence=True,
                                  disabled=False),
                    ]),
                    dbc.FormText("Must be negative value.")
                ]),
            ]),

            dbc.Col([
                dbc.Label('Correlation Length'),
                dbc.Row([
                    dbc.Col([
                        dbc.FormGroup([
                            dbc.InputGroup([
                                dbc.InputGroupAddon("x", addon_type="prepend"),
                                dbc.Input(id='corr_x_input', type='number', persistence=True,
                                          disabled=False),
                                dbc.InputGroupAddon("metres", addon_type="append"),

                            ]),

                        ]),

                    ]),
                    dbc.Col([
                        dbc.FormGroup([
                            dbc.InputGroup([
                                dbc.InputGroupAddon("y", addon_type="prepend"),
                                dbc.Input(id='corr_y_input', type='number', persistence=True,
                                          disabled=False),
                                dbc.InputGroupAddon("metres", addon_type="append"),

                            ]),

                        ]),

                    ]),

                ], form=True),
                dbc.Label("Elevation Bounds"),
                dbc.Row([
                    dbc.Col([
                        dbc.FormGroup([
                            dbc.InputGroup([
                                dbc.InputGroupAddon("max", addon_type="prepend"),
                                dbc.Input(id='max_input', type='number', persistence=True,
                                          disabled=False),
                                dbc.InputGroupAddon("metres", addon_type="append"),

                            ]),

                        ]),

                    ]),
                    dbc.Col([
                        dbc.FormGroup([
                            dbc.InputGroup([
                                dbc.InputGroupAddon("min", addon_type="prepend"),
                                dbc.Input(id='min_input', type='number', persistence=True,
                                          disabled=False),
                                dbc.InputGroupAddon("metres", addon_type="append"),

                            ]),

                        ]),

                    ]),

                ], form=True),
                dbc.FormGroup([
                    dbc.Label("File Path to Custom DTM"),
                    dbc.Input(id='terrain_upload_path',
                              placeholder="e.g., /home/user/terrain_files/terrain.txt",
                              type="text",
                              disabled=True),
                    dbc.FormText("Filename must include .txt"),
                ]),
                dbc.FormGroup([
                    dbc.Button('Generate DTM',
                               id='terrain_button',
                               color='primary',
                               size='lg',
                               outline=True,
                               block=True)

                ]),

            ]),

        ]),

    ])

    dem_plot_card = dbc.Card(
        [
            dbc.CardHeader(
                dbc.Tabs([
                    dbc.Tab(label="3D Surface", tab_id="dem_tab_1"),
                    dbc.Tab(label="2D Raster", tab_id="dem_tab_2")
                ], id='dem_tabs', card=True, active_tab='dem_tab_1')
            ),
            dbc.CardBody(
                [
                    dbc.Col([
                        dbc.Label("Digital Terrain Model Plus Uncertainty"),
                        dcc.Graph(id='dem_plot')
                    ]),
                ]
            )
        ]
    )

    dem_opts_card = dbc.Card([
        dbc.CardHeader("Synthetic Terrain Generation Plus Uncertainty (DTM+)"),
        dbc.CardBody([
            dbc.FormGroup([
                dbc.Label('DTM Uncertainty'),
                dbc.InputGroup([
                    dbc.Input(id='dem_input', type='number', persistence=True,
                              disabled=False, value=10),
                    dbc.InputGroupAddon("metres", addon_type="append")
                ]),
                dbc.FormText("Maximum error between ground truth terrain and DTM. Note that the ground truth terrain "
                             "surface colour scale will change to match DTM color scale for clarity.")
            ]),
            dbc.FormGroup([
                dbc.Button('Generate DTM+',
                           id='dem_button',
                           color='primary',
                           size='lg',
                           outline=True,
                           block=True,
                           disabled=True),
                dbc.FormText("No terrain surface in memory.",
                             id='dem_button_text')
            ]),
        ])
    ])

    tgrav_plot_card = dbc.Card(
        [
            dbc.CardHeader(
                dbc.Tabs([
                    dbc.Tab(label="DTM Gravity", tab_id="tgrav_tab_1"),
                    dbc.Tab(label="DTM+ Gravity", tab_id="tgrav_tab_2")
                ], id='tgrav_tabs', card=True, active_tab='tgrav_tab_1')
            ),
            dbc.CardBody(
                [
                    dbc.Col([
                        dbc.Label("Terrain Gravity"),
                        dcc.Graph(id='tgrav_plot')
                    ]),
                ]
            )
        ]
    )

    tgrav_opts_card = dbc.Card([
        dbc.CardHeader("Terrain Gravity Setup"),
        dbc.CardBody([
            dbc.FormGroup([
                dbc.Label('Terrain Density'),
                dbc.InputGroup([
                    dbc.Input(id='t_density_input', type='number', persistence=True,
                              disabled=False, value=2700),
                    dbc.InputGroupAddon("kg/m^3", addon_type="append")
                ]),
                dbc.FormText("Density of the terrain, including the material surrounding the voxel model.")
            ]),
            dbc.FormGroup([
                dbc.Button('Calculate Terrain Gravity',
                           id='tgrav_button',
                           color='primary',
                           size='lg',
                           outline=True,
                           block=True,
                           disabled=True),
                dbc.FormText("No DTM+ in memory.",
                             id='tgrav_button_text')
            ]),
        ])
    ])

    terrain_header = html.Div([html.H1(children='Terrain Configuration'),
                               html.Hr()])

    terrain_cards = dbc.CardGroup([
        terrain_plot_card,
        terrain_opts_card,
    ])

    dem_cards = dbc.CardGroup([
        dem_plot_card,
        dem_opts_card
    ])

    tgrav_cards = dbc.CardGroup([
        tgrav_plot_card,
        tgrav_opts_card
    ])

    cmap_holder = html.Div(id='cmap_holder', hidden=True)

    terrain_layout = html.Div(children=[terrain_header,
                                        terrain_cards,
                                        dem_cards,
                                        tgrav_cards,
                                        cmap_holder])

    # Page 3 Content, where the user specifies the survey configuration
    survey_header = html.Div([html.H1(children='Survey Configuration'),
                              html.Hr()])

    survey_plot_card = dbc.Card(
        [
            dbc.CardHeader("Click on pink shaded area to create gravity stations."),
            dbc.CardBody(
                [
                    dcc.Graph(id='survey_pick_plot'),
                ]
            )
        ]
    )

    survey_opts_card = dbc.Card([
        dbc.CardHeader([
            "Custom Survey Path"
        ]),
        dbc.CardBody([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        dbc.Button('Configure Grid Layout',
                                   id='grid_display_button',
                                   color='link'),
                    ),
                    dbc.Collapse(
                        dbc.CardBody([
                            dbc.Label('Grid Spacing'),
                            dbc.Row([
                                dbc.Col([
                                    dbc.FormGroup([
                                        dbc.InputGroup([
                                            dbc.InputGroupAddon("x", addon_type="prepend"),
                                            dbc.Input(id='grid_x_input', type='number', value=10,
                                                      disabled=False),
                                            dbc.InputGroupAddon("metres", addon_type="append"),

                                        ]),

                                    ]),

                                ]),
                                dbc.Col([
                                    dbc.FormGroup([
                                        dbc.InputGroup([
                                            dbc.InputGroupAddon("y", addon_type="prepend"),
                                            dbc.Input(id='grid_y_input', type='number', value=10,
                                                      disabled=False),
                                            dbc.InputGroupAddon("metres", addon_type="append"),

                                        ]),

                                    ]),

                                ]),

                            ], form=True),
                            dbc.FormGroup([
                                dcc.Graph(id='grid_plot'),
                                dbc.FormText("Click and drag to select grid extent in x and y. Possible points are "
                                             "limited by grid spacing.")
                            ]),
                            dbc.FormGroup([
                                dbc.Button('Add Grid',
                                           id='add_grid_button',
                                           color='primary',
                                           size='lg',
                                           outline=True,
                                           block=True,
                                           disabled=False),
                                dbc.FormText("Add a grid of points to the survey design.")
                            ]),

                        ]),
                        id='grid_collapse',
                        is_open=False
                    )
                ]),
                dbc.Card([
                    dbc.CardHeader(
                        dbc.Button('Configure Spiral Layout',
                                   id='spiral_display_button',
                                   color='link'),
                    ),
                    dbc.Collapse(
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.FormGroup([
                                        dbc.Label('Number of Turns'),
                                        dbc.InputGroup([
                                            dbc.Input(id='turns_input', type='number', persistence=True,
                                                      disabled=False),
                                        ]),

                                    ]),

                                ]),
                                dbc.Col([
                                    dbc.FormGroup([
                                        dbc.Label('Number of Points'),
                                        dbc.InputGroup([
                                            dbc.Input(id='points_input', type='number', persistence=True,
                                                      disabled=False),

                                        ]),

                                    ]),

                                ]),

                            ], form=True),
                            dbc.FormGroup([
                                dbc.Button('Add Spiral',
                                           id='add_spiral_button',
                                           color='primary',
                                           size='lg',
                                           outline=True,
                                           block=True,
                                           disabled=False),
                                dbc.FormText("Add a spiral of points to the survey design.")
                            ]),

                        ]),
                        id='spiral_collapse',
                        is_open=False
                    )
                ]),
                dbc.Card([
                    dbc.CardHeader(
                        dbc.Button('View Point Locations',
                                   id='points_display_button',
                                   color='link'),
                    ),
                    dbc.Collapse(
                        dbc.CardBody([
                            dbc.Label('Click in a cell to change the coordinate.'),
                            dash_table.DataTable(id='survey_table',
                                                 columns=[{
                                                     'name': a,
                                                     'id': 'column_{}'.format(i),
                                                 } for a, i in zip(['x', 'y', 'z'], range(1, 4))],
                                                 data=list(),
                                                 editable=True,
                                                 fixed_rows={'headers': True},
                                                 style_table={'height': '250px', 'overflowY': 'auto'})
                        ]),
                        id='points_collapse',
                        is_open=False
                    )
                ]),

            ]),
        ]),
        dbc.CardFooter([
            dbc.FormGroup([
                dbc.Button('Delete Survey',
                           id='new_survey_button',
                           color='danger',
                           size='sm',
                           outline=True,
                           block=True),
                dbc.FormText("WARNING: This will delete the survey points.")
            ]),

        ])
    ])

    instrument_plot_card = dbc.Card(
        [
            dbc.CardHeader(
                dbc.Tabs([
                    dbc.Tab(label="Gravity+ for Full Survey", tab_id="survey_tab_1"),
                    dbc.Tab(label="Gravity+ for Full Survey no terrain", tab_id="survey_tab_2")
                ], id='survey_tabs', card=True, active_tab='survey_tab_1')
            ),
            dbc.CardBody(
                [
                    dbc.Col([
                        dcc.Graph(id='survey_plot')
                    ]),
                ]
            )
        ]
    )

    instrument_opts_card = dbc.Card([
        dbc.CardHeader("Survey Uncertainties"),
        dbc.CardBody([
            dbc.FormGroup([
                dbc.Label('Gravimeter Uncertainty'),
                dbc.InputGroup([
                    dbc.Input(id='grav_err_input', type='number', persistence=True,
                              disabled=False, value=10),
                    dbc.InputGroupAddon("milligals", addon_type="append")
                ]),
                dbc.FormText("Maximum error of gravimeter.")
            ]),
            dbc.FormGroup([
                dbc.Label('Station Location Uncertainty'),
                dbc.InputGroup([
                    dbc.Input(id='gps_err_input', type='number', persistence=True,
                              disabled=False, value=10),
                    dbc.InputGroupAddon("metres", addon_type="append")
                ]),
                dbc.FormText("Maximum error of horizontal survey location.")
            ]),
            dbc.FormGroup([
                dbc.Button('Calculate Gravity+',
                           id='simulate_button',
                           color='primary',
                           size='lg',
                           outline=True,
                           block=True,
                           disabled=False),
                dbc.FormText("Click to calculate gravity for full station coverage and including gravimeter and "
                             "location uncertainties.")
            ]),
        ])
    ])

    interp_plot_card = dbc.Card(
        [
            dbc.CardHeader(
                dbc.Tabs([
                    dbc.Tab(label="Gravity+ from Survey with DTM Gravity", tab_id="interp_tab_1"),
                    dbc.Tab(label="Gravity+ from Survey", tab_id="interp_tab_2")
                ], id='interp_tabs', card=True, active_tab='interp_tab_1')
            ),
            dbc.CardBody(
                [
                    dbc.Col([
                        dcc.Graph(id='interp_plot')
                    ]),
                ]
            )
        ]
    )

    interp_opts_card = dbc.Card([
        dbc.CardHeader("Interpolation Setup"),
        dbc.CardBody([
            dbc.FormGroup([
                dbc.Label("Interpolation Method"),
                dbc.RadioItems(id='sip_radio',
                               options=[
                                   {'label': "Linear", 'value': 'linear'},
                                   {'label': "Cubic", 'value': 'cubic'},
                                   {'label': "Nearest-Neighbour", 'value': 'nearest'},
                               ],
                               persistence=True),

            ]),
            dbc.FormGroup([
                dbc.Button('Calculate Gravity+ from Survey Points',
                           id='interp_button',
                           color='primary',
                           size='lg',
                           outline=True,
                           block=True,
                           disabled=True),
                dbc.FormText("No survey points in memory.",
                             id='interp_button_text')
            ]),
        ])
    ])

    instrument_cards = dbc.CardGroup([
        instrument_plot_card,
        instrument_opts_card
    ])

    survey_cards = dbc.CardGroup([
        survey_plot_card,
        survey_opts_card
    ])

    interp_cards = dbc.CardGroup([
        interp_plot_card,
        interp_opts_card
    ])

    click_data = html.Div(id='click_data', hidden=True)
    count_data = html.Div(id='count_data', hidden=True)

    survey_layout = html.Div(children=[survey_header,
                                       instrument_cards,
                                       survey_cards,
                                       interp_cards,
                                       click_data,
                                       count_data])

    # Page 4 content, where the visualization dashboard is given
    vis_plots = dbc.CardGroup([
        dbc.Card([
            dbc.CardHeader("Target Gravity"),
            dbc.CardBody([
                dcc.Graph(id='vis_target_plot')
            ])
        ]),
        dbc.Card([
            dbc.CardHeader("Complete Gravity"),
            dbc.CardBody([
                dcc.Graph(id='vis_full_plot')
            ])
        ]),
        dbc.Card([
            dbc.CardHeader("Complete Gravity+"),
            dbc.CardBody([
                dcc.Graph(id='vis_raw_plot'),
                dbc.FormGroup([
                    dbc.Label("Apply Correction"),
                    dbc.Checklist(id='correction_radio',
                                  options=[
                                      {'label': "Free Air Correction", 'value': 0},
                                      {'label': "Terrain Correction", 'value': 1},
                                  ],
                                  persistence=True),
                    dbc.FormText("Note that the terrain correction is "
                                 "calculated from DTM+ because it is assumed that the DTM is not "
                                 "known.")

                ]),
            ])
        ]),
    ])

    vis_slice = dbc.CardGroup([
        dbc.Card([
            dbc.CardHeader("2D Cross Section View"),
            dbc.CardBody([
                dbc.Checklist(id='vis_target_toggle',
                              options=[
                                  {'label': 'Plot Target Gravity', 'value': 0}
                              ], inline=True, switch=True),
                dcc.Graph(id='vis_xy_plot'),
            ])
        ]),
        dbc.Card([
            dbc.CardHeader("Select Cross Section"),
            dbc.CardBody([
                dbc.FormGroup([
                    dcc.Dropdown(
                        id='vis_slice_dropdown',
                        options=[
                            {'label': 'Survey: Target Gravity', 'value': 0},
                            {'label': 'Survey: Complete Gravity', 'value': 1},
                            {'label': 'Survey: Complete Gravity+', 'value': 2},
                            {'label': 'Survey: Complete Gravity+, corrected', 'value': 12},
                            {'label': 'All: Target Gravity', 'value': 3},
                            {'label': 'All: Complete Gravity', 'value': 4},
                            {'label': 'All: Complete Gravity+', 'value': 5},
                            {'label': 'All: Complete Gravity+, corrected', 'value': 13},
                            {'label': 'DTM Gravity', 'value': 6},
                            {'label': 'DTM+ Gravity', 'value': 7},
                            {'label': 'Free Air Correction', 'value': 8},
                            {'label': 'Terrain Correction', 'value': 9},
                            {'label': 'DTM Elevation', 'value': 10},
                            {'label': 'DTM+ Elevation', 'value': 11},
                        ],
                        value=0,
                        placeholder="Select plot for 2D cross section extraction.",
                        clearable=False
                    ),
                    dbc.FormText("Click anywhere on the plot to display the N-S (y) and E-W (x) cross sections.")
                ]),

                dcc.Graph(id='vis_slice_plot')
            ])
        ])
    ])

    vis_parent = dbc.Card([
        dbc.CardHeader([
            dbc.Row([
                dbc.Col([
                    dbc.Tabs([
                        dbc.Tab(label="Survey Points", tab_id="vis_tab_1"),
                        dbc.Tab(label="All Points", tab_id="vis_tab_2")
                    ], id='vis_tabs', card=True, active_tab='vis_tab_1')
                ]),
            ]),
        ]),
        dbc.CardBody([
            vis_plots,
        ]),
    ])

    vis_3d = dbc.Card([
        dbc.CardHeader([
            dbc.Button('Toggle Model Overview',
                       id='vis_3d_button',
                       color='link')
        ]),
        dbc.Collapse(
            dbc.CardBody([
                dbc.CardGroup([
                    dbc.Card([
                        dbc.CardHeader(
                            dbc.Tabs([
                                dbc.Tab(label="Mesh with DTM", tab_id="sum_tab_1"),
                                dbc.Tab(label="Voxel with DTM", tab_id="sum_tab_2")
                            ], id='sum_tabs', card=True, active_tab='sum_tab_1')
                        ),
                        dbc.CardBody([
                            dcc.Graph(id='vis_3d_plot')
                        ])
                    ]),
                    dbc.Card([
                        dbc.CardHeader("Parameter list"),
                        dbc.CardBody(id='vis_table')
                    ])

                ])
            ]),
            id='vis_collapse', is_open=False)
    ])

    vis_click_data = html.Div(id='vis_click_data', hidden=True)

    vis_download_modal = html.Div([
        dbc.Button('Download Raw Data',
                   id='vis_dl_button',
                   color='info',
                   size='lg',
                   outline=True,
                   block=True,
                   disabled=False),
        dbc.Modal([
            dbc.ModalHeader([
                "Download Raw Data"
            ]),
            dbc.ModalBody([
                dbc.Label("Check the items you wish to download."),
                dbc.FormGroup([
                    dbc.Checklist(
                        id='vis_dl_checkbox',
                        options=[
                            {'label': 'Survey: Target Gravity', 'value': 0},
                            {'label': 'Survey: Complete Gravity', 'value': 1},
                            {'label': 'Survey: Complete Gravity+', 'value': 2},
                            {'label': 'Survey: Complete Gravity+, corrected', 'value': 12},
                            {'label': 'All: Target Gravity', 'value': 3},
                            {'label': 'All: Complete Gravity', 'value': 4},
                            {'label': 'All: Complete Gravity+', 'value': 5},
                            {'label': 'All: Complete Gravity+, corrected', 'value': 13},
                            {'label': 'DTM Gravity', 'value': 6},
                            {'label': 'DTM+ Gravity', 'value': 7},
                            {'label': 'Free Air Correction', 'value': 8},
                            {'label': 'Terrain Correction', 'value': 9},
                            {'label': 'DTM Elevation', 'value': 10},
                            {'label': 'DTM+ Elevation', 'value': 11},
                        ],
                    ),
                ]),
                dbc.FormGroup([
                    dbc.Input(id='vis_path_input',
                              placeholder="e.g., /home/user/downloads/",
                              type="text",
                              disabled=False),
                    dbc.FormText(
                        "Path to where the .txt file(s) will be saved. Note that .png files of any plot "
                        "can be saved by clicking the camera icon that appears when hovering over the "
                        "plot."),

                ]),

            ]),
            dbc.ModalFooter([
                dbc.Button("Close",
                           id="vis_close_button",
                           size='sm'),
                dbc.Button("Download",
                           id="vis_save_button",
                           color='primary',
                           size='sm'),
            ])],
            id="vis_download_modal",
            size='lg'
        ),

    ])

    vis_header = html.Div([
        dbc.Row([
            dbc.Col([
                html.H1(children='Visualization Dashboard')
            ], width=6),
            dbc.Col([
                dbc.Button('Load Data',
                           id='vis_button',
                           color='primary',
                           size='lg',
                           outline=True,
                           block=True,
                           disabled=False),
            ]),
            dbc.Col([

                vis_download_modal
            ])

        ]),
        html.Hr()
    ])

    # vis_header = html.Div([html.H1(children='Visualization Dashboard'),
    #                        html.Hr()])

    vis_layout = html.Div([vis_header,
                           vis_3d,
                           vis_parent,
                           vis_slice,
                           vis_click_data])

    sc = Scene('scene1')

    @dash_app.callback([Output('target_mesh_plot', 'figure'),
                        Output('voxel_button', 'disabled'),
                        Output('voxel_button_text', 'children')],
                       Input('target_render_button', 'n_clicks'),
                       [State('target_upload_path', 'value'),
                        State('target_geometry_radio', 'value'),
                        State('radius_comp_input', 'value'),
                        State('length_comp_input', 'value'),
                        State('cen_x_input', 'value'),
                        State('cen_y_input', 'value'),
                        State('cen_z_input', 'value')],
                       prevent_initial_call=True)
    def render_mesh(click, path, mode, radius, length, x0, y0, z0):
        voxel_button_status = True
        voxel_button_text = "No mesh in memory."

        if mode == 'custom':
            file_path = path
            target_shape = None
        else:
            file_path = None
            target_shape = mode

        sc.render_mesh(centre_depth=z0,
                       centre_x=x0,
                       centre_y=y0,
                       path=file_path,
                       shape=target_shape,
                       radius=radius,
                       length=length)

        if click > 0:
            voxel_button_status = False
            voxel_button_text = "Click to voxelize the mesh displayed in the 3D Mesh Plot."

        mesh_fig = go.Figure(data=go.Mesh3d(x=sc.target_geometry['mesh']['vertices'][:, 0],
                                            y=sc.target_geometry['mesh']['vertices'][:, 1],
                                            z=sc.target_geometry['mesh']['vertices'][:, 2],
                                            i=sc.target_geometry['mesh']['indices'][:, 0],
                                            j=sc.target_geometry['mesh']['indices'][:, 1],
                                            k=sc.target_geometry['mesh']['indices'][:, 2]))

        mesh_fig.update_scenes(aspectmode='data')

        return mesh_fig, voxel_button_status, voxel_button_text

    @dash_app.callback([Output('target_voxel_plot', 'figure'),
                        Output('gravity_button', 'disabled'),
                        Output('gravity_button_text', 'children')],
                       Input('voxel_button', 'n_clicks'),
                       State('voxel_resolution_input', 'value'),
                       prevent_initial_call=True)
    def voxelize_mesh(click, resolution):
        gravity_button_status = True
        gravity_button_text = "No voxel model in memory."

        sc.voxelize_mesh(resolution=resolution)

        vox_fig = go.Figure(data=go.Mesh3d(x=sc.target_geometry['voxel']['vertices'][:, 0],
                                           y=sc.target_geometry['voxel']['vertices'][:, 1],
                                           z=sc.target_geometry['voxel']['vertices'][:, 2],
                                           i=sc.target_geometry['voxel']['indices'][:, 0],
                                           j=sc.target_geometry['voxel']['indices'][:, 1],
                                           k=sc.target_geometry['voxel']['indices'][:, 2]))

        vox_fig.add_trace(go.Scatter3d(x=sc.target_geometry['wireframe'][0],
                                       y=sc.target_geometry['wireframe'][1],
                                       z=sc.target_geometry['wireframe'][2],
                                       mode='lines',
                                       line=dict(color='rgb(70,70,70)', width=1)))

        vox_fig.update_scenes(aspectmode='data')

        if click > 0:
            gravity_button_status = False
            gravity_button_text = "Click to calculate gravity at z=0"

        return vox_fig, gravity_button_status, gravity_button_text

    @dash_app.callback(Output('target_grav_plot', 'figure'),
                       Input('gravity_button', 'n_clicks'),
                       [State('calculation_resolution_input', 'value'),
                        State('density_input', 'value'),
                        State('calculation_extent', 'value')],
                       prevent_initial_call=True)
    def plot_perfect_gravity(click, resolution, density, extent_multiplier):
        sc.create_datum(resolution=resolution,
                        extent_multiplier=extent_multiplier)
        sc.calculate_target_gravity(density_contrast=density, with_terrain=False)

        perfect_fig = go.Figure(go.Heatmap(x=sc.data['perfect_gravity']['target'][0],
                                           y=sc.data['perfect_gravity']['target'][1],
                                           z=sc.data['perfect_gravity']['target'][2],
                                           colorbar_title="milligal"))

        return perfect_fig

    @dash_app.callback([Output('terrain_plot', 'figure'),
                        Output('dem_button', 'disabled'),
                        Output('dem_button_text', 'children')],
                       [Input('terrain_button', 'n_clicks'),
                        Input('terrain_tabs', 'active_tab'),
                        Input('cmap_holder', 'children')],
                       [State('seed_input', 'value'),
                        State('corr_x_input', 'value'),
                        State('corr_y_input', 'value'),
                        State('max_input', 'value'),
                        State('min_input', 'value'),
                        State('terrain_upload_path', 'value'),
                        State('terrain_dropdown', 'value')],
                       prevent_initial_call=True)
    def plot_terrain(click, tab, cmap_dump, seed, corr_x, corr_y, max_in, min_in, path, method):
        ctx = dash.callback_context
        dem_button_status = True
        dem_button_text = "No terrain surface in memory."
        if ctx.triggered[0]['prop_id'].split('.')[0] == 'terrain_button':
            sc.generate_terrain(seed=seed,
                                method=method,
                                x_corr_len=corr_x,
                                y_corr_len=corr_y,
                                max_elevation=max_in, min_elevation=min_in)

        if click is None and ctx.triggered[0]['prop_id'].split('.')[0] == 'terrain_tabs':
            return None, None, None
        else:
            if cmap_dump:
                cmap_load = json.loads(cmap_dump)
                zmin = cmap_load[0]
                zmax = cmap_load[1]
            else:
                zmin = np.min(sc.data['elevation']['terrain'][2])
                zmax = np.max(sc.data['elevation']['terrain'][2])

            dem_button_status = False
            dem_button_text = "Click to generate DTM surface."
            raster_attrs = dict(x=sc.data['elevation']['terrain'][0],
                                y=sc.data['elevation']['terrain'][1],
                                z=sc.data['elevation']['terrain'][2],
                                colorbar_title="metres",
                                colorscale='Viridis',
                                zmin=zmin, zmax=zmax)
            surface_attrs = dict(x=sc.scene_properties['datum'][0],
                                 y=sc.scene_properties['datum'][1],
                                 z=sc.data['elevation']['terrain'][3],
                                 colorbar_title="metres",
                                 colorscale='Viridis',
                                 cmin=zmin, cmax=zmax)

            if tab == 'terrain_tab_2':
                fig_data = go.Heatmap(raster_attrs)
            elif tab == 'terrain_tab_1':
                fig_data = go.Surface(surface_attrs)
                vox_data = [go.Mesh3d(x=sc.target_geometry['voxel']['vertices'][:, 0],
                                      y=sc.target_geometry['voxel']['vertices'][:, 1],
                                      z=sc.target_geometry['voxel']['vertices'][:, 2],
                                      i=sc.target_geometry['voxel']['indices'][:, 0],
                                      j=sc.target_geometry['voxel']['indices'][:, 1],
                                      k=sc.target_geometry['voxel']['indices'][:, 2],
                                      color='rgb(77,81,255)'),
                            go.Scatter3d(x=sc.target_geometry['wireframe'][0],
                                         y=sc.target_geometry['wireframe'][1],
                                         z=sc.target_geometry['wireframe'][2],
                                         mode='lines',
                                         line=dict(color='rgb(70,70,70)', width=1))]

            terrain_fig = go.Figure(fig_data)
            terrain_fig.update_layout(yaxis=dict(scaleanchor='x'),
                                      xaxis=dict(scaleanchor='y'))
            if tab == 'terrain_tab_1':
                terrain_fig.add_trace(vox_data[0])
                terrain_fig.add_trace(vox_data[1])
                terrain_fig.update_scenes(aspectmode='data')

            return terrain_fig, dem_button_status, dem_button_text

    @dash_app.callback([Output('dem_plot', 'figure'),
                        Output('cmap_holder', 'children'),
                        Output('tgrav_button', 'disabled'),
                        Output('tgrav_button_text', 'children')],
                       [Input('dem_button', 'n_clicks'),
                        Input('dem_tabs', 'active_tab')],
                       [State('dem_input', 'value')],
                       prevent_initial_call=True)
    def plot_dem(click, tab, dem_err):
        ctx = dash.callback_context
        tgrav_button_status = True
        tgrav_button_text = "No DTM in memory."
        if ctx.triggered[0]['prop_id'].split('.')[0] == 'dem_button':
            sc.generate_dem(err=dem_err)

        if click is None and ctx.triggered[0]['prop_id'].split('.')[0] == 'dem_tabs':
            return None, None, None, None
        else:
            tgrav_button_status = False
            tgrav_button_text = "Click to calculate gravitational acceleration for true terrain and DTM."
            raster_attrs = dict(x=sc.data['elevation']['dem'][0],
                                y=sc.data['elevation']['dem'][1],
                                z=sc.data['elevation']['dem'][2],
                                colorbar_title="metres",
                                colorscale='Viridis')
            surface_attrs = dict(x=sc.scene_properties['datum'][0],
                                 y=sc.scene_properties['datum'][1],
                                 z=sc.data['elevation']['dem'][3],
                                 colorbar_title="metres",
                                 colorscale='Viridis')

            if tab == 'dem_tab_2':
                fig_data = go.Heatmap(raster_attrs)
            elif tab == 'dem_tab_1':
                fig_data = go.Surface(surface_attrs)
                vox_data = [go.Mesh3d(x=sc.target_geometry['voxel']['vertices'][:, 0],
                                      y=sc.target_geometry['voxel']['vertices'][:, 1],
                                      z=sc.target_geometry['voxel']['vertices'][:, 2],
                                      i=sc.target_geometry['voxel']['indices'][:, 0],
                                      j=sc.target_geometry['voxel']['indices'][:, 1],
                                      k=sc.target_geometry['voxel']['indices'][:, 2],
                                      color='rgb(77,81,255)'),
                            go.Scatter3d(x=sc.target_geometry['wireframe'][0],
                                         y=sc.target_geometry['wireframe'][1],
                                         z=sc.target_geometry['wireframe'][2],
                                         mode='lines',
                                         line=dict(color='rgb(70,70,70)', width=1))]

            dem_fig = go.Figure(fig_data)
            dem_fig.update_layout(yaxis=dict(scaleanchor='x'),
                                  xaxis=dict(scaleanchor='y'))
            if tab == 'dem_tab_1':
                dem_fig.add_trace(vox_data[0])
                dem_fig.add_trace(vox_data[1])
                dem_fig.update_scenes(aspectmode='data')

            zmin = np.min(sc.data['elevation']['dem'][2])
            zmax = np.max(sc.data['elevation']['dem'][2])

            cmap_dump = json.dumps([zmin, zmax])

            return dem_fig, cmap_dump, tgrav_button_status, tgrav_button_text

    @dash_app.callback(Output('tgrav_plot', 'figure'),
                       [Input('tgrav_button', 'n_clicks'),
                        Input('tgrav_tabs', 'active_tab')],
                       State('t_density_input', 'value'),
                       prevent_initial_call=True)
    def plot_terrain_gravity(click, tab, density):
        ctx = dash.callback_context
        if ctx.triggered[0]['prop_id'].split('.')[0] == 'tgrav_button':
            sc.calculate_terrain_gravity(rho=density)

        if click is None and ctx.triggered[0]['prop_id'].split('.')[0] == 'tgrav_tabs':
            return None, None, None
        else:
            dem_attrs = dict(x=sc.data['perfect_gravity']['dem'][0],
                             y=sc.data['perfect_gravity']['dem'][1],
                             z=sc.data['perfect_gravity']['dem'][2],
                             colorbar_title="milligals")
            gt_attrs = dict(x=sc.data['perfect_gravity']['terrain'][0],
                            y=sc.data['perfect_gravity']['terrain'][1],
                            z=sc.data['perfect_gravity']['terrain'][2],
                            colorbar_title="milligals")
        if tab == 'tgrav_tab_2':
            fig_data = go.Heatmap(dem_attrs)
        elif tab == 'tgrav_tab_1':
            fig_data = go.Heatmap(gt_attrs)

        tgrav_fig = go.Figure(fig_data)
        tgrav_fig.update_layout(yaxis=dict(scaleanchor='x'),
                                xaxis=dict(scaleanchor='y'))

        return tgrav_fig

    @dash_app.callback([Output(f'{i}_collapse', 'is_open') for i in ['grid', 'spiral', 'points']],
                       [Input(f'{i}_display_button', 'n_clicks') for i in ['grid', 'spiral', 'points']],
                       [State(f'{i}_collapse', 'is_open') for i in ['grid', 'spiral', 'points']],
                       prevent_initial_call=True)
    def survey_collapse(n1, n2, n3, is_open1, is_open2, is_open3):
        ctx = dash.callback_context

        if not ctx.triggered:
            return False, False, False
        else:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "grid_display_button" and n1:
            return not is_open1, False, False
        elif button_id == "spiral_display_button" and n2:
            return False, not is_open2, False
        elif button_id == "points_display_button" and n3:
            return False, False, not is_open3
        return False, False, False

    @dash_app.callback(Output('survey_plot', 'figure'),
                       [Input('simulate_button', 'n_clicks'),
                        Input('survey_tabs', 'active_tab')],
                       [State('grav_err_input', 'value'),
                        State('gps_err_input', 'value')],
                       prevent_initial_call=True)
    def plot_survey(click, tab, grav_err, gps_err):
        ctx = dash.callback_context
        if ctx.triggered[0]['prop_id'].split('.')[0] == 'simulate_button':
            sc.calculate_target_gravity(sc.target_parameters['density'],
                                        with_terrain=True,
                                        with_noise=True,
                                        grav_err=grav_err, gps_err=gps_err)
            sc.calculate_target_gravity(sc.target_parameters['density'],
                                        with_terrain=False,
                                        with_noise=True,
                                        grav_err=grav_err, gps_err=gps_err)
            sc.calculate_target_gravity(sc.target_parameters['density'],
                                        with_terrain=True,
                                        with_noise=False,
                                        grav_err=grav_err, gps_err=gps_err)
        if click is None and ctx.triggered[0]['prop_id'].split('.')[0] == 'survey_tabs':
            return None, None, None
        else:
            full_attrs = dict(x=sc.data['noisy_gravity']['full'][0],
                              y=sc.data['noisy_gravity']['full'][1],
                              z=sc.data['noisy_gravity']['full'][2],
                              colorbar_title="milligals")
            nt_attrs = dict(x=sc.data['noisy_gravity']['target'][0],
                            y=sc.data['noisy_gravity']['target'][1],
                            z=sc.data['noisy_gravity']['target'][2],
                            colorbar_title="milligals")
        if tab == 'survey_tab_1':
            fig_data = go.Heatmap(full_attrs)
        elif tab == 'survey_tab_2':
            fig_data = go.Heatmap(nt_attrs)

        survey_fig = go.Figure(fig_data)
        survey_fig.update_layout(yaxis=dict(scaleanchor='x'),
                                 xaxis=dict(scaleanchor='y'))

        return survey_fig

    @dash_app.callback([Output('survey_pick_plot', 'figure'),
                        Output('interp_button', 'disabled'),
                        Output('interp_button_text', 'children')],
                       Input('survey_table', 'data'),
                       [State('count_data', 'children')])
    def pick_survey(data, count):
        ctx = dash.callback_context
        interp_button_status = True
        interp_button_text = 'Not enough survey points in memory (at least 3 required).'
        try:
            survey_pick_fig = go.Figure(data=go.Mesh3d(x=sc.target_geometry['voxel']['vertices'][:, 0],
                                                       y=sc.target_geometry['voxel']['vertices'][:, 1],
                                                       z=sc.target_geometry['voxel']['vertices'][:, 2],
                                                       i=sc.target_geometry['voxel']['indices'][:, 0],
                                                       j=sc.target_geometry['voxel']['indices'][:, 1],
                                                       k=sc.target_geometry['voxel']['indices'][:, 2]))
            survey_pick_fig.add_trace(go.Surface(x=(sc.scene_properties['datum'][0]),
                                                 y=sc.scene_properties['datum'][1],
                                                 z=sc.scene_properties['datum'][2],
                                                 showscale=False,
                                                 opacity=0.2))
            survey_pick_fig.update_scenes(aspectmode='data',
                                          dragmode=False)
            survey_pick_fig.update_layout(scene_camera=dict(eye=dict(x=0., y=0., z=2),
                                                            up=dict(x=0., y=2, z=0.)))
        except TypeError:
            print("No target or terrain data loaded.")
            return go.Figure(), interp_button_status, interp_button_text

        if ctx.triggered[0]['prop_id'].split('.')[0] == 'survey_table':
            count = int(count) - 1
            x_vals = [float(data[c]['column_1']) for c in range(count + 1)]
            y_vals = [float(data[c]['column_2']) for c in range(count + 1)]
            z_vals = [float(data[c]['column_3']) for c in range(count + 1)]

            survey_pick_fig.add_trace(go.Scatter3d(x=x_vals,
                                                   y=y_vals,
                                                   z=z_vals,
                                                   mode='markers',
                                                   marker_color='white',
                                                   marker_size=2))

            if count > 1:
                interp_button_status = False
                interp_button_text = "Click to interpolate between survey points."

        return survey_pick_fig, interp_button_status, interp_button_text

    @dash_app.callback(Output('interp_plot', 'figure'),
                       [Input('interp_button', 'n_clicks'),
                        Input('interp_tabs', 'active_tab')],
                       [State('grav_err_input', 'value'),
                        State('gps_err_input', 'value'),
                        State('survey_table', 'data'),
                        State('count_data', 'children'),
                        State('sip_radio', 'value')],
                       prevent_initial_call=True)
    def plot_interpolated_survey(click, tab, grav_err, gps_err, data, count, method):
        ctx = dash.callback_context
        if ctx.triggered[0]['prop_id'].split('.')[0] == 'interp_button':
            count = int(count) - 1
            x_vals = [float(data[c]['column_1']) for c in range(count + 1)]
            y_vals = [float(data[c]['column_2']) for c in range(count + 1)]
            z_vals = [float(data[c]['column_3']) for c in range(count + 1)]

            sc.update_survey(x_vals, y_vals, z_vals, grav_err, gps_err)
            sc.interpolate_survey_pts(method=method)

        if click is None and ctx.triggered[0]['prop_id'].split('.')[0] == 'interp_tabs':
            return None, None, None
        else:
            interp_attrs = dict(x=sc.data['interp_gravity']['raw'][0],
                                y=sc.data['interp_gravity']['raw'][1],
                                z=sc.data['interp_gravity']['raw'][2],
                                colorbar_title="milligals")
            perfect_attrs = dict(x=sc.data['interp_gravity']['target'][0],
                                 y=sc.data['interp_gravity']['target'][1],
                                 z=sc.data['interp_gravity']['target'][2],
                                 colorbar_title="milligals")
        if tab == 'interp_tab_2':
            fig_data = go.Heatmap(perfect_attrs)
        elif tab == 'interp_tab_1':
            fig_data = go.Heatmap(interp_attrs)

        interp_fig = go.Figure(fig_data)
        interp_fig.update_layout(yaxis=dict(scaleanchor='x'),
                                 xaxis=dict(scaleanchor='y'))

        return interp_fig

    @dash_app.callback(Output('click_data', 'children'),
                       [Input('survey_pick_plot', 'clickData')],
                       prevent_initial_call=True)
    def collect_click_data(click_data):
        x_pos = click_data['points'][0]['x']
        y_pos = click_data['points'][0]['y']
        z_pos = click_data['points'][0]['z']
        pos = [x_pos, y_pos, z_pos]
        return json.dumps(pos, indent=2)

    # @dash_app.callback([Output('grid_plot', 'figure'),],
    #                    [Input('grid_plot', 'selectedData')],
    #                    prevent_initial_call=True)
    # def grid_builder(click_data):


    # comment
    @dash_app.callback([Output('survey_table', 'data'),
                        Output('count_data', 'children')],
                       [Input('click_data', 'children'),
                        Input('new_survey_button', 'n_clicks')],
                       [State('survey_table', 'data'),
                        State('survey_table', 'columns')],
                       prevent_initial_call=True)
    def update_table(pos, click, table_data, table_cols):
        ctx = dash.callback_context
        if ctx.triggered[0]['prop_id'].split('.')[0] == 'click_data':
            data = json.loads(pos)
            table_data.append({c['id']: data[i] for c, i in zip(table_cols, range(0, 3))})
            count = len(table_data)
        elif ctx.triggered[0]['prop_id'].split('.')[0] == 'new_survey_button':
            table_data = list()
            count = 0
        return table_data, count

    # Target Geometry active/inactive fields callback
    @dash_app.callback([Output('radius_comp_input', 'disabled'),
                        Output('length_comp_input', 'disabled'),
                        Output('target_upload_path', 'disabled')],
                       Input('target_geometry_radio', 'value'),
                       prevent_initial_call=False)
    def geom_field_status(selection):
        status = [True, True, True, True]
        if selection == 'sphere':
            status[0] = False
        elif selection == 'cylinder':
            status[0] = False
            status[1] = False
        elif selection == 'custom':
            status[2] = False
        return status[0], status[1], status[2]

    # Terrain active/inactive fields callback
    @dash_app.callback([Output('seed_input', 'disabled'),
                        Output('corr_x_input', 'disabled'),
                        Output('corr_y_input', 'disabled'),
                        Output('max_input', 'disabled'),
                        Output('min_input', 'disabled'),
                        Output('terrain_upload_path', 'disabled')],
                       Input('terrain_dropdown', 'value'),
                       prevent_initial_call=False)
    def geom_field_status(selection):
        if selection == 6:
            seed_status = True
            corr_x_status = True
            corr_y_status = True
            max_status = True
            min_status = True
            path_status = True
        elif selection == 1:
            seed_status = False
            corr_x_status = False
            corr_y_status = True
            max_status = False
            min_status = False
            path_status = True
        else:
            seed_status = False
            corr_x_status = False
            corr_y_status = False
            max_status = False
            min_status = False
            path_status = True

        return seed_status, corr_x_status, corr_y_status, max_status, min_status, path_status

    @dash_app.callback([Output('vis_target_plot', 'figure'),
                        Output('vis_full_plot', 'figure'),
                        Output('vis_raw_plot', 'figure'),
                        Output('vis_slice_plot', 'figure')],
                       [Input('vis_button', 'n_clicks'),
                        Input('vis_click_data', 'children'),
                        Input('vis_slice_dropdown', 'value'),
                        Input('correction_radio', 'value'),
                        Input('vis_tabs', 'active_tab')],
                       prevent_initial_call=True)
    def vis(click, pos, value, correction, tab):
        ctx = dash.callback_context
        if correction == [0, 1] or correction == [1, 0]:
            sc.apply_corrections(free_air=True, terrain=True)
        elif correction == [0]:
            sc.apply_corrections(free_air=True, terrain=False)
        elif correction == [1]:
            sc.apply_corrections(free_air=False, terrain=True)
        else:
            sc.apply_corrections(free_air=False, terrain=False)

        selected_plot_list = [sc.data['interp_gravity']['target'],
                              sc.data['interp_gravity']['full'],
                              sc.data['interp_gravity']['raw'],
                              sc.data['perfect_gravity']['target'],
                              sc.data['perfect_gravity']['full'],
                              sc.data['noisy_gravity']['full'],
                              sc.data['perfect_gravity']['terrain'],
                              sc.data['perfect_gravity']['dem'],
                              sc.corrections['free_air'],
                              sc.corrections['terrain'],
                              sc.data['elevation']['terrain'],
                              sc.data['elevation']['dem'],
                              sc.data['corrected_gravity']['full'],
                              sc.data['corrected_gravity']['interp']]

        if value == 10 or value == 11:
            unit = 'metres'
        else:
            unit = 'milligals'

        if click is None and ctx.triggered[0]['prop_id'].split('.')[0] == 'vis_tabs':
            return None, None, None, None
        else:
            if tab == 'vis_tab_1':
                data = [selected_plot_list[0][3],
                        selected_plot_list[1][3],
                        selected_plot_list[13][3]]
            elif tab == 'vis_tab_2':
                data = [selected_plot_list[3][3],
                        selected_plot_list[4][3],
                        selected_plot_list[12][3]]

        c1_fig = px.imshow(img=np.flipud(data[0]),
                           x=sc.scene_properties['datum'][0][0],
                           y=sc.scene_properties['datum'][0][0])

        c1_fig.update_layout(coloraxis_colorbar=dict(title='milligal'))

        c2_fig = px.imshow(img=np.flipud(data[1]),
                           x=sc.scene_properties['datum'][0][0],
                           y=sc.scene_properties['datum'][0][0])

        c2_fig.update_layout(coloraxis_colorbar=dict(title='milligal'))

        c3_fig = px.imshow(img=np.flipud(data[2]),
                           x=sc.scene_properties['datum'][0][0],
                           y=sc.scene_properties['datum'][0][0])

        c3_fig.update_layout(coloraxis_colorbar=dict(title='milligal'))

        slice_fig = px.imshow(img=np.flipud(selected_plot_list[value][3]),
                              x=sc.scene_properties['datum'][0][0],
                              y=sc.scene_properties['datum'][0][0])
        slice_fig.update_xaxes(spikemode='across', showspikes=True)
        slice_fig.update_yaxes(spikemode='across', showspikes=True)

        if ctx.triggered[0]['prop_id'].split('.')[0] == 'vis_click_data':
            click_data = json.loads(pos)
            x_pos = click_data[0]
            y_pos = click_data[1]

            x_trace = go.Scatter(x=sc.scene_properties['datum'][0][0],
                                 y=np.ones_like(sc.scene_properties['datum'][0][0]) * y_pos,
                                 marker_color='cyan',
                                 name="E-W")
            y_trace = go.Scatter(x=np.ones_like(sc.scene_properties['datum'][0][0]) * x_pos,
                                 y=sc.scene_properties['datum'][0][0],
                                 marker_color='lightgreen',
                                 name="N-S")

            slice_fig.add_trace(x_trace)
            slice_fig.add_trace(y_trace)
            slice_fig.update_layout(legend_title=unit)

        return c1_fig, c2_fig, c3_fig, slice_fig

    @dash_app.callback([Output('vis_table', 'children'),
                        Output('vis_3d_plot', 'figure')],
                       [Input('vis_target_plot', 'figure'),
                        Input('sum_tabs', 'active_tab')])
    def vis_summary(click, tab):
        sim_df = pd.DataFrame(list(zip(sc.sim_params.keys(), sc.sim_params.values())),
                              columns=['Parameter', 'Value'])

        param_table = dbc.Table.from_dataframe(sim_df)

        terrain_data = go.Surface(x=sc.scene_properties['datum'][0],
                                  y=sc.scene_properties['datum'][1],
                                  z=sc.data['elevation']['terrain'][3],
                                  colorbar_title="metres",
                                  colorscale='Viridis')

        if tab == 'sum_tab_1':
            fig = go.Figure(terrain_data)
            fig.add_trace(go.Mesh3d(x=sc.target_geometry['mesh']['vertices'][:, 0],
                                    y=sc.target_geometry['mesh']['vertices'][:, 1],
                                    z=sc.target_geometry['mesh']['vertices'][:, 2],
                                    i=sc.target_geometry['mesh']['indices'][:, 0],
                                    j=sc.target_geometry['mesh']['indices'][:, 1],
                                    k=sc.target_geometry['mesh']['indices'][:, 2],
                                    color='rgb(77,81,255)'))
        elif tab == 'sum_tab_2':
            fig = go.Figure(terrain_data)
            fig.add_trace(go.Mesh3d(x=sc.target_geometry['voxel']['vertices'][:, 0],
                                    y=sc.target_geometry['voxel']['vertices'][:, 1],
                                    z=sc.target_geometry['voxel']['vertices'][:, 2],
                                    i=sc.target_geometry['voxel']['indices'][:, 0],
                                    j=sc.target_geometry['voxel']['indices'][:, 1],
                                    k=sc.target_geometry['voxel']['indices'][:, 2],
                                    color='rgb(77,81,255)'))
            fig.add_trace(go.Scatter3d(x=sc.target_geometry['wireframe'][0],
                                       y=sc.target_geometry['wireframe'][1],
                                       z=sc.target_geometry['wireframe'][2],
                                       mode='lines',
                                       line=dict(color='rgb(70,70,70)', width=1)))
        return param_table, fig

    @dash_app.callback(Output('vis_xy_plot', 'figure'),
                       [Input('vis_click_data', 'children'),
                        Input('vis_target_toggle', 'value')],
                       State('vis_slice_dropdown', 'value'),
                       prevent_initial_call=True)
    def vis_slice(pos, toggle, value):
        selected_plot_list = [sc.data['interp_gravity']['target'],
                              sc.data['interp_gravity']['full'],
                              sc.data['interp_gravity']['raw'],
                              sc.data['perfect_gravity']['target'],
                              sc.data['perfect_gravity']['full'],
                              sc.data['noisy_gravity']['full'],
                              sc.data['perfect_gravity']['terrain'],
                              sc.data['perfect_gravity']['dem'],
                              sc.corrections['free_air'],
                              sc.corrections['terrain'],
                              sc.data['elevation']['terrain'],
                              sc.data['elevation']['dem'],
                              sc.data['corrected_gravity']['full'],
                              sc.data['corrected_gravity']['interp']]

        if value == 10 or value == 11:
            unit = 'metres'
        else:
            unit = 'milligals'

        click_data = json.loads(pos)
        x_pos = click_data[0]
        y_pos = click_data[1]

        idx = np.where(sc.scene_properties['datum'][0] == x_pos)[1][0]
        idy = np.where(sc.scene_properties['datum'][1] == y_pos)[0][0]

        y_min = np.min(np.flipud(selected_plot_list[value][3]))
        y_max = np.max(np.flipud(selected_plot_list[value][3]))

        fig = make_subplots(rows=2, cols=1,
                            shared_xaxes=True,
                            x_title='Position, metres',
                            y_title='Signal Strength, ' + unit)

        fig.append_trace(go.Scatter(y=np.flipud(selected_plot_list[value][3])[idy, :],
                                    x=sc.scene_properties['datum'][0][idx, :],
                                    name='E-W', marker_color='cyan'),
                         row=1, col=1)
        fig.append_trace(go.Scatter(y=np.flipud(selected_plot_list[value][3])[:, idx],
                                    x=sc.scene_properties['datum'][1][:, idx],
                                    name='N-S', marker_color='lightgreen'),
                         row=2, col=1)

        if toggle == [0] and (value not in range(8, 11)):
            fig.append_trace(go.Scatter(y=np.flipud(selected_plot_list[3][3])[idy, :],
                                        x=sc.scene_properties['datum'][0][idx, :],
                                        name='Target', marker_color='red'),
                             row=1, col=1)
            fig.append_trace(go.Scatter(y=np.flipud(selected_plot_list[3][3])[:, idx],
                                        x=sc.scene_properties['datum'][1][:, idx],
                                        name='Target', marker_color='red', showlegend=False),
                             row=2, col=1)

        fig.update_yaxes(range=[y_min, y_max])

        return fig

    @dash_app.callback(Output('vis_click_data', 'children'),
                       Input('vis_slice_plot', 'clickData'),
                       prevent_initial_call=True)
    def vis_get_click(click_data):
        x_pos = click_data['points'][0]['x']
        y_pos = click_data['points'][0]['y']
        pos = [x_pos, y_pos]
        return json.dumps(pos)

    @dash_app.callback(Output("vis_collapse", "is_open"),
                       [Input("vis_3d_button", "n_clicks")],
                       [State("vis_collapse", "is_open")],
                       prevent_initial_call=True)
    def toggle_vis_collapse(n, is_open):
        if n:
            return not is_open
        return is_open

    @dash_app.callback(Output('vis_download_modal', 'is_open'),
                       [Input('vis_dl_button', 'n_clicks'),
                        Input('vis_close_button', 'n_clicks')],
                       [State('vis_download_modal', 'is_open')],
                       prevent_initial_call=True)
    def toggle_download_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    @dash_app.callback(Output('vis_dl_button', 'children'),
                       Input('vis_save_button', 'n_clicks'),
                       [State('vis_dl_checkbox', 'value'),
                        State('vis_path_input', 'value')],
                       prevent_initial_call=True)
    def download_data(click, value, path):
        data_list = [sc.data['interp_gravity']['target'],
                     sc.data['interp_gravity']['full'],
                     sc.data['interp_gravity']['raw'],
                     sc.data['perfect_gravity']['target'],
                     sc.data['perfect_gravity']['full'],
                     sc.data['noisy_gravity']['full'],
                     sc.data['perfect_gravity']['terrain'],
                     sc.data['perfect_gravity']['dem'],
                     sc.corrections['free_air'],
                     sc.corrections['terrain'],
                     sc.data['elevation']['terrain'],
                     sc.data['elevation']['dem'],
                     sc.data['corrected_gravity']['full'],
                     sc.data['corrected_gravity']['interp']]
        label_list = ['Interp_Only_Target_Signal',
                      'Interp_Target_Terrain_no_noise',
                      'Interp_Target_Terrain_with_noise',
                      'Full_Only_Target_Signal',
                      'Full_Target_Terrain_no_noise',
                      'Full_Target_Terrain_with_noise',
                      'True_Terrain_Gravity_Component',
                      'DTM_Gravity_Component',
                      'Free_Air_Correction',
                      'Terrain_Correction',
                      'True_Terrain_Elevation',
                      'DTM_Elevation',
                      'Full_Target_Terrain_corrected'
                      'Interp_Target_Terrain_corrected']

        for i in value:
            file_data = data_list[i][3]
            label = label_list[i]
            np.savetxt('{}{}.txt'.format(path, label), file_data)
        return 'test'

    # # Survey Update Callback
    # @dash_app.callback([Output('survey_background_plot', 'figure'),
    #                     Output('survey_perfect_plot', 'figure'),
    #                     Output('survey_target_plot', 'figure'),
    #                     Output('survey_full_plot', 'figure')],
    #                    [Input('page-2-link', 'n_clicks'),
    #                     Input('survey_table', 'data'),
    #                     Input('sip_radio', 'value'),
    #                     Input('noise_button', 'n_clicks')],
    #                    [State('survey_background_plot', 'figure'),
    #                     State('count_div', 'children'),
    #                     State('grav_error', 'value'),
    #                     State('gps_error', 'value')])
    # def update_survey(click, data, interp_method, apply_noise, fig, count, grav_err, gps_err):
    #     sv1.update_inheritance(sc)
    #     ctx = dash.callback_context
    #     count = int(count) - 1
    #     print(count)
    #     zmin = np.min(sv1.target['measured_gravity'][2])
    #     zmax = np.max(sv1.target['measured_gravity'][2])
    #     survey_background_fig = go.Figure(data=go.Mesh3d(x=sc.target_geometry['voxel']['vertices'][:, 0],
    #                                                      y=sc.target_geometry['voxel']['vertices'][:, 1],
    #                                                      z=sc.target_geometry['voxel']['vertices'][:, 2],
    #                                                      i=sc.target_geometry['voxel']['indices'][:, 0],
    #                                                      j=sc.target_geometry['voxel']['indices'][:, 1],
    #                                                      k=sc.target_geometry['voxel']['indices'][:, 2]))
    #     survey_background_fig.add_trace(go.Surface(x=(sc.scene_properties['datum'][0]),
    #                                                y=sc.scene_properties['datum'][1],
    #                                                z=sc.scene_properties['datum'][2],
    #                                                showscale=False,
    #                                                opacity=0.2))
    #
    #     survey_background_fig.update_scenes(aspectmode='data')
    #     survey_background_fig.update_layout(height=600, width=600,
    #                                         title_text='DEM with Target Outline (Pick Survey Points)',
    #                                         scene_camera=dict(eye=dict(x=0., y=0., z=2.5),
    #                                                           up=dict(x=0., y=2, z=0.)))
    #
    #     survey_target_fig = go.Figure(go.Heatmap(x=(sv1.measurements['interpolated']['measured'][0]),
    #                                              y=(sv1.measurements['interpolated']['measured'][1]),
    #                                              z=(sv1.measurements['interpolated']['measured'][2]),
    #                                              zmin=zmin, zmax=zmax))
    #
    #     if ctx.triggered[0]['prop_id'].split('.')[0] == 'survey_table':
    #         x_vals = [float(data[c]['column_1']) for c in range(count + 1)]
    #         y_vals = [float(data[c]['column_2']) for c in range(count + 1)]
    #         z_vals = [float(data[c]['column_3']) for c in range(count + 1)]
    #
    #         sv1.update_survey(x_vals, y_vals, z_vals, grav_err, gps_err)
    #
    #         survey_background_fig.add_trace(go.Scatter3d(x=x_vals,
    #                                                      y=y_vals,
    #                                                      z=z_vals,
    #                                                      mode='markers',
    #                                                      marker_color='white',
    #                                                      marker_size=2))
    #         survey_background_fig.update_scenes(aspectmode='data')
    #         survey_background_fig.update_layout(scene_camera=dict(eye=dict(x=0., y=0., z=2.5)))
    #
    #         if count > 1:
    #             sv1.interpolate_survey_pts(method=interp_method)
    #             survey_target_fig = go.Figure(go.Heatmap(x=(sv1.measurements['interpolated']['measured'][0]),
    #                                                      y=(sv1.measurements['interpolated']['measured'][1]),
    #                                                      z=(sv1.measurements['interpolated']['measured'][2]),
    #                                                      zmin=zmin, zmax=zmax))
    #
    #     survey_perfect_fig = go.Figure(go.Heatmap(x=sv1.target['gravity'][0],
    #                                               y=sv1.target['gravity'][1],
    #                                               z=sv1.target['gravity'][2],
    #                                               zmin=zmin, zmax=zmax))
    #     survey_full_fig = go.Figure(go.Heatmap(x=sv1.target['measured_gravity'][0],
    #                                            y=sv1.target['measured_gravity'][1],
    #                                            z=sv1.target['measured_gravity'][2],
    #                                            zmin=zmin, zmax=zmax))
    #
    #     survey_target_fig.update_layout(title_text='Interpolated Gravity Signal from Measurement Points',
    #                                     coloraxis={'colorscale': 'inferno'})
    #     survey_perfect_fig.update_layout(title_text='Gravitational Accl. from Target Model',
    #                                      coloraxis={'colorscale': 'inferno'})
    #     survey_full_fig.update_layout(title_text='Gravitational Accl. from Perfect Survey',
    #                                   coloraxis={'colorscale': 'inferno'})
    #
    #     return survey_background_fig, survey_perfect_fig, survey_target_fig, survey_full_fig
    #
    # @dash_app.callback(Output('click_data', 'children'),
    #                    [Input('survey_background_plot', 'clickData')],
    #                    prevent_initial_call=True)
    # def collect_click_data(click_data):
    #     x_pos = click_data['points'][0]['x']
    #     y_pos = click_data['points'][0]['y']
    #     z_pos = click_data['points'][0]['z']
    #     pos = [x_pos, y_pos, z_pos]
    #     print(pos)
    #     return json.dumps(pos, indent=2)
    #
    # # comment
    # @dash_app.callback([Output('survey_table', 'data'),
    #                     Output('count_div', 'children')],
    #                    [Input('click_data', 'children')],
    #                    [State('survey_table', 'data'),
    #                     State('survey_table', 'columns')],
    #                    prevent_initial_call=True)
    # def update_table(pos, table_data, table_cols):
    #     data = json.loads(pos)
    #     table_data.append({c['id']: data[i] for c, i in zip(table_cols, range(0, 3))})
    #     count = len(table_data)
    #     return table_data, count

    # @dash_app.callback([Output('vis_subplot', 'figure'),
    #                     Output('vis_mesh_plot', 'figure'),
    #                     Output('vis_vox_plot', 'figure'),
    #                     Output('x_slider', 'min'),
    #                     Output('x_slider', 'max'),
    #                     Output('y_slider', 'min'),
    #                     Output('y_slider', 'max'),
    #                     Output('x_slider', 'step'),
    #                     Output('y_slider', 'step')],
    #                    [Input('page-4-link', 'n_clicks'),
    #                     Input('correction_checklist', 'value'),
    #                     Input('x_slider', 'value'),
    #                     Input('y_slider', 'value'),
    #                     Input('slice_dropdown', 'value')])
    # def display_vis(click, corrections, xval, yval, dropdown_val):
    #     ctx = dash.callback_context
    #     if ctx.triggered[0]['prop_id'].split('.')[0] == 'page-4-link':
    #         pass
    #     xmin = np.min(sv1.survey_properties['datum'][0])
    #     xmax = np.max(sv1.survey_properties['datum'][0])
    #     ymin = np.min(sv1.survey_properties['datum'][1])
    #     ymax = np.max(sv1.survey_properties['datum'][1])
    #     step = sv1.survey_properties['resolution']
    #
    #     if corrections == ['fac']:
    #         full_corrected = sv1.measurements['full_raw'] + sv1.corrections['free_air'][2]
    #         survey_corrected = np.add(sv1.measurements['interpolated']['measured'][2],
    #                                   sv1.corrections['free_air'][2],
    #                                   where=(sv1.measurements['interpolated']['measured'][2] != None))
    #     elif corrections == ['tc']:
    #         full_corrected = sv1.measurements['full_raw'] + sv1.corrections['terrain'][2]
    #         survey_corrected = np.add(sv1.measurements['interpolated']['measured'][2],
    #                                   sv1.corrections['terrain'][2],
    #                                   where=(sv1.measurements['interpolated']['measured'][2] != None))
    #     elif corrections and len(corrections) == 2:
    #         corr_vals = sv1.corrections['free_air'][2] + sv1.corrections['terrain'][2]
    #         full_corrected = sv1.measurements['full_raw'] + corr_vals
    #         survey_corrected = np.add(sv1.measurements['interpolated']['measured'][2],
    #                                   corr_vals,
    #                                   where=(sv1.measurements['interpolated']['measured'][2] != None))
    #     else:
    #         full_corrected = sv1.measurements['full_raw']
    #         survey_corrected = sv1.measurements['interpolated']['measured'][2]
    #     dim = int(np.sqrt(len(sv1.measurements['interpolated']['true'][0])))
    #     possible_data = [sv1.measurements['interpolated']['true'][3],
    #                      sv1.measurements['interpolated']['measured'][3],
    #                      survey_corrected.reshape(dim, dim),
    #                      sv1.target['gravity'][3],
    #                      sv1.measurements['full_raw'].reshape(dim, dim),
    #                      full_corrected.reshape(dim, dim)]
    #     slice_data = possible_data[dropdown_val - 1]
    #
    #     r1_zmin = np.min(survey_corrected)
    #     r1_zmax = np.max(survey_corrected)
    #     r2_zmin = np.min(full_corrected)
    #     r2_zmax = np.max(full_corrected)
    #
    #     fig = make_subplots(rows=4, cols=4,
    #                         specs=[[{"rowspan": 3}, {}, {}, {}],
    #                                [None, {}, {}, {}],
    #                                [None, {}, {}, {}],
    #                                [None, {"colspan": 3}, None, None]],
    #                         subplot_titles=(
    #                             "Y-slice", "Survey: True Target", "Survey: Target + Terrain", "Survey: Measured",
    #                             "Full: True Target", "Full: Target + Terrain", "Full: Measured",
    #                             "Free Air Correction", "", "Terrain Correction", "X-slice"))
    #
    #     fig.add_trace(go.Heatmap(x=(sv1.measurements['interpolated']['true'][0]),
    #                              y=(sv1.measurements['interpolated']['true'][1]),
    #                              z=(sv1.measurements['interpolated']['true'][2]),
    #                              colorbar=dict(len=0.2, x=1, y=0.92),
    #                              zmin=r1_zmin, zmax=r1_zmax, zsmooth=False),
    #                   row=1, col=2)
    #     fig.add_trace(go.Heatmap(x=(sv1.measurements['interpolated']['measured'][0]),
    #                              y=(sv1.measurements['interpolated']['measured'][1]),
    #                              z=sv1.measurements['interpolated']['measured'][2],
    #                              showscale=False,
    #                              zmin=r1_zmin, zmax=r1_zmax, zsmooth=False),
    #                   row=1, col=3)
    #     fig.add_trace(go.Heatmap(x=(sv1.measurements['interpolated']['measured'][0]),
    #                              y=(sv1.measurements['interpolated']['measured'][1]),
    #                              z=survey_corrected,
    #                              showscale=False,
    #                              zmin=r1_zmin, zmax=r1_zmax, zsmooth=False),
    #                   row=1, col=4)
    #     fig.add_trace(go.Heatmap(x=sv1.target['gravity'][0],
    #                              y=sv1.target['gravity'][1],
    #                              z=sv1.target['gravity'][2],
    #                              colorbar=dict(len=0.2, x=1, y=0.63),
    #                              zmin=r2_zmin, zmax=r2_zmax, zsmooth=False),
    #                   row=2, col=2)
    #     fig.add_trace(go.Heatmap(x=sv1.target['measured_gravity'][0],
    #                              y=sv1.target['measured_gravity'][1],
    #                              z=sv1.measurements['full_raw'],
    #                              showscale=False,
    #                              zmin=r2_zmin, zmax=r2_zmax, zsmooth=False),
    #                   row=2, col=3)
    #     fig.add_trace(go.Heatmap(x=sv1.target['measured_gravity'][0],
    #                              y=sv1.target['measured_gravity'][1],
    #                              z=full_corrected,
    #                              showscale=False,
    #                              zmin=r2_zmin, zmax=r2_zmax, zsmooth=False),
    #                   row=2, col=4)
    #     fig.add_trace(go.Heatmap(x=sv1.corrections['free_air'][0],
    #                              y=sv1.corrections['free_air'][1],
    #                              z=sv1.corrections['free_air'][2],
    #                              colorbar=dict(len=0.2, x=0.47, y=0.35),
    #                              zsmooth=False),
    #                   row=3, col=2)
    #     fig.add_trace(go.Heatmap(x=sv1.corrections['terrain'][0],
    #                              y=sv1.corrections['terrain'][1],
    #                              z=sv1.corrections['terrain'][2],
    #                              colorbar=dict(len=0.2, x=1, y=0.35),
    #                              zsmooth=False),
    #                   row=3, col=4)
    #     fig.add_trace(go.Scatter(x=sv1.target['gravity'][3][:, int(yval / step)],
    #                              y=sv1.survey_properties['datum'][1][:, int(yval / step)],
    #                              name="y Target Signal"),
    #                   row=1, col=1)
    #     fig.add_trace(go.Scatter(x=slice_data[:, int(yval / step)],
    #                              y=sv1.survey_properties['datum'][1][:, int(yval / step)],
    #                              name='y Dropdown Dataset'),
    #                   row=1, col=1)
    #     fig.add_trace(go.Scatter(y=sv1.target['gravity'][3][int(xval / step), :],
    #                              x=sv1.survey_properties['datum'][0][int(xval / step), :],
    #                              name="x Target Signal"),
    #                   row=4, col=2)
    #     fig.add_trace(go.Scatter(y=slice_data[int(xval / step), :],
    #                              x=sv1.survey_properties['datum'][0][int(xval / step), :],
    #                              name='x Dropdown Dataset'),
    #                   row=4, col=2)
    #
    #     fig.update_layout(height=900, width=900,
    #                       legend=dict(yanchor='top',
    #                                   xanchor='left',
    #                                   y=0.2,
    #                                   x=0.))
    #     fig.update_coloraxes(colorbar_title=dict(text='mgal'))
    #
    #     mesh_fig = go.Figure(data=go.Mesh3d(x=sc.target_geometry['mesh']['vertices'][:, 0],
    #                                         y=sc.target_geometry['mesh']['vertices'][:, 1],
    #                                         z=sc.target_geometry['mesh']['vertices'][:, 2],
    #                                         i=sc.target_geometry['mesh']['indices'][:, 0],
    #                                         j=sc.target_geometry['mesh']['indices'][:, 1],
    #                                         k=sc.target_geometry['mesh']['indices'][:, 2]))
    #     mesh_fig.add_trace(go.Surface(z=sc.terrain['true']['elevation'][3],
    #                                   x=sc.scene_properties['datum'][0],
    #                                   y=sc.scene_properties['datum'][1],
    #                                   showscale=False,
    #                                   opacity=0.8,
    #                                   colorscale='Viridis'))
    #
    #     vox_fig = go.Figure(data=go.Mesh3d(x=sc.target_geometry['voxel']['vertices'][:, 0],
    #                                        y=sc.target_geometry['voxel']['vertices'][:, 1],
    #                                        z=sc.target_geometry['voxel']['vertices'][:, 2],
    #                                        i=sc.target_geometry['voxel']['indices'][:, 0],
    #                                        j=sc.target_geometry['voxel']['indices'][:, 1],
    #                                        k=sc.target_geometry['voxel']['indices'][:, 2]))
    #
    #     vox_fig.add_trace(go.Scatter3d(x=sc.target_geometry['wireframe'][0],
    #                                    y=sc.target_geometry['wireframe'][1],
    #                                    z=sc.target_geometry['wireframe'][2],
    #                                    mode='lines',
    #                                    line=dict(color='rgb(70,70,70)', width=1)))
    #
    #     vox_fig.add_trace(go.Surface(z=sc.terrain['true']['elevation'][3],
    #                                  x=sc.scene_properties['datum'][0],
    #                                  y=sc.scene_properties['datum'][1],
    #                                  showscale=False,
    #                                  opacity=0.8,
    #                                  colorscale='Viridis'))
    #
    #     mesh_fig.update_scenes(aspectmode='data')
    #     vox_fig.update_scenes(aspectmode='data')
    #
    #     return fig, mesh_fig, vox_fig, xmin, xmax, ymin, ymax, step, step

    # # Terrain Update Callback
    # @dash_app.callback([Output('terrain_3d_plot', 'figure'),
    #                     Output('terrain_2d_plot', 'figure'),
    #                     Output('terrain_grav_plot', 'figure')],
    #                    [Input('terrain_button', 'n_clicks'),
    #                     Input('page-2-link', 'n_clicks')],
    #                    [State('tgf_radio', 'value'),
    #                     State('seed_input', 'value'),
    #                     State('x_corr_input', 'value'),
    #                     State('y_corr_input', 'value'),
    #                     State('t_max_elev', 'value'),
    #                     State('t_min_elev', 'value'),
    #                     State('dem_error', 'value')],
    #                    prevent_initial_call=False)
    # def update_terrain(calculate,
    #                    click,
    #                    generation_function,
    #                    seed,
    #                    x_corr, y_corr,
    #                    max_z, min_z,
    #                    dem_error):
    #     ctx = dash.callback_context
    #     if ctx.triggered[0]['prop_id'].split('.')[0] == 'terrain_button':
    #         sc.generate_terrain(generation_function, x_corr, y_corr, max_z, min_z, seed, dem_error)
    #         sc.calculate_terrain_gravity(2700)
    #         sc.calculate_target_gravity(sc.target_parameters['density'][0])
    #
    #     terrain_3d_fig = make_subplots(rows=1, cols=2, specs=[[{"type": "surface"}, {"type": "surface"}]],
    #                                    subplot_titles=("True", "DEM"))
    #     terrain_3d_fig.add_trace(go.Surface(z=sc.terrain['true']['elevation'][3],
    #                                         x=sc.scene_properties['datum'][0],
    #                                         y=sc.scene_properties['datum'][1],
    #                                         coloraxis="coloraxis"),
    #                              row=1, col=1)
    #     terrain_3d_fig.add_trace(go.Surface(z=sc.terrain['dem']['elevation'][3],
    #                                         x=sc.scene_properties['datum'][0],
    #                                         y=sc.scene_properties['datum'][1],
    #                                         coloraxis='coloraxis'),
    #                              row=1, col=2)
    #     terrain_3d_fig.update_layout(coloraxis={'colorscale': 'Viridis'},
    #                                  height=400, width=800,
    #                                  title_text='3D Terrain Elevation Surface')
    #     terrain_3d_fig.update_scenes(zaxis=dict(nticks=4, range=[np.min(sc.terrain['dem']['elevation'][2]),
    #                                                              np.max(sc.terrain['dem']['elevation'][2])]),
    #                                  aspectratio=dict(x=1, y=1, z=0.5))
    #     terrain_3d_fig.update_coloraxes(colorbar_title=dict(text='metres'))
    #     terrain_2d_fig = make_subplots(rows=1, cols=2, specs=[[{"type": "heatmap"}, {"type": "heatmap"}]],
    #                                    subplot_titles=("True", "DEM"))
    #     terrain_2d_fig.add_trace(go.Heatmap(x=sc.terrain['true']['elevation'][0],
    #                                         y=sc.terrain['true']['elevation'][1],
    #                                         z=sc.terrain['true']['elevation'][2],
    #                                         coloraxis='coloraxis'),
    #                              row=1, col=1)
    #     terrain_2d_fig.add_trace(go.Heatmap(x=sc.terrain['dem']['elevation'][0],
    #                                         y=sc.terrain['dem']['elevation'][1],
    #                                         z=sc.terrain['dem']['elevation'][2],
    #                                         coloraxis='coloraxis'),
    #                              row=1, col=2)
    #     terrain_2d_fig.update_layout(coloraxis={'colorscale': 'Viridis'},
    #                                  height=400, width=800,
    #                                  title_text='Terrain Elevation Raster')
    #     terrain_2d_fig.update_coloraxes(colorbar_title=dict(text='metres'))
    #     terrain_grav_fig = make_subplots(rows=1, cols=2, specs=[[{"type": "heatmap"}, {"type": "heatmap"}]],
    #                                      subplot_titles=("True", "DEM"))
    #     terrain_grav_fig.add_trace(go.Heatmap(x=sc.terrain['true']['gravity'][0],
    #                                           y=sc.terrain['true']['gravity'][1],
    #                                           z=sc.terrain['true']['gravity'][2],
    #                                           coloraxis='coloraxis'),
    #                                row=1, col=1)
    #     terrain_grav_fig.add_trace(go.Heatmap(x=sc.terrain['dem']['gravity'][0],
    #                                           y=sc.terrain['dem']['gravity'][1],
    #                                           z=sc.terrain['dem']['gravity'][2],
    #                                           coloraxis='coloraxis'),
    #                                row=1, col=2)
    #     terrain_grav_fig.update_layout(coloraxis={'colorscale': 'inferno'},
    #                                    height=400, width=800,
    #                                    title_text='Terrain Gravitational Acceleration Field')
    #     terrain_grav_fig.update_coloraxes(colorbar_title=dict(text='milligal'))
    #
    #     return terrain_3d_fig, terrain_2d_fig, terrain_grav_fig

    # Callback for switching pages within the dashboard.
    @dash_app.callback(Output("page-content", "children"), [Input("url", "pathname")])
    def render_page_content(pathname):
        if pathname in ["/dashapp/", "/dashapp/page-1"]:
            return target_layout
        elif pathname == "/dashapp/page-2":
            return terrain_layout
        elif pathname == "/dashapp/page-3":
            return survey_layout
        elif pathname == "/dashapp/page-4":
            return vis_layout
        # If the user tries to reach a different page, return a 404 message
        return dbc.Jumbotron(
            [
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
                html.P(f"The pathname {pathname} was not recognised..."),
            ]
        )

    return dash_app.server
