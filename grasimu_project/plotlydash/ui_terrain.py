import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
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
