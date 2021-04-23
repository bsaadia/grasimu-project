import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table

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
