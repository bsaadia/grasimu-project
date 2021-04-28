import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

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
                        {'label': 'Survey: Complete Gravity+, corrected', 'value': 13},
                        {'label': 'All: Target Gravity', 'value': 3},
                        {'label': 'All: Complete Gravity', 'value': 4},
                        {'label': 'All: Complete Gravity+', 'value': 5},
                        {'label': 'All: Complete Gravity+, corrected', 'value': 12},
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
