import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

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

extent_plot_card = dbc.Card(
    [
        dbc.CardHeader("Model Extent Plot"),
        dbc.CardBody(
            [
                dcc.Graph(id='extent_pick_plot'),
            ]
        )
    ]
)


extent_opts_card = dbc.Card([
    dbc.CardHeader([
        "Set Model Extent"
    ]),
    dbc.CardBody([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    dbc.Button('Automatic Extent',
                               id='auto_extent_button',
                               color='link'),
                ),
                dbc.Collapse(
                    dbc.CardBody([
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
                                disabled=True
                            ),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.FormGroup([
                                    dbc.Label("Extent from DEM"),
                                    dbc.InputGroup([
                                        dbc.InputGroupAddon(
                                            dbc.Checkbox(
                                                id="extent_dem_checkbox"
                                            ),
                                            addon_type="prepend"
                                        ),
                                        dbc.Input(id='extent_dem_path',
                                                  placeholder="e.g., /home/user/mesh_files/mesh.stl",
                                                  type="text",
                                                  disabled=False,
                                                  persistence=True),
                                    ]),
                                    dbc.FormText("Filename must include .csv"),
                                ]),

                            ]),
                            dbc.Col([
                                dbc.Label("DEM resolution"),
                                dbc.InputGroup([
                                    dbc.Input(id='extent_dem_resolution',
                                              type='number'),
                                    dbc.InputGroupAddon('m', addon_type='append')
                                ])
                            ], width=4),
                        ]),

                    ]),
                    id='auto_extent_collapse',
                    is_open=True
                )
            ]),
            dbc.Card([
                dbc.CardHeader(
                    dbc.Button('Manually Set Extent',
                               id='manual_extent_button',
                               color='link'),
                ),
                dbc.Collapse(
                    dbc.CardBody([
                        dbc.Label('Manual Simulation Extent'),
                        dbc.Col([
                            dbc.Row([
                                dbc.Col(
                                    dbc.FormGroup(
                                        dbc.InputGroup([
                                            dbc.InputGroupAddon("x1", addon_type="prepend"),
                                            dbc.Input(id='extent_x1_input', type='number', persistence=True,
                                                      disabled=False),
                                        ]),

                                    ),

                                ),
                                dbc.Col(
                                    dbc.FormGroup(
                                        dbc.InputGroup([
                                            dbc.InputGroupAddon("y1", addon_type="prepend"),
                                            dbc.Input(id='extent_y1_input', type='number', persistence=True,
                                                      disabled=False),
                                        ]),

                                    ),

                                ),

                            ], form=True),

                            dbc.Row([
                                dbc.Col(
                                    dbc.FormGroup(
                                        dbc.InputGroup([
                                            dbc.InputGroupAddon("x2", addon_type="prepend"),
                                            dbc.Input(id='extent_x2_input', type='number', persistence=True,
                                                      disabled=False),
                                        ]),

                                    ),

                                ),
                                dbc.Col(
                                    dbc.FormGroup(
                                        dbc.InputGroup([
                                            dbc.InputGroupAddon("y2", addon_type="prepend"),
                                            dbc.Input(id='extent_y2_input', type='number', persistence=True,
                                                      disabled=False),
                                        ]),
                                    ),

                                ),
                            ], form=True),

                        ]),
                    ]),
                    id='manual_extent_collapse',
                    is_open=False
                )
            ]),

        ]),
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
            dbc.Button('Set Model Extent',
                       id='extent_button',
                       color='primary',
                       size='lg',
                       outline=True,
                       block=True,
                       disabled=False),
            dbc.FormText("Sets the extent of the model, and how often the model space is sampled.",
                         id='extent_button_text')
        ]),

    ]),
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
            dbc.Label('Target Density Contrast'),
            dbc.InputGroup([
                dbc.Input(id='density_input', type='number', persistence=True,
                          disabled=False),
                dbc.InputGroupAddon("kg/m^3", addon_type="append")
            ]),

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

extent_cards = dbc.CardGroup([
    extent_plot_card,
    extent_opts_card
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
                                   extent_cards,
                                   target_grav_cards])
